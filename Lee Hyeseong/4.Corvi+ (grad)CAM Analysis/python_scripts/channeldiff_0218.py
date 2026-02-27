import pandas as pd
import numpy as np

def analyze_tp_fn_ratio(csv_path, output_prefix, topk=20):
    """
    TP-FN 차이와 TP/FN 비율 분석
    
    출력:
    1. Diff (TP-FN) 기준 정렬 표
    2. Ratio (TP/FN) 기준 정렬 표
    3. 두 지표 비교 표
    """
    
    # CSV 로드
    df = pd.read_csv(csv_path)
    
    # 필요한 컬럼 확인
    if 'TP_Act_Mean' not in df.columns or 'FN_Act_Mean' not in df.columns:
        print("❌ TP_Act_Mean 또는 FN_Act_Mean 컬럼이 없습니다.")
        return None
    
    # ========== Activation 기준 분석 ==========
    print("=" * 80)
    print("📊 Activation 기준 분석 (TP vs FN)")
    print("=" * 80)
    
    # Diff와 Ratio 계산
    df['Diff_Act'] = df['TP_Act_Mean'] - df['FN_Act_Mean']
    df['Ratio_Act'] = df['TP_Act_Mean'] / (df['FN_Act_Mean'] + 1e-8)  # 0 나눗셈 방지
    
    # Diff 기준 Top-K
    df_diff_sorted = df.sort_values('Diff_Act', ascending=False).head(topk)
    
    print(f"\n🔹 TP-FN 차이(Diff) 상위 {topk}개 채널:")
    print("-" * 70)
    print(f"{'Rank':<6} {'Channel':<10} {'TP':<12} {'FN':<12} {'Diff':<12} {'Ratio':<10}")
    print("-" * 70)
    
    for rank, (_, row) in enumerate(df_diff_sorted.iterrows(), 1):
        ch = int(row['Channel_ID'])
        tp = row['TP_Act_Mean']
        fn = row['FN_Act_Mean']
        diff = row['Diff_Act']
        ratio = row['Ratio_Act']
        print(f"{rank:<6} Ch{ch:<7} {tp:<12.4f} {fn:<12.4f} {diff:<12.4f} {ratio:<10.1f}x")
    
    # Ratio 기준 Top-K
    df_ratio_sorted = df.sort_values('Ratio_Act', ascending=False).head(topk)
    
    print(f"\n🔹 TP/FN 비율(Ratio) 상위 {topk}개 채널:")
    print("-" * 70)
    print(f"{'Rank':<6} {'Channel':<10} {'TP':<12} {'FN':<12} {'Diff':<12} {'Ratio':<10}")
    print("-" * 70)
    
    for rank, (_, row) in enumerate(df_ratio_sorted.iterrows(), 1):
        ch = int(row['Channel_ID'])
        tp = row['TP_Act_Mean']
        fn = row['FN_Act_Mean']
        diff = row['Diff_Act']
        ratio = row['Ratio_Act']
        print(f"{rank:<6} Ch{ch:<7} {tp:<12.4f} {fn:<12.4f} {diff:<12.4f} {ratio:<10.1f}x")
    
    # ========== Attribution 기준 분석 ==========
    if 'TP_Attr_Mean' in df.columns and 'FN_Attr_Mean' in df.columns:
        print("\n" + "=" * 80)
        print("📊 Attribution 기준 분석 (TP vs FN)")
        print("=" * 80)
        
        df['Diff_Attr'] = df['TP_Attr_Mean'] - df['FN_Attr_Mean']
        df['Ratio_Attr'] = df['TP_Attr_Mean'] / (df['FN_Attr_Mean'] + 1e-8)
        
        # Diff 기준
        df_diff_attr = df.sort_values('Diff_Attr', ascending=False).head(topk)
        
        print(f"\n🔹 Attribution TP-FN 차이(Diff) 상위 {topk}개 채널:")
        print("-" * 80)
        print(f"{'Rank':<6} {'Channel':<10} {'Weight':<10} {'TP_Attr':<12} {'FN_Attr':<12} {'Diff':<12} {'Ratio':<10}")
        print("-" * 80)
        
        for rank, (_, row) in enumerate(df_diff_attr.iterrows(), 1):
            ch = int(row['Channel_ID'])
            w = row['Weight']
            tp = row['TP_Attr_Mean']
            fn = row['FN_Attr_Mean']
            diff = row['Diff_Attr']
            ratio = row['Ratio_Attr']
            print(f"{rank:<6} Ch{ch:<7} {w:<10.4f} {tp:<12.4f} {fn:<12.4f} {diff:<12.4f} {ratio:<10.1f}x")
        
        # Ratio 기준
        df_ratio_attr = df.sort_values('Ratio_Attr', ascending=False).head(topk)
        
        print(f"\n🔹 Attribution TP/FN 비율(Ratio) 상위 {topk}개 채널:")
        print("-" * 80)
        print(f"{'Rank':<6} {'Channel':<10} {'Weight':<10} {'TP_Attr':<12} {'FN_Attr':<12} {'Diff':<12} {'Ratio':<10}")
        print("-" * 80)
        
        for rank, (_, row) in enumerate(df_ratio_attr.iterrows(), 1):
            ch = int(row['Channel_ID'])
            w = row['Weight']
            tp = row['TP_Attr_Mean']
            fn = row['FN_Attr_Mean']
            diff = row['Diff_Attr']
            ratio = row['Ratio_Attr']
            print(f"{rank:<6} Ch{ch:<7} {w:<10.4f} {tp:<12.4f} {fn:<12.4f} {diff:<12.4f} {ratio:<10.1f}x")
    
    # ========== CSV 저장 ==========
    # 전체 결과 저장
    output_cols = ['Channel_ID', 'Weight', 
                   'TP_Act_Mean', 'FN_Act_Mean', 'Diff_Act', 'Ratio_Act']
    
    if 'Diff_Attr' in df.columns:
        output_cols += ['TP_Attr_Mean', 'FN_Attr_Mean', 'Diff_Attr', 'Ratio_Attr']
    
    df_output = df[output_cols].sort_values('Diff_Act', ascending=False)
    df_output.to_csv(f"{output_prefix}_tp_fn_analysis.csv", index=False)
    
    # Ratio 기준 정렬도 저장
    df_ratio_output = df[output_cols].sort_values('Ratio_Act', ascending=False)
    df_ratio_output.to_csv(f"{output_prefix}_tp_fn_ratio_sorted.csv", index=False)
    
    print(f"\n✅ 결과 저장 완료:")
    print(f"   - {output_prefix}_tp_fn_analysis.csv (Diff 기준 정렬)")
    print(f"   - {output_prefix}_tp_fn_ratio_sorted.csv (Ratio 기준 정렬)")
    
    # ========== 순위 비교 분석 ==========
    print("\n" + "=" * 80)
    print("📊 Diff vs Ratio 순위 비교 (상위 10개)")
    print("=" * 80)
    
    df_diff_top10 = df.nlargest(10, 'Diff_Act')['Channel_ID'].values
    df_ratio_top10 = df.nlargest(10, 'Ratio_Act')['Channel_ID'].values
    
    print(f"\n{'Rank':<6} {'Diff 기준':<15} {'Ratio 기준':<15}")
    print("-" * 40)
    for i in range(10):
        print(f"{i+1:<6} Ch{int(df_diff_top10[i]):<12} Ch{int(df_ratio_top10[i]):<12}")
    
    # 공통 채널
    common = set(df_diff_top10) & set(df_ratio_top10)
    print(f"\n🔸 공통 채널 (Top 10): {[f'Ch{int(c)}' for c in common]}")
    print(f"🔸 Diff에만 있는 채널: {[f'Ch{int(c)}' for c in set(df_diff_top10) - common]}")
    print(f"🔸 Ratio에만 있는 채널: {[f'Ch{int(c)}' for c in set(df_ratio_top10) - common]}")
    
    return df


# ========== 실행 ==========
if __name__ == "__main__":
    
    # ✅ CSV 파일 경로 수정
    csv_path = "/home/ice06/project/HS/0215/out_global_zimage_real/GLOBAL_Corvi_ALL_pos_analysis_stats_with_scores.csv"
    output_prefix = "/home/ice06/project/HS/0215/0218_channeldiff_zimage_result"
    
    df = analyze_tp_fn_ratio(csv_path, output_prefix, topk=15)

    #써야하는 코드 0227