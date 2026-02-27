import io
from PIL import Image
# ==========================================
# Instagram 모사
# ==========================================
def apply_distortion(img_pil, distortion_type, severity, filename=None):
    """
    메모리 상에서 이미지에 압축 및 변형을 적용합니다.
    img_pil: 변환할 image (img_pil = Image.open(filename).convert('RGB'))
    distortion_type: 압축 환경 설정
    severity: 품질(Quality Factor) 또는 Sigma 값
    filename: image 주
    """
    if distortion_type is None or distortion_type.lower() == 'none':
        return img_pil

    try:
        # 1. 모바일 환경 모사 (Pillow: Lanczos 리사이징 + WebP 압축)
        if distortion_type == 'webp_mobile':
            # 1080x1080 리사이징
            img_resized = img_pil.resize((1080, 1080), Image.Resampling.LANCZOS)
            
            # 메모리 버퍼 생성 및 WebP 압축 저장
            buffer = io.BytesIO()
            img_resized.save(buffer, format="WEBP", quality=int(severity))
            buffer.seek(0)
            
            # 압축된 버퍼를 다시 PIL 이미지로 로드
            return Image.open(buffer).convert('RGB')

        # 2. PC 환경 모사 (Pillow: Bicubic 리사이징 + JPEG 압축)
        elif distortion_type == 'jpeg_pc':
            # PC 환경의 보편적인 Bicubic 보간법으로 1080x1080 리사이징
            img_resized = img_pil.resize((1080, 1080), Image.Resampling.BICUBIC)
            
            # 메모리 버퍼 상에서 JPEG 압축 수행 (subsampling=0 은 화질 손실을 최소화하는 고품질 JPEG 설정)
            buffer = io.BytesIO()
            img_resized.save(buffer, format="JPEG", quality=int(severity), subsampling=0)
            buffer.seek(0)
            
            # 압축된 버퍼를 다시 PIL 이미지로 로드
            return Image.open(buffer).convert('RGB')

    except Exception as e:
        print(f"\n⚠️ Distortion Error ({distortion_type}, {severity}): {e}")
        return img_pil  # 에러 시 원본 반환