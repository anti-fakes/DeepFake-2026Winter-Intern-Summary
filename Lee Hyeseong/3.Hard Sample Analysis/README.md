# Hard Sample 분석

## 배경 및 목적
사용한 모든 탐지 모델에서 회피한 데이터셋들의 공통점 존재 여부 확인 (정성적 분석)

### Hard Sample 구성 (총 974장)
- 사용한 모든 탐지모델을 통과한 이미지들로 총 974장 존재
- Z-image: 40장 / GPT: 42장 / Wild_data(Ours): 892장

---

## 분석 방법
1. **직접 분석** → 사람의 눈으로 판단되는 공통적인 부분이 존재하는가?
2. **주파수 기반 분석** → Hard Sample에서 공통적으로 드러나는 주파수 or 픽셀 흔적이 존재하는가?
3. **ResNet-50 기반 시각적 유사도 분석** → 공통적인 질감, 구조, 형태가 존재하는가?
4. **CLIP 기반 의미적 유사도 분석** → 공통적인 이미지의 주제나 의미가 존재하는가?

---

<br>

# 분석 결과
<br>

## 1. 주파수 기반 분석
### TN, FP, TP, FN 각 영역 이미지들의 2D FFT 평균 스펙트럼 분석 결과
<img width="3980" height="937" alt="image" src="https://github.com/user-attachments/assets/c4fcb51b-2a6f-471e-b400-e675213e0b08" />

### 공통점
   -  4개 그룹 모두 중심부(저주파)에 에너지가 집중되어 있고, 가로/세로 십자 패턴(수평·수직 성분)이 나타나는 전형적인 자연 이미지 스펙트럼 형태를 보이며 구조가 모두 유사함.

### 차이점
- TN (N=4938) - 실제 이미지 정탐
   - 중심 에너지가 가장 넓게 퍼져 있고 십자 패턴이 뚜렷함.
   - 자연 이미지의 전형적인 스펙트럼 분포를 보임.

- FP (N=23) - 실제 이미지 오탐
   - 샘플 수가 23장으로 매우 적어서 신뢰도가 낮음.
   - TN과 유사한 패턴이지만 중심 에너지가 약간 더 집중된 느낌을 받음.

- TP (N=11977) - AI 이미지 정탐
   - 중심부가 가장 어둡고(에너지가 낮음) 전체적으로 균일한 분포.
   - 고주파 성분이 TN 대비 상대적으로 억제된 느낌을 받음.

- FN (N=974) - AI 이미지 오탐 (Hard Sample)
   - TP보다 TN에 가까운 스펙트럼 분포를 보임.
   - 즉, AI로 생성됐음에도 실제 이미지(TN)와 비슷한 주파수 특성을 가짐.

<br>

### 주파수 에너지 분포 분석 (Radial Frequency Profile) 결과 
- X축: Log 주파수 (저주파 → 고주파)
- Y축: Log 에너지 (파워)
- Slope: 곡선의 기울기 → 값이 클수록(가파를수록) 저주파에 에너지가 집중됨
 <img width="1979" height="1578" alt="image" src="https://github.com/user-attachments/assets/75d29958-8fcc-4bd8-b1d8-905eb5091b8d" />
 
### 각 영역의 기울기가 유사하다 → 특정 주파수 대역에서 두드러진 에너지 증가가 존재하지 않는다.
- 특정 아티팩트에 에너지가 몰려 있지 않다.

<br>
<br>

## 2. 시각적 유사도 확인 (ResNet-50 + t-SNE)
-상용 탐지모델 중 성능이 가장 좋았던 ResNet-50 기반의 Corvi+를 백본으로 한 영역별 분포 t-SNE 시각화.
<img width="2377" height="1977" alt="image" src="https://github.com/user-attachments/assets/fdf9b074-b296-4cf7-b835-5469dab63313" />

### 결과분석
- TN(Real이미지 정탐)과 같은 영역에 존재하는 FN(Fake 이미지 정탐)이 많이 있는것으로 보아 해당 모델이 판단하는 Real artifact들이 Hard Sample에 다수 존재하는 것을 확인할 수 있음
- TP(Fake이미지 정탐) 영역에 포함되는 Hard Sample들이 존재하며 해당 샘플들은 실제로 TP영역과 유사한 동시에 t-SNE의 2D 시각화에 따른 왜곡으로 인한 결과로 보여짐

<br>
<br>

## 3. 의미적 유사도 확인 (CLIP + UMAP)
- CLIP의 백본에 최종 출력 전 결과 벡터를 기반으로 UMAP 시각화를 진행
- Hard Sample이 CLIP의 feature extraction 과정을 통해 분리가 되는지 확인하고자 실험을 진행 
<img width="2966" height="2371" alt="image" src="https://github.com/user-attachments/assets/c24ee5f3-a223-4deb-b0ed-be340c8ec43f" />

### 결과분석
- Hard Sample(FN)만의 고유한 의미적 패턴이 없다 → 특정 주제나 장면에 편향되지 않고 다양한 콘텐츠로 구성됨
- Real과 Fake를 의미적으로 구분할 수 없다(추가적인 학습이 필요해 보인다) → CLIP 수준에서는 AI 이미지와 실제 이미지가 동일한 시맨틱 공간을 공유
- t-SNE에서 보인 Real_TN과의 유사성은 시각적 특성 때문 → 의미가 비슷해서가 아니라 픽셀/텍스처 레벨의 특성이 비슷한 것으로 보인다
