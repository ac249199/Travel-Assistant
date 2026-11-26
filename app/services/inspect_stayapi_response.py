import json

from pathlib import Path


file_path = Path(
    "data/api_responses/varanasi_hotels_2026_11_25.json"
)

with open(file_path, "r", encoding="utf-8") as file:
    results = json.load(file)

print("\n========== RESPONSE KEYS ==========")
print(results.keys())

data = results.get("data", {})

print("\n========== DATA KEYS ==========")
print(data.keys())

hotels = data.get("hotels", [])

if hotels:
    print("\n========== FIRST HOTEL COMPLETE DATA ==========")

    print(json.dumps(
        hotels[0],
        indent=4,
        ensure_ascii=False
    ))