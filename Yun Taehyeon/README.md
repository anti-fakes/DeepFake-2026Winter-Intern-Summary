# DeepFake-2026Winter-Intern-Summary
Technical Report for 2026 Winter Research Internship (AISI)
> 이 문서는 2026 ETRI 동계 연구연수생(26.01.01.~26.02.28.) 기술문서입니다.
> 작성자: 윤태현 연구연수생

## Dataset Path
All datasets are in AICA `/home/deepfake/datasets/` and folders are start with `intern_`
`intern_zimage_turbo`: Z-Image Turbo images
`intern_wild_img`: Wild images(from web)
`intern_wild_vid`: Wild videos(from web)
`intern_instagram_compression/`: Instagram Compression Test(2번 항목 참고)




## 1. Dataset Construction
### 1-1. ⚡Generate Images with Z-Image Turbo
Open Weights 모델 중 고품질 경량 모델인 Z-Image Turbo를 바탕으로 이미지 생성을 진행함.

Z-Image Turbo: <https://github.com/Tongyi-MAI/Z-Image>
 

#### Prompt References
- parti-prompts: <https://huggingface.co/datasets/nateraw/parti-prompts>
- COCO captions: <https://huggingface.co/datasets/jxie/coco_captions>

#### Prompt Preprocessing
COCO captions의 경우 동일 image에 대한 다양한 prompt가 존재하므로, prompt length에 따라 분리하여 저장했다. 가장 포괄적인 image를 생성하기 위해 이 중 가장 짧은 prompt를 생성에 사용했다.
- `coco_prompts_original.json`: caption 원본 (Too big to upload github)
- `coco_prompts_longest.json`: 각 image에 대한 가장 긴 caption
- `coco_prompts_shortest.json`: 각 image에 대한 가장 짧은 caption
- `COCO_captions_seperate.py`: COCO cpations 분리

#### Generate with parti-prompts
- Z-Image Turbo 7 inference steps: 1,632 samples
- Z-Image Turbo 8 inference steps: 1,632 samples

#### Generate with COCO captions
- Z-Image Turbo 8 inference steps: 7,000 samples

### 1-2.  🌐Collect Images & Videos from Web(wild data)
Wild data 수집은 웹에 존재하는 무질서한 deepfake, synthesis content 수집을 일컫는다.
#### Deepfake vs Synthesis Content
여기서 분류한 기준은 절대적 기준이 아니며, 임의 분류임을 밝힌다.
- Deepfake: 유명인의 얼굴이 포함된 이미지나 비디오
- Synthesis Content: Deepfake 기준이 아닌 기타 합성 컨텐츠 전부

#### References
수집을 위해 활용한 사이트들은 다음과 같다.
- Instagram(대부분)
- Facebook
- Tiktok
- Grok
- Reddit
- Artificial Analysis
- X(구 Twitter)

#### Methods
수집을 위해 사용한 방법은 다음과 같으며, 자세한 내용은 pdf를 참고한다. [웹 데이터 수집 과정](./img/260120_웹_데이터_수집_방법_윤태현)

#### Results
Total 2,213 samples 수집 완료함.
 - Wild data(image): 1,813 samples
 - Wild data(video): 320 samples (Not used)


### 1-3. 📄Metadata Explanation
메타데이터는 본 연구자가 생성 및 수집한 모든 이미지 폴더와 hard samples 폴더에 적용되어 있다(intern_instagram_compression 제외).
#### Components of Metadata
- id: 고유 id 값으로, UUID 사용
- file_name: category + source + label + short UUID로 구성
- created_at: 생성 일자(wild data의 경우 download 일자)
- file_format: 파일 형식
- category: `[deepfake, synthesis]`
- source: `[generate, instagram, grok ...]`
- model: wild image의 경우 생성 모델 신뢰 불가로 인해 공란
- label: `[fake]`
- prompt: 생성 이미지의 경우 parti-prompts나 COCO captions의 prompt 첨부
- subject: parti-prompts로 생성한 경우 생성 주제가 존재하여 subject 첨부
- source_content: `null` (real image 부재로 인해 불필요 component)

![Metadata Example](./img/metadata_screenshot.png)

## 2. Instagram Compression Policy Reverse Engineering
### 2-1. 👨‍🔬실험 동기 및 실험 데이터셋
대부분의 wild data의 reference가 Instagram이며, Instagram의 경우 image compression policy가 정확하게 공개 되어있지 않음. Resizing, Compression 등 post-processing은 AI generated contents의 고유 artifact를 훼손하여 detection model의 dectection rate를 저하시키는 주요 요인이다.

이에 image를 실제로 업로드 및 다운로드하여 전후 비교 및 post-processing 모사 환경을 실험하여 추후 wild data를 타겟으로 한 detection test에 활용할 수 있도록 한다.

