# DeepFake-2026Winter-Intern-Summary (LEEHYESEONG)
Technical Report – 2026 Winter Research Internship
아래의 각 항목별 내용을 각 폴더의 README에서 확인 가능 

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

## 5. Conclusion 
### 이미지 캡션 생성 프롬프트 구조화 
* 이미지 생성을 크게 4개의 부분으로 분리 및 구조화.
* LLM을 홯용한 캡션 생성으로 같은 장르, 촬영도구 내에서도 다양한 이미지 생성하기 위해 노력.
* 생성과정에서 나온 상식적오류 샘플들 확인 

### Hard Sample 분석
* CLIP, Freqeuncy기반 Hard Sample 분석(공통점 탐색).
* 가장 높은 성능을 보인 Corvi+에 대해 해당 모델을 기반으로 한 Hard Sample t-SNE 시각화 진행.
  * 2차원 시각화에 따른 정탐, 오탐이 시각화에서 분리가 되지 않는 샘플들도 존재하는 한계점도 확인함.
* 여러 기법을 통해 확인해도 뚜렷한 공통점이 존재하지 않는 경향을 보임.

### Corvi+ 추가 분석
* 사용한 탐지모델 중 가장 높은 성능을 보인 Corvi+에 대한 추가 분석.
  * Stay-Positive의 목적에 맞춰 학습된 양수 가중치는 몇개인지
  * 사용된 채널들 중 탐지에 영향을 많이(적게)주는 채널들은 어떤 것이 존재하는지
  * 
---

## 6. Future Work

### 편향된 채널 개선 및 모델 경량화
* 전체 2048개의 채널 중 실제 결정에 사용되는 채널은 소수에 불과함을 확인.
  * 사용 빈도가 낮거나 기여도가 미미한 채널을 대상으로 **Channel Pruning**을 통한 성능 변화를 확인하는 실험이 추가로 가능.

### 시각화(CAM)를 통한 상위 채널의 정성적 분석
* 상위 채널이 공통적으로 바라보는 패턴(경계, 질감, 주파수 artifact 등)을 확인.
  * 오탐에 민감한 채널과 오탐에 강한 채널이 공통적으로 집중하는 패턴을 확인.
* `TP > FP > FN > TN` 경향을 보이는 채널들의 시각적 집중 영역을 심층 분석.
* 모델이 단순히 "특정 패턴 탐지"에 과도하게 의존하고 있는지 검증.

### Hard Sample 기반의 재학습 (Fine-Tuning)
* `Wild_data` 데이터셋에 대한 추가적인 실험을 진행하고 결과를 분석(같은 경향성을 보이는지 확인).
* GPT, Z-Image에서 발생한 FN(미탐) 이미지들을 기반으로 모델을 재학습하여 성능 개선을 도모.
* Hard Sample 재학습 전/후의 채널 Attribution 구조 변화를 비교 분석하여 재학습의 효과를 검증.
