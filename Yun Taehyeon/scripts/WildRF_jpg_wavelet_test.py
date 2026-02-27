import os
import cv2
import numpy as np
import matplotlib.pyplot as plt
import pywt  # PyWavelets 라이브러리
from glob import glob
from tqdm import tqdm

# ==========================================
# 1. 실험 설정 (Configuration)
# ==========================================
# WildRF 데이터셋 경로
dataset_paths = {
    "WildRF_Real": r"/path/to/dir",  # 실제 경로 입력
    "WildRF_Fake": r"/path/to/dir"   # 실제 경로 입력
}

# 압축 파라미터 (Stress Level)
JPEG_QUALITY = 70 
IMG_SIZE = 512

# ==========================================
# 2. 핵심 함수: 압축 잔차 & 웨이블릿 에너지 계산
# ==========================================
def jpeg_compress(img, quality):
    """ 이미지를 메모리 상에서 JPEG로 압축했다가 다시 풂 """
    encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), quality]
    _, encimg = cv2.imencode('.jpg', img, encode_param)
    decimg = cv2.imdecode(encimg, 0) # Grayscale 로드
    return decimg

def get_wavelet_residual_energy(img):
    """
    1. 압축 수행
    2. 잔차(Residual) 계산
    3. Wavelet 변환 후 고주파 에너지(Log Scale) 반환
    """
    # A. Active Re-compression
    compressed = jpeg_compress(img, JPEG_QUALITY)
    
    # B. Residual Calculation (절대값 차이)
    # float32로 변환하여 오버플로우/언더플로우 방지
    residual = np.abs(img.astype(np.float32) - compressed.astype(np.float32))
    
    # C. Wavelet Transform (Haar Wavelet 사용)
    # 'db1' (Haar)은 급격한 변화(엣지, 노이즈) 탐지에 유리함
    coeffs = pywt.dwt2(residual, 'db1')
    LL, (LH, HL, HH) = coeffs
    
    # D. Energy Calculation (Detail Coefficients only)
    # LH: 수평 고주파, HL: 수직 고주파, HH: 대각선 고주파
    # 이 세 성분의 에너지를 합침 (Mean Square)
    detail_energy = np.mean(LH**2 + HL**2 + HH**2)
    
    # 로그 스케일로 변환 (시각화를 위해)
    return np.log(detail_energy + 1e-10)

def process_dataset(folder_path):
    extensions = ['*.jpg', '*.jpeg', '*.png', '*.webp']
    files = []
    for ext in extensions:
        files.extend(glob(os.path.join(folder_path, ext)))
        files.extend(glob(os.path.join(folder_path, ext.upper())))
    
    if not files:
        print(f"Warning: No images found in {folder_path}")
        return []

    energies = []
    print(f"Processing {folder_path} (Quality={JPEG_QUALITY})...")
    
    for f in tqdm(files):
        try:
            img = cv2.imread(f, 0) # Grayscale
            if img is None: continue
            
            # Center Crop (얼굴/중심부 집중을 위해 Resizing 대신 Crop 추천)
            h, w = img.shape
            min_dim = min(h, w, IMG_SIZE)
            # 중앙 크롭
            cy, cx = h // 2, w // 2
            img = img[cy - min_dim//2 : cy + min_dim//2, cx - min_dim//2 : cx + min_dim//2]
            
            # 크기가 너무 작으면 리사이즈, 크면 그대로 사용
            if img.shape[0] != IMG_SIZE:
                img = cv2.resize(img, (IMG_SIZE, IMG_SIZE))

            energy = get_wavelet_residual_energy(img)
            energies.append(energy)
        except Exception as e:
            print(f"Error: {e}")
            continue
            
    return energies

# ==========================================
# 3. 데이터 처리 및 시각화
# ==========================================
results = {}

for name, path in dataset_paths.items():
    results[name] = process_dataset(path)

# 히스토그램 그리기
import matplotlib
matplotlib.use('Agg') 

plt.figure(figsize=(10, 6))

colors = ['blue', 'red'] # Real: Blue, Fake: Red
for i, (name, energy_list) in enumerate(results.items()):
    if energy_list:
        plt.hist(energy_list, bins=70, alpha=0.6, label=name, 
                 color=colors[i % 2], density=True, histtype='stepfilled')

plt.title(f"Wavelet Residual Energy Distribution (JPEG QF={JPEG_QUALITY})", fontsize=14, fontweight='bold')
plt.xlabel("Log Energy of High-Freq Residuals")
plt.ylabel("Density")
plt.legend(loc='upper right')
plt.grid(True, alpha=0.3)

save_path = f"wavelet_residual_q{JPEG_QUALITY}.png"
plt.savefig(save_path, dpi=300)
print(f"\n[Success] 결과 그래프가 '{save_path}'로 저장되었습니다.")