Instagram에서 선호하는 여러 이미지 비율 중 정방형을 채택하여 생성한 Z-Image Turbo 및 COCO real dataset에서 정방형 이미지를 50장씩 random 추출한다.

Instagram의 경우 직접 다운로드가 불가능하기 때문에 `savefrom.net` 이라는 웹사이트를 통해 우회하여 다운로드한다.
- savefrom.net: <https://ko.savefrom.net/229au/>

### 2-2. 🧪Pilot Test
앞서 언급한 100장의 데이터셋을 활용하기 전, Instagram의 Basic Upload Environment를 파악하기 위해 총 10장의 image로 pilot test를 진행한다. Instagram compression policy reverse engineering에서 사용할 용어의 정의는 다음과 같다. 
- 압축(compression) = Instagram Upload 후 Download
- n차 압축 = 압축 과정을 n번 진행

Pilot test에 활용한 image 목록은 다음과 같다.

#### Pilot Test Data
- `12m_1`~`12m_3`: Photo by smartphone(Galaxy S21, 12MP, `.jpg`)
- `64m_1`~`64m_3`: Photo by smartphone(Galaxy S21, 64MP, `.jpg`)
- `z1`~`z3`: Z-Image Tubro images(`.png`)
- `web`: Image from website(wild data, `.jpg`)

#### Test Case
- PC Environment Compression
- Mobile Environment Compression
- Compression N times

#### Results
결과는 아래와 같으며, pilot test를 통한 분석은 다음과 같다.
![instagram_compression_pilot_test](./img/instagram_compression_pilot_test.png)

- Mobile Environment에서 더 큰 압축이 일어난다.
- Mobile Environment Compression의 경우 확장자가 `.webp`로 바뀌어, 2차 압축이 불가하다.
- PC Environment에서는 upload 용량 제한이 있다.(`64m_1`~`64m_3` 업로드 실패)
- 1차 압축 ~ 3차 압축의 용량 변화는 거의 없다.


### 2-3. ⬆️Instagram Compression Policy by Upload Environment
Pilot test의 결과를 바탕으로, 본 실험 시 n차 압축은 PC Environment에서만 진행한다.

#### Results
결과는 아래와 같다.
![instagram_compression_100](./img/instagram_compression_100.png)


#### PC Environment
- 업로드 image에 대한 용량 제한이 존재한다.
- 업로드 시 확장자가 `.jpg`로 변환된다.
- 반복 업로드 시 용량 압축은 최초 압축 수준에서 변화가 거의 없다. (1차 압축 용량 거의 유지)
- `.webp`에 비해 용량 손실이 덜 일어난다.
#### Mobile(app) Environment
- 업로드 image에 대한 용량 제한이 명시되어 있지 않다.
- 업로드 시 확장자가 `.webp`로 변환된다.
- `.webp`로 변환된 image는 재업로드가 불가하다(`.webp` 형식 미지원).
- `.jpg`에 비해 용량 손실이 더 일어난다.

### 2-4. 🎭Instagram Photo Upload Environment Simulation
Instagram의 압축 환경을 모사하기 위해 다양한 resizing, compression을 진행하여 가장 유사한 환경값을 찾아낸다. REsizing과 compression을 위해 활용한 코드는 `./scripts/compression_simul.py`를 참고한다.

#### Tools
- Bicubic / Lanczos 보간법: 고급 resizing 기법
- JPEG, WebP Compression: 각각 PC, Mobile Environment 모사
- Stay-Positive(Corvi+): Deepfake detection model의 score로 유사도 측정

#### Dataset
- Z-Image Turbo(50 samples): 1024x1024의 균일한 resolution
#### Test Settings: PC Environment
- Bicubic 보간법으로 resizing
- JPEG 압축(`Q=[80, 84, 88, 92, 96, 100]`, 기초 실험을 통해 구간 선정)
- (실제 compressed image - test image)를 Stay-Positive(Corvi+) score로 측정(MAE)
#### Test Settings: Mobile Environment
- Lanczos 보간법으로 resizing
- WebP 압축(`Q=[40, 44, 48, 52, 56, 60]`, 기초 실험을 통해 구간 선정)
- (실제 compressed image - test image)를 Stay-Positive(Corvi+) score로 측정(MAE)

#### Results
결과는 다음과 같다.
![PC_JPEG_score_similarity_graph](./img/PC_JPEG_score_similarity_graph.png)
![Mobile_WebP_score_similarity_graph](./img/Mobile_WebP_score_similarity_graph.png)

결과를 통해 얻을 수 있는 사실은 다음과 같다.
- JPEG 압축 시 `Q=92`에서 가장 비슷한 결과값이 나온다.
- WebP 압축 시 `Q=52`에서 가장 비슷한 결과값이 나온다.

