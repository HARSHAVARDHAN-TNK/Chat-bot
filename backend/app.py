from flask import Flask, request, jsonify
from flask_cors import CORS
import joblib
import json
import random

app = Flask(__name__)
CORS(app)

import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
with open(os.path.join(BASE_DIR, "data", "intents.json"), encoding="utf-8") as f:
    intents = json.load(f)["intents"]
# Load trained model
model = joblib.load("intent_model.pkl")

# Helper: find intent object by tag
def find_intent(tag):
    for intent in intents:
        if intent["tag"] == tag:
            return intent
    return None

@app.route("/", methods=["GET"])
def home():
    return "<h2>EduBot API is running 🚀</h2><p>Use POST /chat to talk to the bot.</p>"

@app.route("/chat", methods=["POST"])
def chat():
    data = request.get_json(force=True) or {}
    user_msg = (data.get("message") or "").strip()
    if not user_msg:
        return jsonify({"reply": "Please type a question."}), 400

    # Predict intent
    probs = model.predict_proba([user_msg])[0]
    pred = model.predict([user_msg])[0]
    confidence = float(probs.max())

    # Threshold (lowered for small dataset)
    if confidence < 0.25:
        return jsonify({
            "intent": "uncertain",
            "confidence": round(confidence, 3),
            "reply": "I’m not fully sure what you mean. Try asking about admissions, courses, or placements."
        })

    # Get response for predicted intent
    intent_obj = find_intent(pred)
    if intent_obj and intent_obj.get("responses"):
        return jsonify({
            "intent": pred,
            "confidence": round(confidence, 3),
            "reply": random.choice(intent_obj["responses"])
        })

    # Fallback
    return jsonify({
        "intent": "uncertain",
        "confidence": round(confidence, 3),
        "reply": "Sorry, I don’t have an answer for that yet."
    })

if __name__ == "__main__":
    # Important for Render: bind to 0.0.0.0 and use PORT env var if available
    import os
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)