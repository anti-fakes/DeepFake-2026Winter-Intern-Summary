import json
from collections import defaultdict

# 1. 원본 데이터 로드
input_file = "coco_prompts_original.json"
print(f"Reading {input_file}...")

with open(input_file, "r", encoding="utf-8") as f:
    data = json.load(f)

# 2. ID별로 데이터 그룹화
# 동일한 이미지는 같은 ID를 가지므로 리스트로 묶습니다.
grouped_data = defaultdict(list)
for item in data:
    grouped_data[item["id"]].append(item)

longest_results = []
shortest_results = []

print("Processing prompts by length...")
for img_id, items in grouped_data.items():
    # prompt 문자열 길이를 기준으로 최대/최소값 탐색
    # len()을 기준으로 가장 긴 항목과 짧은 항목을 추출합니다.
    longest_item = max(items, key=lambda x: len(x["prompt"]))
    shortest_item = min(items, key=lambda x: len(x["prompt"]))
    
    longest_results.append(longest_item)
    shortest_results.append(shortest_item)

# 3. 결과 저장
# 가장 긴 설명 저장
with open("coco_prompts_longest.json", "w", encoding="utf-8") as f:
    json.dump(longest_results, f, ensure_ascii=False, indent=4)

# 가장 짧은 설명 저장
with open("coco_prompts_shortest.json", "w", encoding="utf-8") as f:
    json.dump(shortest_results, f, ensure_ascii=False, indent=4)

print("-" * 30)
print(f"전체 고유 이미지 수: {len(grouped_data)}개")
print(f"저장 완료 (가장 긴 프롬프트): coco_prompts_longest.json")
print(f"저장 완료 (가장 짧은 프롬프트): coco_prompts_shortest.json")