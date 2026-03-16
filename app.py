# app.py
import os
from flask import Flask, render_template, request, jsonify, redirect, url_for
from ai_generator import generate_exam
from grader import grade_exam, check_answer
from config import EXAM_SIZE

app = Flask(__name__)

# For simplicity we store the current exam in memory.
# For production scale, store per-user in DB or server session.
CURRENT_EXAM = []

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/generate", methods=["GET"])
def generate_route():
    global CURRENT_EXAM
    CURRENT_EXAM = generate_exam()
    return render_template("exam.html", exam=CURRENT_EXAM)

@app.route("/submit", methods=["POST"])
def submit():
    global CURRENT_EXAM
    answers = request.form.to_dict()
    score, results = grade_exam(CURRENT_EXAM, answers)
    return render_template("results.html", score=score, results=results, total=len(CURRENT_EXAM))

@app.route("/check_question/<int:qid>", methods=["POST"])
def check_question(qid):
    """
    AJAX endpoint to check a single question.
    Expects form field 'answer'
    """
    global CURRENT_EXAM
    item = next((x for x in CURRENT_EXAM if x['id'] == qid), None)
    if not item:
        return jsonify({"error":"question not found"}), 404
    user_answer = request.form.get("answer","")
    res = check_answer(item, user_answer)
    return jsonify(res)

if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
