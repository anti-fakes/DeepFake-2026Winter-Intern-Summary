# T2I 기반 데이터셋 생성 (Caption & Image Generation)

본 섹션은 T2I(Text-to-Image) 모델을 활용하여 다양하고 현실적인 이미지를 생성하기 위한 프롬프트 엔지니어링 및 데이터셋 구축 파이프라인을 설명한다. 생성된 캡션 기반으로 만들어진 이미지는 현실에서 얻어지는 이미지들과 최대한 유사하게 만들기 위한 시도를 하였다.

---

## 1. 이미지 생성의 4가지 구성 요소
<img width="1207" height="652" alt="image" src="https://github.com/user-attachments/assets/3b9b4e4a-8d2a-422f-b81c-edf99ff40ee0" />




다양한 환경을 반영하기 위해 이미지 생성 요소를 4가지 계층으로 분리하여 설계.
* 촬영도구 (Capture Device): Smartphone, DSLR, CCTV, BlackBox, Drone 등 시점과 화질을 결정.
* 관계 (Relationship): 객체 간의 무수히 많은 상호작용 (배경 이미지의 경우 관계가 없을 수도 있음).
* 객체 (Object): 특정 주제나 배경에 부합하는 일반적인 물체들.
* 주제 및 배경 (Genre & Background): 세상의 대부분을 반영하기 위한 광범위한 환경.

<br>

<br>

## 2. 최종 이미지 캡션 생성 프롬프트 구조

LLM을 활용하여 다양한 이미지 캡션을 생성하기 위해 아래와 같은 특징으로 캡션 프롬프트를 구성.
1. **LLM 역할 부여**: 전문적인 디렉터(Contextual Photography Director)로서의 역할을 부여하여 퀄리티 높은 결과물 유도.
2. **요소 분리**: 생성할 이미지 내용(Scene Graph)과 촬영 도구(Capture Device)의 제약 조건을 명확히 분리.
3. **무작위성 부여(RANDOM)**: Scene Graph를 `Subject + Action + Target + Location`으로 세분화하고, LLM이 각 요소를 무작위로 결정하게 하여 다채로운 장면 생성 유도.
4. **장르(Genre) 활용**: 사용자가 장르를 설정해 도메인을 한정함으로써 비정상적이거나 비현실적인 캡션 생성을 방지.
5. **최종 프롬프트 & 예시**: 구체적인 출력 포맷과 예시를 포함하여 일관된 형태의 캡션을 얻어냄.

<br>

### 프롬프트 구조
아래 코드 블록의 내용을 복사하여 LLM(ChatGPT, Gemini, Claude 등)에 붙여넣어 사용 가능.
<br>
Capture Device, Chareteristic, Genre를 사용자가 직접 설정하여 프롬프트에 추가해 사용

````text
[System Prompt]
You are a "Contextual Photography Director". 
Your goal is to generate a highly detailed image prompt 
based on a randomly assembled Scene Graph and a specific Capture Device constraint.

[Instruction]
1. Randomly select variables for the Scene Graph.
   - IMPORTANT: The 'Subject' can be a person, an object, or a landscape feature.
   - If the Subject is a static object or landscape, set Action and Target to 'None'.
2. Apply the strict visual description associated with the selected Capture Device.

---
1. Scene Graph Generation (Randomly Pick One)
- Subject (Who/What): {Random Entity} (e.g., A tired nurse, A solitary mountain peak, A spilled coffee cup, A cute animal)
- Action (Doing what): {Random Verb OR 'None'} (e.g., staring at, running from, melting. Use 'None' for landscapes/still life)
- Target (To whom/what): {Random Object OR 'None'} (Connects to Action. Use 'None' if intransitive or no action)
- Location (Where): {Random Place} (e.g., Flooded subway station, Sunlit park, Neon-lit alley, On a velvet table)

2. Capture Device
Retrieve the "Description" for the selected Capture Device.
- Capture device: {capture Device}
- Description: {characteristics}

3. Prompt Construction:
- The prompt must describe visual imperfections and capture artifacts FIRST.
- Camera characteristics must reflect in-the-wild usage, not ideal studio conditions.

[Format Structure]
"[Capture Device characteristics + (optional)], a {Genre} photography image of [Subject] [Action] [Target] in [Location], shot on [Capture Device] in an unplanned, real-world setting." 

The image should appear as a naturally captured real-world photograph.

---
4. Output Generation
DO NOT GENERATE AN IMAGE.
Instead, output ONLY the final text prompt inside a code block, ready for copy-pasting.

[Output Example]
Shot on Sony A7R V, 85mm f/1.2 GM, shallow depth of field with imperfect focus, 
subtle motion blur from hand movement, natural color noise, visible JPEG compression artifacts, 
a street photography image of an elderly street musician playing 
a worn violin on a crowded pedestrian street during an overcast afternoon.
````

<br>
<br>

## 3. Capture Devices Database (촬영 기기 데이터베이스)
프롬프트 생성 시 LLM이 참고할 수 있는 촬영 기기별 시각적 특성 및 제약 조건(Negative Prompt). 이 데이터베이스를 통해 기기 고유의 물리적 특성과 결함을 프롬프트에 사실적으로 반영

<br>

### 촬영 장비 데이터베이스
아래 코드 블록을 복사하여 시스템 프롬프트의 하단이나 참조용 데이터베이스로 추가.

````text
[Database: Capture Devices]

1. Analog Film
   - Characteristics: Shot on 35mm film, Kodak Portra 400, natural film grain, slight motion blur, uneven exposure, subtle lens flare, soft focus falloff, organic texture casual snapshot. 
   - Negative: --no digital perfection, hdr, 4k, sharp, cgi

