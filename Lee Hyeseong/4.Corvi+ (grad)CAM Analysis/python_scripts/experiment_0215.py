import torch
import os
import glob
import pandas as pd
import numpy as np
from tqdm import tqdm
import matplotlib.pyplot as plt
from PIL import Image

from torchvision.transforms import Compose, Resize, CenterCrop
from utils.processing import make_normalize
from networks import create_architecture, load_weights
import yaml

# ... (1. get_config, 2. build_transform 함수는 기존과 완전히 동일하게 유지) ...

def get_config(model_name, weights_dir='./weights'):
    with open(os.path.join(weights_dir, model_name, 'config.yaml')) as fid:
        data = yaml.load(fid, Loader=yaml.FullLoader)
    model_path = os.path.join(weights_dir, model_name, data['weights_file'])
    return data['model_name'], model_path, data['arch'], data['norm_type'], data['patch_size']

def build_transform(patch_size, norm_type):
    tfms = []
    if patch_size == 'Clip224':
        tfms.extend([Resize(224), CenterCrop((224, 224))])
    elif isinstance(patch_size, (tuple, list)):
        tfms.extend([Resize(*patch_size), CenterCrop(patch_size[0])])
    elif patch_size is not None and patch_size > 0:
        tfms.append(CenterCrop(patch_size))
    tfms.append(make_normalize(norm_type))
    return Compose(tfms)


