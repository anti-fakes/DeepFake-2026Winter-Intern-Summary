#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import glob
import shutil
import argparse

# (사용하시는 통합 분석 함수 임포트)
from experiment_0215 import analyze_and_plot_four_groups

def _mkdir(p: str): os.makedirs(p, exist_ok=True)

def _link_or_copy(src: str, dst: str, mode: str):
    if os.path.exists(dst): return
    if mode == "symlink": os.symlink(src, dst)
    else: shutil.copy2(src, dst)

def build_global_run_dir(result_dir: str, run_root: str, link_mode: str):
    """
    모든 데이터셋을 무시하고 TP, FN, TN, FP 4개 폴더로 모두 통합하는 함수
    """
    run_dir = os.path.join(run_root, "GLOBAL_ALL")
    _mkdir(run_dir)
    counts = {g: 0 for g in ["TP", "TN", "FP", "FN"]}
    
    for g in counts.keys():
        _mkdir(os.path.join(run_dir, g))
        
    # result_dir 안의 모든 폴더를 탐색
    for folder_name in os.listdir(result_dir):
        folder_path = os.path.join(result_dir, folder_name)
        if not os.path.isdir(folder_path): continue
        
        # 끝자리가 _TP, _FN, _TN, _FP 로 끝나는지 확인
        for g in counts.keys():
            if folder_name.endswith(f"_{g}"):
                src = os.path.join(folder_path, "images")
                if not os.path.isdir(src): continue
                
                for fp in sorted(glob.glob(os.path.join(src, "*.*"))):
                    # 파일명 충돌을 막기 위해 앞에 원본 폴더명(예: gpt_TP_)을 붙임
                    safe_filename = f"{folder_name}_{os.path.basename(fp)}"
                    dst = os.path.join(run_dir, g, safe_filename)
                    _link_or_copy(fp, dst, link_mode)
                    counts[g] += 1
                    
    return run_dir, counts

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--result_dir", type=str, required=True)
    ap.add_argument("--weights_dir", type=str, required=True)
    ap.add_argument("--model_name", type=str, default="Corvi")
    ap.add_argument("--run_root", type=str, default="./runs_global") # 통합용 폴더
    ap.add_argument("--out_root", type=str, default="./out_global")  # 통합용 결과 폴더
    ap.add_argument("--link_mode", type=str, default="symlink", choices=["symlink","copy"])
    ap.add_argument("--topk", type=int, default=40)
    args = ap.parse_args()

    _mkdir(args.run_root)
    _mkdir(args.out_root)

    # 1. 전 세계(?) 데이터 통합 모으기
    print("🌍 전 세계 데이터 영혼까지 끌어모으는 중...")
    run_dir, counts = build_global_run_dir(args.result_dir, args.run_root, args.link_mode)
    
    valid_groups = [g for g, cnt in counts.items() if cnt > 0]
    print(f"✅ 통합 완료! 그룹별 개수: {counts}")

    if len(valid_groups) == 0:
        print("[SKIP] 이미지를 찾을 수 없습니다.")
        return

    # 2. 통합본 단 한 번만 실행 (for ds in datasets 루프가 없어졌습니다!)
    for survivor_mode in ["pos", "neg"]:
        tag = f"GLOBAL_{args.model_name}_ALL_{survivor_mode}"
        out_prefix = os.path.join(args.out_root, tag)

        print(f"\n[RUN] GLOBAL INTEGRATION | groups={valid_groups} | mode={survivor_mode}")
        
        analyze_and_plot_four_groups(
            base_dir=run_dir,
            weights_dir=args.weights_dir,
            model_name=args.model_name,
            output_prefix=out_prefix,
            groups=valid_groups,  
            save_debug_csv=False,
            topk=args.topk,
            survivor_mode=survivor_mode,
        )

if __name__ == "__main__":
    import sys
    if len(sys.argv) == 1:
        sys.argv.extend([
            "--result_dir", "/home/ice06/project/HS/0215/Dataset2",
            "--weights_dir", "./weights",
            "--model_name", "Corvi",
            "--run_root", "/home/ice06/project/HS/0227/runs_global_gpt_real", 
            "--out_root", "/home/ice06/project/HS/0227/out_global_gpt_real",
            "--link_mode", "symlink",
            "--topk", "40"
        ])
    main()