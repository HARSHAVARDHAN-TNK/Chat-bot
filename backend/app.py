from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import json
import numpy as np
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

app = Flask(__name__)
CORS(app)

# Paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODELS_DIR = os.path.join(BASE_DIR, "models")
EMBEDDINGS_PATH = os.path.join(MODELS_DIR, "embeddings.npy")
META_PATH = os.path.join(MODELS_DIR, "meta.json")

# Globals
model = None
embeddings = None
patterns = []
tags = []
responses = []

def load_resources():
    """Load embeddings and meta data"""
    global model, embeddings, patterns, tags, responses

    if not os.path.exists(META_PATH) or not os.path.exists(EMBEDDINGS_PATH):
        app.logger.error("Model files not found. Please run train.py first.")
        return False

    with open(META_PATH, "r", encoding="utf-8") as f:
        meta = json.load(f)

    patterns = meta.get("patterns", [])
    tags = meta.get("tags", [])
    responses = meta.get("responses", [])

    embeddings = np.load(EMBEDDINGS_PATH)

    if len(patterns) == 0 or embeddings.shape[0] == 0:
        app.logger.error("Empty dataset or embeddings. Re-run train.py with valid intents.")
        return False

    model = SentenceTransformer("all-MiniLM-L6-v2")
    app.logger.info(f"Loaded {len(patterns)} patterns with embeddings shape {embeddings.shape}")
    return True

READY = load_resources()

@app.route("/ping", methods=["GET"])
def ping():
    return jsonify({"status": "ok" if READY else "not_ready"})

@app.route("/chat", methods=["POST"])
def chat():
    if not READY:
        return jsonify({"error": "Model not ready. Run train.py first."}), 503

    data = request.get_json(silent=True) or {}
    query = str(data.get("query", "")).strip()

    if not query:
        return jsonify({"answer": "Please enter a valid question.", "tag": "fallback"}), 200

    try:
        query_vec = model.encode([query])
        scores = cosine_similarity(query_vec, embeddings)[0]
        best_idx = int(np.argmax(scores))
        best_score = float(scores[best_idx])

        threshold = 0.55
        if best_score < threshold:
            default_message = (
                "I’m sorry, I don’t have that information right now. "
                "Please contact the Vel Tech office for official details:\n"
                "📞 +91-44-2684 1601\n"
                "📧 admissions@veltech.edu.in\n"
                "🌐 www.veltech.edu.in"
            )
            return jsonify({
                "answer": default_message,
                "tag": "fallback",
                "match": {"pattern": patterns[best_idx], "score": best_score}
            }), 200

        reply = responses[best_idx]
        return jsonify({
            "answer": reply,
            "tag": tags[best_idx],
            "match": {"pattern": patterns[best_idx], "score": best_score}
        }), 200

    except Exception as e:
        app.logger.exception(f"Error in /chat: {e}")
        return jsonify({"error": "Internal error processing query."}), 500

@app.errorhandler(404)
def not_found(e):
    return jsonify({"error": "Route not found"}), 404

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)

