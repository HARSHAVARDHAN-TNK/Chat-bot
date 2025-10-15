import json
from collections import Counter
import os

DATA_PATH = os.path.join("data", "intents.json")

with open(DATA_PATH, "r", encoding="utf-8") as f:
    data = json.load(f)

intents = data.get("intents", [])
print(f"\n✅ Total intents: {len(intents)}")

tags = []
errors = []

for i, intent in enumerate(intents):
    tag = intent.get("tag", "").strip()
    patterns = intent.get("patterns", [])
    responses = intent.get("responses", [])

    tags.append(tag)

    if not tag:
        errors.append(f"[Intent {i}] Missing tag.")
    if not patterns:
        errors.append(f"[{tag}] No patterns.")
    if not responses:
        errors.append(f"[{tag}] No responses.")
    if isinstance(responses, list) and all(not r.strip() for r in responses):
        errors.append(f"[{tag}] Responses are empty strings.")

# Check for duplicate tags
tag_counts = Counter(tags)
dupes = [tag for tag, count in tag_counts.items() if count > 1]

if dupes:
    print("\n⚠️ Duplicate tags found:")
    for tag in dupes:
        print(f" - {tag} ({tag_counts[tag]} times)")

if errors:
    print("\n❌ Issues found:")
    for err in errors:
        print(" -", err)
else:
    print("\n✅ No structural issues found.")

# Summary
print("\n📊 Tag distribution:")
for tag, count in tag_counts.items():
    print(f" - {tag}: {count} intent(s)")