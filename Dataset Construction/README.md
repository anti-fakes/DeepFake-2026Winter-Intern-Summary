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

## 2. 최종 이미지 캡션 생성 프롬프트 구조
<img src="https://github.com/user-attachments/assets/3f994fe1-67b6-44c1-9a00-ca331b2fb048" width="100%">

LLM을 활용하여 다양한 이미지 캡션을 생성하기 위해 아래와 같은 특징으로 캡션 프롬프트를 구성.
1. LLM에게 역할을 부여하여 전문적인 LLM으로 활용하고자 유도.
2. 생성할 이미지(Scene Graph)와 촬영 도구(Capture Device)를 분리.
3. 무작위성 부여(RANDOM): Scene Graph를 `Subject + Action + Target + Location`으로 구체화하고 각 요소를 LLM이 결정하도록 하여 다양한 Scen Graph가 만들어지도록 유도함.
4. 장르(Genre) 활용: 비정상적인 이미지 생성을 완화하기 위해 사용자가 장르를 설정하여 Domain을 줄이고, LLM이 비정상 혹은 비현실적인 캡션을 생성하지 않도록 강제.
5. 최종 프롬프트: 구체적인 예시를 포함하여 최종 캡션 생성 프롬프트를 작성합니다.

<br>

## 3. 촬영 도구 (Capture Device) 세부 정의

<img src="https://github.com/user-attachments/assets/5a275fb3-4e76-4328-963a-c21bb7936a94" width="100%">

기존의 불분명한 기기 차이를 극복하기 위해 디바이스의 특성을 구체적으로 재정의.
* 정의: 기본적으로 Analog Film과 High-End DSLR 두 가지 경우로 명확히 나누고, 장르에 따라 Drone, Action Cam 등을 추가로 사용하도록 정의.
* 구체화: 사용할 장비, 시점, 느낌, 화질 등을 상세히 묘사하며, 특히 반드시 배제해야 할 특징들도 함께 언급하여 해당 디바이스의 고유한 느낌을 강하게 부여

<br>

## 4. 파이프라인 요약 및 결과

* 주제(Subject)와 촬영 도구(Capture Device)는 사용자가 직접 선정할 수 있도록 하며, 객체(Object)와 관계(Relationship)의 생성은 LLM에게 위임하여 랜덤하게 구성.
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
| **첫 번째 사진 설명**<br>(상세 내용) | **두 번째 사진 설명**<br>(상세 내용) | **세 번째 사진 설명**<br>(상세 내용) | **네 번째 사진 설명**<br>(상세 내용) |





