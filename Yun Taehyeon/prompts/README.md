## Prompt References
- parti-prompts: <https://huggingface.co/datasets/nateraw/parti-prompts>
- COCO captions: <https://huggingface.co/datasets/jxie/coco_captions>

## Prompt Preprocessing
COCO captions의 경우 동일 image에 대한 다양한 prompt가 존재하므로, prompt length에 따라 분리하여 저장했다. 가장 포괄적인 image를 생성하기 위해 이 중 가장 짧은 prompt를 생성에 사용했다.
- `coco_prompts_original.json`: caption 원본
- `coco_prompts_longest.json`: 각 image에 대한 가장 긴 caption
- `coco_prompts_shortest.json`: 각 image에 대한 가장 짧은 caption
