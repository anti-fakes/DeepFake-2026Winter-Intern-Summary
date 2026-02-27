import numpy as np
import cv2  # OpenCV 추가
from PIL import Image


# ==========================================
# Blur, Noise 적용 함수
# ==========================================
def apply_distortion(img_pil, distortion_type, severity):
    """
    메모리 상에서 이미지에 Blur 또는 Noise를 적용합니다.
    img_pil: PIL Image
    distortion_type: 'blur' or 'noise'
    severity: float (sigma 값)
    """
    if distortion_type is None or distortion_type.lower() == 'none':
        return img_pil

    # PIL -> Numpy 변환
    img_np = np.array(img_pil)

    try:
        if distortion_type == 'blur':
            # Gaussian Blur (kernel size는 (0,0)으로 두면 sigma에 맞춰 자동 계산됨)
            # severity가 곧 Sigma X, Sigma Y
            if severity > 0:
                img_np = cv2.GaussianBlur(img_np, (0, 0), sigmaX=severity, sigmaY=severity)

        elif distortion_type == 'noise':
            # Gaussian Noise
            if severity > 0:
                row, col, ch = img_np.shape
                mean = 0
                # severity가 곧 Noise Sigma
                gauss = np.random.normal(mean, severity, (row, col, ch))
                noisy = img_np + gauss
                # 0~255로 자르고 uint8로 변환
                img_np = np.clip(noisy, 0, 255).astype(np.uint8)

    except Exception as e:
        print(f"⚠️ Distortion Error ({distortion_type}, {severity}): {e}")
        return img_pil  # 에러 시 원본 반환

    # Numpy -> PIL 변환 후 반환
    return Image.fromarray(img_np)


"""
grayscale 적용 시 하단 코드 추가
# img_pil = img_pil.convert('L').convert('RGB')
"""