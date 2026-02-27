import torch
import torch.nn.functional as F
import os
import glob
import numpy as np
from tqdm import tqdm
import matplotlib.pyplot as plt
from PIL import Image
import cv2
import gc

from torchvision.transforms import Compose, Resize, CenterCrop
from utils.processing import make_normalize
from networks import create_architecture, load_weights
import yaml


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


def clear_gpu_memory():
    if torch.cuda.is_available():
        torch.cuda.empty_cache()
        gc.collect()


def compare_channels_visualization(
    base_dir,
    weights_dir,
    model_name,
    output_prefix,
    dataset_config,
    channel_sensitive,    # 오탐에 민감한 채널 (예: 1636)
    channel_robust,       # 오탐에 강한 채널 (예: 338)
    images_per_group=10,
    use_cpu=False,
):
    """
    두 채널 비교 시각화:
    - channel_sensitive: Ratio 높음 = TP↔FN 차이 큼 = 오탐에 민감
    - channel_robust: Ratio 낮음 = TP↔FN 차이 작음 = 오탐에 강함
    """
    
    # 디바이스 설정
    if use_cpu:
        device = torch.device('cpu')
        print("⚠️ Running on CPU")
    else:
        device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    print(f"Using device: {device}")
    
    clear_gpu_memory()
    
    # 모델 로드
    _, model_path, arch, norm_type, patch_size = get_config(model_name, weights_dir)
    model = load_weights(create_architecture(arch), model_path)
    model = model.to(device).eval()
    transform = build_transform(patch_size, norm_type)
    
    # Hook 설정
    cache = {}
    
    def conv_hook(module, input, output):
        cache["feature_map"] = output.detach().cpu()
    
    # Target layer 찾기
    if hasattr(model, 'layer4'):
        target_layer = model.layer4[-1]
    elif hasattr(model, 'features'):
        target_layer = model.features[-1]
    else:
        raise ValueError("Cannot find target conv layer")
    
    conv_handle = target_layer.register_forward_hook(conv_hook)
    
    # FC weights 추출
    W = model.fc.weight.detach().cpu().numpy()
    if W.ndim == 2 and W.shape[0] > 1:
        fc_weights = W[1]
    else:
        fc_weights = W.reshape(-1)
    
    weight_sensitive = fc_weights[channel_sensitive]
    weight_robust = fc_weights[channel_robust]
    
    print(f"\n📊 Channel Comparison:")
    print(f"  Sensitive Ch{channel_sensitive}: weight={weight_sensitive:.4f}")
    print(f"  Robust    Ch{channel_robust}: weight={weight_robust:.4f}")
    
    # 출력 디렉토리
    output_dir = f"{output_prefix}_channel_comparison"
    os.makedirs(output_dir, exist_ok=True)
    
    groups = list(dataset_config.keys())
    results = {g: [] for g in groups}
    
    # ========== 1. 데이터 수집 ==========
    print("\n📊 Collecting data...")
    
    for group in groups:
        folders = dataset_config[group]
        all_img_paths = []
        
        for folder in folders:
            folder_path = os.path.join(base_dir, folder)
            if os.path.exists(folder_path):
                imgs = glob.glob(os.path.join(folder_path, "*.*"))
                imgs = [p for p in imgs if p.lower().endswith(('.jpg', '.jpeg', '.png', '.bmp', '.webp'))]
                for img in imgs:
                    all_img_paths.append(img)
        
        all_img_paths = all_img_paths[:images_per_group]
        print(f"  {group}: {len(all_img_paths)} images")
        
        for img_path in tqdm(all_img_paths, desc=f"Processing {group}"):
            try:
                img_pil = Image.open(img_path).convert("RGB")
                img_tensor = transform(img_pil).unsqueeze(0).to(device)
                
                with torch.no_grad():
                    output = model(img_tensor)
                    if output.shape[-1] == 1 or output.ndim == 1 or output.shape[1] == 1:
                        score = torch.sigmoid(output).squeeze().item()
                    else:
                        score = torch.softmax(output, dim=1)[0, 1].item()
                
                feature_map = cache["feature_map"].numpy().squeeze()
                
                results[group].append({
                    "img_path": img_path,
                    "score": score,
                    "feature_map": feature_map,
                    "img_pil": img_pil
                })
                
                clear_gpu_memory()
                
            except Exception as e:
                print(f"Error: {img_path} - {e}")
                continue
    
    conv_handle.remove()
    clear_gpu_memory()
    
    # ========== 2. 시각화 함수 ==========
    
    def get_channel_cam(feature_map, channel_idx, weight, img_size):
        """특정 채널의 CAM 계산"""
        ch_map = feature_map[channel_idx]
        attr_map = ch_map * weight
        attr_map = np.maximum(attr_map, 0)  # ReLU
        if attr_map.max() > 0:
            attr_map = attr_map / attr_map.max()
        return cv2.resize(attr_map, img_size)
    
    def overlay_heatmap(img, heatmap, alpha=0.5):
        img_np = np.array(img)
        heatmap_color = cv2.applyColorMap(np.uint8(255 * heatmap), cv2.COLORMAP_JET)
        heatmap_color = cv2.cvtColor(heatmap_color, cv2.COLOR_BGR2RGB)
        overlay = (1 - alpha) * img_np + alpha * heatmap_color
        return np.clip(overlay, 0, 255).astype(np.uint8)
    
    # ========== 3. 개별 이미지 비교 시각화 ==========
    print("\n🎨 Generating comparison visualizations...")
    
    for group in groups:
        group_dir = f"{output_dir}/{group}"
        os.makedirs(group_dir, exist_ok=True)
        
        for idx, sample in enumerate(results[group]):
            img_np = np.array(sample["img_pil"])
            img_size = (img_np.shape[1], img_np.shape[0])
            
            # 두 채널의 CAM 계산
            cam_sensitive = get_channel_cam(
                sample["feature_map"], channel_sensitive, weight_sensitive, img_size
            )
            cam_robust = get_channel_cam(
                sample["feature_map"], channel_robust, weight_robust, img_size
            )
            
            # Activation 값 추출
            act_sensitive = sample["feature_map"][channel_sensitive].mean()
            act_robust = sample["feature_map"][channel_robust].mean()
            
            # 시각화
            fig, axes = plt.subplots(2, 3, figsize=(15, 10))
            
            # Row 1: Sensitive Channel (1636)
            axes[0, 0].imshow(sample["img_pil"])
            axes[0, 0].set_title(f"Original\nScore: {sample['score']:.3f}")
            axes[0, 0].axis('off')
            
            axes[0, 1].imshow(cam_sensitive, cmap='jet', vmin=0, vmax=1)
            axes[0, 1].set_title(f"Ch{channel_sensitive}\nAct: {act_sensitive:.4f}, w: {weight_sensitive:.3f}")
            axes[0, 1].axis('off')
            
            overlay_sensitive = overlay_heatmap(sample["img_pil"], cam_sensitive)
            axes[0, 2].imshow(overlay_sensitive)
            axes[0, 2].set_title(f"Ch{channel_sensitive} Overlay")
            axes[0, 2].axis('off')
            
            # Row 2: Robust Channel (338)
            axes[1, 0].imshow(sample["img_pil"])
            axes[1, 0].set_title(f"Original\nScore: {sample['score']:.3f}")
            axes[1, 0].axis('off')
            
            axes[1, 1].imshow(cam_robust, cmap='jet', vmin=0, vmax=1)
            axes[1, 1].set_title(f"Ch{channel_robust}\nAct: {act_robust:.4f}, w: {weight_robust:.3f}")
            axes[1, 1].axis('off')
            
            overlay_robust = overlay_heatmap(sample["img_pil"], cam_robust)
            axes[1, 2].imshow(overlay_robust)
            axes[1, 2].set_title(f"Ch{channel_robust} Overlay")
            axes[1, 2].axis('off')
            
            plt.suptitle(f"{group} Sample {idx+1}: Ch{channel_sensitive}  vs Ch{channel_robust} ", 
                        fontsize=14)
            plt.tight_layout()
            plt.savefig(f"{group_dir}/{group}_sample{idx+1:03d}_comparison.png", dpi=150, bbox_inches='tight')
            plt.close()
    
    # ========== 4. TP vs FN 직접 비교 (핵심!) ==========
    if "TP" in results and "FN" in results and len(results["TP"]) > 0 and len(results["FN"]) > 0:
        print("\n📊 Creating TP vs FN direct comparison...")
        
        compare_dir = f"{output_dir}/TP_vs_FN_direct"
        os.makedirs(compare_dir, exist_ok=True)
        
        n_compare = min(len(results["TP"]), len(results["FN"]), 10)
        
        for i in range(n_compare):
            tp_sample = results["TP"][i]
            fn_sample = results["FN"][i]
            
            fig, axes = plt.subplots(2, 4, figsize=(20, 10))
            
            # TP 이미지
            tp_img_np = np.array(tp_sample["img_pil"])
            tp_size = (tp_img_np.shape[1], tp_img_np.shape[0])
            
            tp_cam_sensitive = get_channel_cam(tp_sample["feature_map"], channel_sensitive, weight_sensitive, tp_size)
            tp_cam_robust = get_channel_cam(tp_sample["feature_map"], channel_robust, weight_robust, tp_size)
            
            tp_act_sensitive = tp_sample["feature_map"][channel_sensitive].mean()
            tp_act_robust = tp_sample["feature_map"][channel_robust].mean()
            
            # FN 이미지
            fn_img_np = np.array(fn_sample["img_pil"])
            fn_size = (fn_img_np.shape[1], fn_img_np.shape[0])
            
            fn_cam_sensitive = get_channel_cam(fn_sample["feature_map"], channel_sensitive, weight_sensitive, fn_size)
            fn_cam_robust = get_channel_cam(fn_sample["feature_map"], channel_robust, weight_robust, fn_size)
            
            fn_act_sensitive = fn_sample["feature_map"][channel_sensitive].mean()
            fn_act_robust = fn_sample["feature_map"][channel_robust].mean()
            
            # Row 0: TP
            axes[0, 0].imshow(tp_sample["img_pil"])
            axes[0, 0].set_title(f"TP Original\nScore: {tp_sample['score']:.3f}")
            axes[0, 0].axis('off')
            
            axes[0, 1].imshow(overlay_heatmap(tp_sample["img_pil"], tp_cam_sensitive))
            axes[0, 1].set_title(f"TP - Ch{channel_sensitive} \nAct: {tp_act_sensitive:.4f}")
            axes[0, 1].axis('off')
            
            axes[0, 2].imshow(overlay_heatmap(tp_sample["img_pil"], tp_cam_robust))
            axes[0, 2].set_title(f"TP - Ch{channel_robust} \nAct: {tp_act_robust:.4f}")
            axes[0, 2].axis('off')
            
            # TP 비교 바 차트
            axes[0, 3].bar(['Ch1636\n', 'Ch338\n'], [tp_act_sensitive, tp_act_robust], 
                          color=['red', 'blue'])
            axes[0, 3].set_ylabel('Activation')
            axes[0, 3].set_title('TP Activation')
            axes[0, 3].set_ylim(0, max(tp_act_sensitive, tp_act_robust, fn_act_sensitive, fn_act_robust) * 1.2)
            
            # Row 1: FN
            axes[1, 0].imshow(fn_sample["img_pil"])
            axes[1, 0].set_title(f"FN Original\nScore: {fn_sample['score']:.3f}")
            axes[1, 0].axis('off')
            
            axes[1, 1].imshow(overlay_heatmap(fn_sample["img_pil"], fn_cam_sensitive))
            axes[1, 1].set_title(f"FN - Ch{channel_sensitive} \nAct: {fn_act_sensitive:.4f}")
            axes[1, 1].axis('off')
            
            axes[1, 2].imshow(overlay_heatmap(fn_sample["img_pil"], fn_cam_robust))
            axes[1, 2].set_title(f"FN - Ch{channel_robust} \nAct: {fn_act_robust:.4f}")
            axes[1, 2].axis('off')
            
            # FN 비교 바 차트
            axes[1, 3].bar(['Ch1636\n', 'Ch338\n'], [fn_act_sensitive, fn_act_robust],
                          color=['red', 'blue'])
            axes[1, 3].set_ylabel('Activation')
            axes[1, 3].set_title('FN Activation')
            axes[1, 3].set_ylim(0, max(tp_act_sensitive, tp_act_robust, fn_act_sensitive, fn_act_robust) * 1.2)
            
            plt.suptitle(f"TP vs FN Comparison {i+1}: Ch{channel_sensitive}  vs Ch{channel_robust} ", 
                        fontsize=14)
            plt.tight_layout()
            plt.savefig(f"{compare_dir}/comparison_{i+1:03d}.png", dpi=150, bbox_inches='tight')
            plt.close()
    
    # ========== 5. 통계 요약 ==========
    print("\n📈 Activation Statistics Summary:")
    print("="*70)
    print(f"{'Group':<10} {'Ch'+ str(channel_sensitive) + ' ':<20} {'Ch' + str(channel_robust) + ' ':<20}")
    print("="*70)
    
    for group in groups:
        if len(results[group]) > 0:
            acts_sensitive = [r["feature_map"][channel_sensitive].mean() for r in results[group]]
            acts_robust = [r["feature_map"][channel_robust].mean() for r in results[group]]
            
            print(f"{group:<10} {np.mean(acts_sensitive):.4f} ± {np.std(acts_sensitive):.4f}        "
                  f"{np.mean(acts_robust):.4f} ± {np.std(acts_robust):.4f}")
    
    if "TP" in results and "FN" in results:
        tp_sens = np.mean([r["feature_map"][channel_sensitive].mean() for r in results["TP"]])
        fn_sens = np.mean([r["feature_map"][channel_sensitive].mean() for r in results["FN"]])
        tp_rob = np.mean([r["feature_map"][channel_robust].mean() for r in results["TP"]])
        fn_rob = np.mean([r["feature_map"][channel_robust].mean() for r in results["FN"]])
        
        print("="*70)
        print(f"{'Ratio (TP/FN)':<10} {tp_sens/fn_sens:.2f}x                   {tp_rob/fn_rob:.2f}x")
    
    print(f"\n✅ All outputs saved to: {output_dir}/")
    
    return results


# ========== 실행 ==========
if __name__ == "__main__":
    
    # ✅ 데이터셋 설정 (GPT 또는 Z-image 선택)
    dataset_config = {
        "TP": [
            "zimage_TP/images",    # Z-image 사용시
            # "gpt_TP/images",     # GPT 사용시
        ],
        "FN": [
            "zimage_FN/images",    # Z-image 사용시
            # "gpt_FN/images",     # GPT 사용시
        ],
    }
    
    results = compare_channels_visualization(
        base_dir="/home/ice06/project/HS/0215/Dataset",    # 경로 확인
        weights_dir="./weights",
        model_name="Corvi",                # 모델명 확인
        output_prefix="/home/ice06/project/HS/0215/0218_channel_comp_zimage",
        dataset_config=dataset_config,
        channel_sensitive=1636,   # 오탐에 민감한 채널 (Ratio 높음)
        channel_robust=338,       # 오탐에 강한 채널 (Ratio 낮음)
        images_per_group=40,
        use_cpu=False,
    )
    #0227