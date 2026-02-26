# DeepFake-2026Winter-Intern-Summary (LEEHYESEONG)
Technical Report – 2026 Winter Research Internship

## 1. Dataset Construction

- 현실세계를 반영(촬영도구, 객체, 장르 등)
- LLM 활용 하 다양한 이미지 캡션 생성 
- 생성한 캡션 기반 예시 이미지 
- 상식적 오류 샘플(설명)

---

## 2. Detection Model Application

- 탐지 기법 분석(Semantic, Visual artifact, Frequency, Diffusion-aware, Ensemble, Rule-based)
- 상용 탐지모델 적용
- 정량적 결과 및 Hard Sample 추출 

---

## 3. Hard Sample Analysis

- 생성한 데이터셋들 중 상용 탐지 모델에서 모두 오탐한 샘플 분석  
- 직접 분석(사람의 눈으로), 주파수 기반 분석, ResNet-50기반 시각적 유사도 분석, CLIP 기반 의미적 유사도 분석

---

## 4. Corvi+ (grad)CAM Analysis

- 상용 모델들 중 가장 뛰어난 모델에 대한 추가적인 분석
- 실험: Channel-wise Attribution Analysis
- 실험: 오탐 유발 채널 확인
- 실험 결과 및 분석 

---

## 5. Conclusion and Future Work