#### Limitation
- Stay-Positive(Corvi+) score를 활용한 유사도 판단의 유효성
- 다양한 resizing 기법의 적용 필요
- 실제 Instagram의 적응형 압축 환경 모사의 한계점
- Spectrum library 적용의 한계(Meta, 2019, C++ 기반으로 test에 적용하지 않음)
- JPEG quality factor scale이 너무 높게 나옴


## 3. SOTA Model Detection Test
### 3-1. 🤖Detection Model & Dataset List
인턴 기간동안 생성 및 수집한 image dataset에 대해 현존하는 SOTA deepfake detection model들을 활용하여 성능 검증 및 detection model을 회피하는 hard samples를 구축하는데에 그 목적을 둔다.

SOTA detection model과 dataset은 아래와 같다.

#### Detection Model
- DDA: <https://github.com/roy-ch/Dual-Data-Alignment>
- B-Free: <https://github.com/grip-unina/B-Free/tree/main>
- SAFE: <https://github.com/Ouxiang-Li/SAFE>
- Stay-Positive(Rajan+): <https://github.com/AniSundar18/AlignedForensics>
- Stay-Positive(Corvi+): <https://github.com/AniSundar18/AlignedForensics>

#### Dataset
- COCO real dataset(1,000 samples)
- Z-Image Turbo (7,264 samples)
- Wild Data (1,893 samples)
- GPT (347 samples)
- Nano Banana (447 samples)

### 3-2. 📝Test Result
각 dataset에 대한 detection model의 accuracy는 다음과 같다.
| Dataset | DDA | B-Free | SAFE | Rajan/Ours+ | Corvi+ |
|---|---|---|---|---|---|
| COCO_real (1,000) | 0.97 | 0.99 | 0.784 | 0.999 | 0.999 |
| Z-Image Turbo (7,264) | 0.203 | 0.266 | 0.709 | 0.032 | **0.940** |
| Wild_data (1,893) | 0.197 | **0.376** | 0.071 | 0.131 | 0.203 |
| Nano Banana (447) | 0.53 | 0.463 | 0.839 | 0.894 | **0.991** |
| GPT (347) | 0.009 | 0.04 | 0.741 | 0.034 | **0.867** |


### 3-3. ❌Hard Samples
5개의 detection model을 모두 회피한 samples를 'Hard Samples'로 정의하며, 최종적으로 974 hard samples를 수집했다.
| Dataset | Hard Samples |
|---|---|
| Z-Image Turbo (7,264) | 40 |
| Wild_data (1,893) | 892 |
| Nano Banana (447) | 0 |
| GPT (347) | 42 |


## 4. Image Degradation Test
### 4-1. 👨‍🔬실험 동기 및 실험 데이터셋
Image Degradation Test는 Wild Data의 매우 높은 탐지기 회피율을 바탕으로, 실제 어떤 wild한 성질들이 실제 detection model의 탐지율 저하를 이끌어내는지 알아내고자 진행했다.

Detection Model은 SOTA Detection Model Test에서 가장 높은 성능을 보인 Stay-Positive(Corvi+)(이하 Corvi+)를 사용했으며, dataset은 fake image인 Z-Image Turbo와 real image인 redcaps, synthbuster를 활용했다. COCO dataset의 경우 Corvi+ train에 일부 사용되었다는 사실을 바탕으로 제외시켰다.

#### Detection Model
- Stay-Positive(Corvi+): <https://github.com/AniSundar18/AlignedForensics>

#### Dataset
- Z-Image Turbo(Fake, 1,000 samples)
- Redcaps(Real, 3,000 samples)
- Synthbuster(Real, 1,000 samples)

### 4-2. 🔥Gaussian Noise & Gaussian Blur Test
다양한 degradation method 중, 가장 일반적이고 보편적으로 적용할 수 있는 gaussian noise와 gaussian blur를 적용했다.

#### Gaussian Noise
`Scale = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10]`
#### Gaussian Blur
`Scale = [0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0]`
#### Degradation Example
`Base Image - Degradation Image`를 통해 실제 적용된 gaussian noise와 gaussian blur를 눈으로 확인한다.

[적용 이미지 넣기]

#### Result



### 4-3. ⬛Grayscale Test
Gaussian noise와 gaussian blur의 경우 주변 픽셀의 값을 이용하여 degradation을 하는 방법이므로 색상에 민감할 수 있다는 가정하에 추가적으로 실험했다. Gaussian noise와 gaussian blur를 사용한 이전 실험에서 그대로 grayscale을 적용하여 그대로 재실험했다.

#### Grayscale
Grayscale 'L' Mode: 

## 5. Other Attempts
### 5-1. High Frequency Bias Test

### 5-2. 

## 6. Conclusion
Thank you for supporting