2. High-End DSLR
   - Characteristics: Shot on Sony A7R V, 85mm f/1.2 GM, creamy bokeh, non-uniform sharpness across frame, realistic lens perfections, occasional chromatic aberration.
   - Negative: --no noise, cctv, distortion, flat

3. CCTV
   - Characteristics: CCTV footage, security camera overlay, fixed high-angle view, wide lens distortion, low bitrate compression, muted colors, slight motion blur, chromatic aberration near the edges.
   - Negative: --no bokeh, high quality, studio lighting

4. Dashcam (Black Box)
   - Characteristics: Dashcam footage, view from inside car windshield, visible dashboard at bottom, wide-angle distortion, harsh contrast, slight motion blur from vehicle movement, windshield reflections.
   - Negative: --no bokeh, cinematic lighting, person holding camera, third person view.

5. Drone
   - Characteristics: Aerial photography, shot on DJI Mavic 3 Cine, bird's-eye view, high altitude, epic scale, sharp detail from edge to edge, mild atmospheric haze, slight motion blur from wind drift.
   - Negative: --no ground level shot, person holding camera, bokeh, shallow depth of field.

6. Action Cam (Optional)
   - Characteristics: Shot on GoPro Hero 12, fisheye lens, barrel distortion, high contrast, deep focus. 
   - Negative: --no telephoto, portrait blur, soft lighting.
````
기존의 불분명한 기기 차이를 극복하기 위해 디바이스의 특성을 구체적으로 재정의.
* 정의: 기본적으로 Analog Film과 High-End DSLR 두 가지 경우로 명확히 나누고, 장르에 따라 Drone, Action Cam 등을 추가로 사용하도록 정의
* 구체화: 사용할 장비, 시점, 느낌, 화질 등을 상세히 묘사하며, 특히 반드시 배제해야 할 특징들도 함께 언급하여 해당 디바이스의 고유한 느낌을 강하게 부여

<br>

## 4. 파이프라인 요약 및 결과

* 주제(Subject)와 촬영 도구(Capture Device)는 사용자가 직접 선정할 수 있도록 하며, 객체(Object)와 관계(Relationship)의 생성은 LLM에게 위임하여 랜덤하게 다양한 캡션 구성.
* 얻어진 캡션을 T2I 모델의 입력으로 사용하여 최종 이미지를 생성.


<br>

## 5-1. 예시 (동일 장르 다른 Capture Device)
| Analog film | High End DSLR |
| :---: | :---: |
| <img src="https://github.com/user-attachments/assets/a9cbefb1-ddbc-4fec-b6ed-359b033b8aa4" width="100%"> | <img src="https://github.com/user-attachments/assets/71710b31-0f5f-42d9-93ca-4bbf5f3acef6" width="100%"> |

| Black BOX | CCTV |
| :---: | :---: |
| <img src="https://github.com/user-attachments/assets/6d9837be-e42f-423b-8396-f228936ce374" width="100%"> | <img src="https://github.com/user-attachments/assets/424d6c63-e219-4e29-9e9c-e11c71b3bcb0" width="100%"> |

* 같은 이미지 캡션이라도 사용되는 촬영도구에 따라 T2I 모델이 다른 이미지를 출력하는 것을 확인할 수 있음.

<br>

## 5-2. 예시 (동일 장르 + LLM의 랜덤성)
| FOOD1 | FOOD2 | FOOD3 | 
| :---: | :---: | :---: |
| <img src="https://github.com/user-attachments/assets/bacbfc6e-e3c1-4b82-a529-4cbfd0f20718" width="100%"> | <img src="https://github.com/user-attachments/assets/fa4a93e2-548a-4d4b-8ee3-96ea604e9b90" width="100%"> | <img src="https://github.com/user-attachments/assets/479bf983-2e43-4eaa-a4c3-028ed3b7707b" width="100%"> |

| Landscape1 | Landscape2 | Landscape3 |
| :---: | :---: | :---: |
| <img src="https://github.com/user-attachments/assets/fc3c3e29-c28d-42cc-a0b1-b45a382ea0b0" width="100%" height="450"> | <img src="https://github.com/user-attachments/assets/b7dda4cd-ab40-46f4-b295-94d7062a915f" width="100%" height="450"> | <img src="https://github.com/user-attachments/assets/f427e117-b4e1-4f5d-93ed-5a85608f8a98" width="100%" height="450"> |


* 동일 장르 + 촬영도구 내에서도 LLM이 다양한 이미지를 생성하는 것을 확인할 수 있음.

<br>

## 6. 상식적(물리적) 오류 샘플 예시

| <img src="https://github.com/user-attachments/assets/2f223551-955f-47f5-b22a-40bad6ad4af6" width="220" height="220"> | <img src="https://github.com/user-attachments/assets/b9e639b9-1393-4672-b5fa-8dee498071fe" width="220" height="220"> | <img src="https://github.com/user-attachments/assets/0231f5b8-0d02-4037-9eb8-5ddf819d95f8" width="220" height="220"> | <img src="https://github.com/user-attachments/assets/a3a66fa6-487b-4d3e-bff4-655a498f30f8" width="220" height="220"> |
| :---: | :---: | :---: | :---: |
| **객체 오류**<br>잔을 들고있는데 아래에 추가 잔이 존재 | **의미적 오류**<br>타자가 헬멧과 글러브를 동시에 착용한 채 홈으로 슬라이딩하는 비현실적 상황 | **물리적 구조 오류**<br>도로 중앙선이 없고, 단일 차선에서 양방향 차량이 동시에 주행하는 구조적 모순 | **중력/접촉 위반 오류**<br>보행자의 발이 지면과 완전히 맞닿지 않아 부유하는 듯한 형태로 표현 |





