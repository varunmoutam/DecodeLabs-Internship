"""
app.py
------
Flask web application for Iris Flower Classification.
Run after train_model.py has been executed at least once.

    python app.py
"""

import os
import json
import numpy as np
import joblib
from flask import Flask, render_template, request, jsonify

# ── App setup ────────────────────────────────────────────────────────────────
app = Flask(__name__)
BASE_DIR    = os.path.dirname(os.path.abspath(__file__))
MODEL_PATH  = os.path.join(BASE_DIR, "model", "iris_knn.pkl")
SCALER_PATH = os.path.join(BASE_DIR, "model", "scaler.pkl")

# ── Load model & scaler once at startup ─────────────────────────────────────
if not os.path.exists(MODEL_PATH) or not os.path.exists(SCALER_PATH):
    raise FileNotFoundError(
        "Model or scaler not found. Please run  python train_model.py  first."
    )

model  = joblib.load(MODEL_PATH)
scaler = joblib.load(SCALER_PATH)

CLASS_NAMES = ["Setosa", "Versicolor", "Virginica"]
CLASS_INFO  = {
    "Setosa": {
        "description": "Iris Setosa is the most distinct species, easily "
                        "identified by its small petals and wide sepals. "
                        "Native to Arctic and sub-arctic regions.",
        "color": "#4f8ef7",
        "emoji": "🔵"
    },
    "Versicolor": {
        "description": "Iris Versicolor, the Blue Flag Iris, thrives in "
                        "wetland environments across North America. Its "
                        "features are intermediate between the other two.",
        "color": "#f7934f",
        "emoji": "🟠"
    },
    "Virginica": {
        "description": "Iris Virginica, the Virginia Iris, is the largest "
                        "of the three species with the longest petals. "
                        "Found in freshwater wetlands of eastern North America.",
        "color": "#4fc97f",
        "emoji": "🟢"
    }
}

# ── Routes ───────────────────────────────────────────────────────────────────

@app.route("/")
def index():
    """Main prediction page."""
    return render_template("index.html")


@app.route("/predict", methods=["POST"])
def predict():
    """
    Accepts form data with four float fields:
        sepal_length, sepal_width, petal_length, petal_width
    Returns JSON:
        { class, confidence, probabilities, color, emoji, description }
    """
    try:
        sepal_length = float(request.form["sepal_length"])
        sepal_width  = float(request.form["sepal_width"])
        petal_length = float(request.form["petal_length"])
        petal_width  = float(request.form["petal_width"])

        # ── Validation ──────────────────────────────────────────────────────
        for name, val, lo, hi in [
            ("Sepal length", sepal_length, 1.0, 10.0),
            ("Sepal width",  sepal_width,  1.0,  8.0),
            ("Petal length", petal_length, 0.1,  8.0),
            ("Petal width",  petal_width,  0.1,  4.0),
        ]:
            if not (lo <= val <= hi):
                return jsonify({
                    "error": f"{name} must be between {lo} and {hi} cm."
                }), 400

        features = np.array([[sepal_length, sepal_width,
                               petal_length, petal_width]])
        features_scaled = scaler.transform(features)

        prediction   = model.predict(features_scaled)[0]
        probabilities = model.predict_proba(features_scaled)[0]
        class_name   = CLASS_NAMES[prediction]
        confidence   = float(probabilities[prediction]) * 100

        prob_dict = {
            CLASS_NAMES[i]: round(float(p) * 100, 2)
            for i, p in enumerate(probabilities)
        }

        return jsonify({
            "class":       class_name,
            "confidence":  round(confidence, 2),
            "probabilities": prob_dict,
            "color":       CLASS_INFO[class_name]["color"],
            "emoji":       CLASS_INFO[class_name]["emoji"],
            "description": CLASS_INFO[class_name]["description"]
        })

    except (KeyError, ValueError) as exc:
        return jsonify({"error": f"Invalid input: {exc}"}), 400
    except Exception as exc:
        return jsonify({"error": f"Server error: {exc}"}), 500


@app.route("/about")
def about():
    """About page – project info, model metrics, tech stack."""
    k_value = model.n_neighbors
    return render_template("about.html", k_value=k_value)


# ── Run ──────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)