def analyze_and_plot_four_groups(
    base_dir,
    weights_dir,
    model_name,
    output_prefix,
    groups=("TP", "FN", "TN", "FP"),  # ✅ 기본값을 4개 모두 처리하도록 변경
    debug_per_group=1,
    save_debug_csv=True,
    topk=40,
    survivor_mode="pos"
):
    # (0. 모델 로드 ~ 1. 가중치 추출 로직은 기존과 동일하므로 생략 없이 사용)
    _, model_path, arch, norm_type, patch_size = get_config(model_name, weights_dir)
    model = load_weights(create_architecture(arch), model_path)
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    model = model.to(device).eval()
    transform = build_transform(patch_size, norm_type)

    fc_cache = {}
    def fc_hook(module, input, output):
        fc_cache["z"] = input[0].detach()
        fc_cache["y"] = output.detach()
    hook_handle = model.fc.register_forward_hook(fc_hook)

    print("1. Extracting Linear Weights...")
    W = model.fc.weight.detach().cpu().numpy()
    b = model.fc.bias.detach().cpu().numpy() if model.fc.bias is not None else None

    if W.ndim == 2 and W.shape[0] > 1:
        target_weights = W[1]
    else:
        target_weights = W.reshape(-1)

    if survivor_mode == "pos":
        mask = target_weights > 0
    elif survivor_mode == "neg":
        mask = target_weights < 0
    else:
        raise ValueError("survivor_mode must be 'pos' or 'neg'")

    survivor_indices = np.where(mask)[0]
    survivor_weights = target_weights[survivor_indices]

    sorted_idx = np.argsort(survivor_weights)[::-1]
    survivor_indices = survivor_indices[sorted_idx]
    survivor_weights = survivor_weights[sorted_idx]

    num_survivors = len(survivor_indices)
    print(f"Found {num_survivors} survivor channels.")

    # 2. 그룹별 데이터 추출
    stats_results = {"Channel_ID": survivor_indices, "Weight": survivor_weights}
    raw_data = {g: {"act": [], "attr": []} for g in groups}
    debug_rows, err_rows = [], []

    for group in groups:
        folder_path = os.path.join(base_dir, group)
        img_paths = sorted(glob.glob(os.path.join(folder_path, "*.*")))
        print(f"\nProcessing Group: {group} (Found {len(img_paths)} images)")
        
        if len(img_paths) == 0:
            print(f"Warning: No images for {group}. Skipping...")
            continue

        debug_printed = 0
        with torch.no_grad():
            for img_path in tqdm(img_paths):
                try:
                    img = Image.open(img_path).convert("RGB")
                    x = transform(img)
                    if not torch.is_tensor(x): raise TypeError("Not a tensor")
                    img_tensor = x.unsqueeze(0).to(device)

                    out_logits = model(img_tensor)

                    feat_vec = fc_cache["z"].detach().cpu().numpy().squeeze()
                    fc_out = fc_cache["y"].detach().cpu().numpy().squeeze()
                    model_out = out_logits.detach().cpu().numpy().squeeze()

                    act_vals = feat_vec[survivor_indices]
                    attr_vals = act_vals * survivor_weights

                    raw_data[group]["act"].append(act_vals)
                    raw_data[group]["attr"].append(attr_vals)

                except Exception as e:
                    err_rows.append({"group": group, "img_path": img_path, "error": repr(e)})
                    continue

        if len(raw_data[group]["act"]) > 0:
            act_array = np.array(raw_data[group]["act"])
            attr_array = np.array(raw_data[group]["attr"])
            stats_results[f"{group}_Act_Mean"] = np.mean(act_array, axis=0)
            stats_results[f"{group}_Act_Std"] = np.std(act_array, axis=0)
            stats_results[f"{group}_Attr_Mean"] = np.mean(attr_array, axis=0)
            stats_results[f"{group}_Attr_Std"] = np.std(attr_array, axis=0)

    hook_handle.remove()

    # 4. 종합 Stats CSV 저장
    df_stats = pd.DataFrame(stats_results)
    csv_path = f"{output_prefix}_analysis_stats.csv"
    df_stats.to_csv(csv_path, index=False)
    print(f"\n✅ All Groups Stats saved: {csv_path}")

    # 5. 분리도 계산 (TP-FN, FP-TN 모두 한 번에 계산)
    df_score = df_stats.copy()
    has_fake = "TP_Attr_Mean" in df_stats.columns and "FN_Attr_Mean" in df_stats.columns
    has_real = "FP_Attr_Mean" in df_stats.columns and "TN_Attr_Mean" in df_stats.columns

    if has_fake:
        df_score["Score_Fake(TP-FN)"] = df_score["TP_Attr_Mean"] - df_score["FN_Attr_Mean"]
        top_fake = df_score.sort_values("Score_Fake(TP-FN)", ascending=False).head(topk)
        top_fake.to_csv(f"{output_prefix}_top{topk}_Fake(TP-FN).csv", index=False)
        
    if has_real:
        df_score["Score_Real(FP-TN)"] = df_score["FP_Attr_Mean"] - df_score["TN_Attr_Mean"]
        top_real = df_score.sort_values("Score_Real(FP-TN)", ascending=False).head(topk)
        top_real.to_csv(f"{output_prefix}_top{topk}_Real(FP-TN).csv", index=False)

    # 전체 데이터 합산 저장
    df_score.to_csv(f"{output_prefix}_analysis_stats_with_scores.csv", index=False)

    # 6. 플롯: 4개가 나란히 그려지도록 자동화
    def plot_metric(metric_prefix: str, ylabel: str, title: str, out_png: str):
        present_groups = [g for g in groups if f"{g}_{metric_prefix}_Mean" in df_stats.columns]
        if len(present_groups) == 0: return

        x = np.arange(num_survivors)
        fig, ax = plt.subplots(figsize=(18, 6)) # 가로 크기 조금 더 늘림

        width = 0.8 / len(present_groups)
        offsets = np.linspace(-0.4 + width/2, 0.4 - width/2, len(present_groups))

        for off, g in zip(offsets, present_groups):
            ax.bar(
                x + off, df_stats[f"{g}_{metric_prefix}_Mean"], width,
                yerr=df_stats[f"{g}_{metric_prefix}_Std"], label=g, capsize=3
            )

        ax.set_ylabel(ylabel)
        ax.set_title(title)
        ax.set_xticks(x)
        ax.set_xticklabels([f"Ch{idx}" for idx in survivor_indices], rotation=90)
        ax.legend()
        plt.tight_layout()
        plt.savefig(out_png)
        plt.close()

    plot_metric("Act", "Activation (Actual FC Input)", "Activation Distribution (TP vs FN vs TN vs FP)", f"{output_prefix}_Activation_plot.png")
    plot_metric("Attr", "Attribution (Weight * Activation)", "Attribution Distribution", f"{output_prefix}_Attribution_plot.png")

    #올릴파일 0227