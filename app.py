from flask import Flask, render_template, request, jsonify
import json
import pickle
import numpy as np
import os

app = Flask(__name__)

# ---------------- BASE PATH ----------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# ---------------- LOAD MODELS ----------------
with open(os.path.join(BASE_DIR, "student_performance_model.pkl"), "rb") as f:
    performance_model = pickle.load(f)

with open(os.path.join(BASE_DIR, "future_score_prediction_model.pkl"), "rb") as f:
    future_score_prediction_model = pickle.load(f)

with open(os.path.join(BASE_DIR, "quiz_data.json"), "r") as f:
    quiz_questions = json.load(f)

# ---------------- PAGES ----------------
@app.route("/")
def index():
    return render_template("index.html")

@app.route("/quiz")
def quiz_page():
    return render_template("quiz.html")

@app.route("/result")
def result_page():
    return render_template("result.html")

# ---------------- QUIZ API ----------------
@app.route("/api/quiz", methods=["GET"])
def get_quiz():
    return jsonify(quiz_questions)

# ---------------- PERFORMANCE PREDICTION ----------------
@app.route("/api/predict", methods=["POST"])
def predict():
    data = request.json

    score = float(data.get("score", 0))
    time_taken = int(data.get("time_taken", 0))

    features = np.array([[score, 100, time_taken, 1, 1, 10]])
    prediction = performance_model.predict(features)[0]

    return jsonify({
        "message": "Tutoring Recommended" if prediction == 1 else "Performance is Good"
    })

# ---------------- FUTURE SCORE PREDICTION ----------------
@app.route("/api/future-score", methods=["POST"])
def future_score():
    data = request.json

    current_score = float(data.get("score", 0))

    features = np.array([[
        current_score,
        float(data.get("max_score", 100)),
        float(data.get("time_taken", 0)),
        int(data.get("attempt_number", 1)),
        int(data.get("subject_encoded", 1)),
        int(data.get("grade_level_encoded", 10))
    ]])

    predicted_score = float(
        future_score_prediction_model.predict(features)[0]
    )

   
    predicted_score = max(predicted_score, current_score)
    predicted_score = min(predicted_score, 100)

    return jsonify({
        "future_score": round(predicted_score, 2)
    })

# ---------------- RUN ----------------
if __name__ == "__main__":
    app.run(debug=True)