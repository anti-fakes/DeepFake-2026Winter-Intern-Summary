<br>

## 5. Dataset Evaluation Details (데이터셋별 세부 평가 결과)
다양한 Real 및 Fake 데이터셋에 대한 모델(Corvi+)의 세부 탐지 성능과 정답/오답 샘플 수입니다.

| | coco_real(real) | facebook_real | reddit_real | twitter_real | Redcaps(real) | Synthbuster(real) | z-image(fake) | GPT(fake) | Nanobanana(fake) | Wild_data(Ours) | twitter_fake | facebook_fake | reddit_fake |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **Total_images** | 1000 | 136 | 289 | 61 | 2987 | 1000 | 9656 | 347 | 447 | 1893 | 230 | 132 | 565 |
| **Corvi+(Stay-positive)** | 0.99 | 1 | 0.986 | 1 | 0.99 | 0.99 | 0.94 | 0.86 | 0.99 | 0.203 | 0.61 | 0.78 | 0.48 |
| **Incorrect Sample** | 1 | 0 | 4 | 0 | 17 | 6 | 608 | 46 | 4 | 1509 | 105 | 30 | 294 |
| **Correct Sample** | 999 | 136 | 285 | 61 | 2970 | 994 | 9048 | 301 | 443 | 384 | 125 | 102 | 271 |
