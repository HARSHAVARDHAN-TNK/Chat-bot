import json
import os

INPUT_PATH = os.path.join("data", "intents.json")
OUTPUT_PATH = os.path.join("data", "intents_converted.json")

with open(INPUT_PATH, "r", encoding="utf-8") as f:
    data = json.load(f)

# Expecting: { "intents": [ { "query": "...", "response": "..." }, ... ] }
if not isinstance(data, dict) or "intents" not in data:
    raise ValueError("Dataset must be a dict with key 'intents'")

converted = {"intents": []}

for i, item in enumerate(data["intents"]):
    query = item.get("query")
    response = item.get("response")

    if not query or not response:
        print(f"⚠️ Skipping item {i} (missing query/response)")
        continue

    converted["intents"].append({
        "tag": f"intent_{i+1}",
        "patterns": [query],
        "responses": [response]
    })

with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
    json.dump(converted, f, indent=2, ensure_ascii=False)

print(f"✅ Converted {len(converted['intents'])} intents")
print(f"💾 Saved to {OUTPUT_PATH}")