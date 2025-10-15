import json
import os
import numpy as np
from sentence_transformers import SentenceTransformer

DATA_PATH = os.path.join("data", "intents.json")
MODEL_PATH = os.path.join("models")

# Load dataset safely
with open(DATA_PATH, "r", encoding="utf-8") as f:
    data = json.load(f)

if isinstance(data, dict) and "intents" in data:
    intents = data["intents"]
elif isinstance(data, list):
    intents = data
else:
    raise ValueError("❌ Invalid dataset format: must be {\"intents\": [...]} or a list of intents")

print(f"✅ Loaded {len(intents)} intents")

# Extract patterns, tags, responses
patterns, tags, responses = [], [], []
for intent in intents:
    tag = intent.get("tag", "unknown")
    for pattern in intent.get("patterns", []):
        patterns.append(pattern)
        tags.append(tag)
        responses.append(intent.get("responses", [""])[0])

print(f"✅ Total patterns: {len(patterns)}")

# Encode with transformer
model = SentenceTransformer("all-MiniLM-L6-v2")
embeddings = model.encode(patterns)

# Save embeddings + metadata
os.makedirs(MODEL_PATH, exist_ok=True)
np.save(os.path.join(MODEL_PATH, "embeddings.npy"), embeddings)

meta = {"patterns": patterns, "tags": tags, "responses": responses}
with open(os.path.join(MODEL_PATH, "meta.json"), "w", encoding="utf-8") as f:
    json.dump(meta, f, indent=2, ensure_ascii=False)

print("✅ Training complete. Files saved to models/")