from flask import Flask, render_template, request, redirect, jsonify
import PyPDF2
import random
import sqlite3
import os
from gtts import gTTS
import cv2
import base64
import numpy as np

app = Flask(__name__)

# -----------------------------
# SKILL DATABASE
# -----------------------------
skills_db = ["python","java","sql","machine learning"]

questions_db = {
"python":[
{"q":"What is Python?","a":"python is a high level programming language"},
{"q":"What is lambda function?","a":"anonymous function"}
],
"java":[
{"q":"What is JVM?","a":"java virtual machine"},
{"q":"What is inheritance?","a":"one class inherits another"}
],
"sql":[
{"q":"What is SQL?","a":"structured query language"},
{"q":"What is primary key?","a":"unique identifier"}
],
"machine learning":[
{"q":"What is machine learning?","a":"machines learn from data"}
]
}

detected_skills_global = []
generated_questions_global = []

# -----------------------------
# DATABASE
# -----------------------------
def init_db():
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS results(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    score INTEGER,
    total_questions INTEGER
    )
    """)
    conn.commit()
    conn.close()

init_db()

# -----------------------------
# 🔥 INTRO PAGE (MUNDHUMATA)
# -----------------------------
@app.route("/")
def intro():
    return render_template("intro.html")   # NEW PAGE

# -----------------------------
# LOGIN
# -----------------------------
@app.route("/login",methods=["GET","POST"])
def login():
    if request.method=="POST":
        return redirect("/upload")
    return render_template("login.html")

# -----------------------------
# REGISTER
# -----------------------------
@app.route("/register",methods=["GET","POST"])
def register():
    if request.method=="POST":
        return redirect("/login")
    return render_template("register.html")

# -----------------------------
# UPLOAD PAGE (RESET DATA)
# -----------------------------
@app.route("/upload")
def upload():
    global detected_skills_global, generated_questions_global

    detected_skills_global = []
    generated_questions_global = []

    return render_template("upload.html")

# -----------------------------
# RESUME ANALYSIS
# -----------------------------
@app.route("/analyze",methods=["POST"])
def analyze():
    global detected_skills_global, generated_questions_global

    file = request.files["resume"]
    reader = PyPDF2.PdfReader(file)

    text = ""
    for page in reader.pages:
        try:
            if page.extract_text():
                text += page.extract_text()
        except:
            pass

    text = text.lower()

    detected_skills = []
    for skill in skills_db:
        if skill in text:
            detected_skills.append(skill)

    questions = []
    for skill in detected_skills:
        if skill in questions_db:
            questions.extend(questions_db[skill])

    if len(questions) > 3:
        questions = random.sample(questions, 3)

    detected_skills_global = detected_skills
    generated_questions_global = questions

    return render_template("skills.html", skills=detected_skills)

# -----------------------------
# START INTERVIEW
# -----------------------------
@app.route("/start_interview")
def start_interview():
    q_list = [q["q"] for q in generated_questions_global]
    return render_template("interview.html", questions=q_list)

# -----------------------------
# CHECK ANSWER (LIVE FEEDBACK)
# -----------------------------
@app.route("/check_answer",methods=["POST"])
def check_answer():
    data = request.json
    index = data["index"]
    user_answer = data["answer"].lower()

    correct = generated_questions_global[index]["a"]

    correct_words = correct.split()
    user_words = user_answer.split()

    missing = [w for w in correct_words if w not in user_words]
    wrong = [w for w in user_words if w not in correct_words]

    result = ""
    if not missing and not wrong:
        result = "✅ Perfect Answer"
    else:
        result = "❌ Mistakes detected\n"
        if missing:
            result += "Missing: " + ", ".join(missing) + "\n"
        if wrong:
            result += "Wrong: " + ", ".join(wrong) + "\n"

    result += "\n✔ Correct Answer: " + correct

    return jsonify({"feedback": result})

# -----------------------------
# FINAL EVALUATION
# -----------------------------
@app.route("/evaluate",methods=["POST"])
def evaluate():

    answers = request.form.getlist("answers")

    score = 0
    for i, ans in enumerate(answers):
        correct = generated_questions_global[i]["a"]
        if correct in ans.lower():
            score += 10

    total_questions = len(answers)

    strong_skills = detected_skills_global if score >= 20 else []
    weak_skills = detected_skills_global if score < 20 else []

    # SAVE RESULT
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO results(score,total_questions) VALUES(?,?)",
        (score, total_questions)
    )
    conn.commit()
    conn.close()

    # FEEDBACK
    feedback = "Good job" if score >= 20 else "Practice more"

    if not os.path.exists("static"):
        os.makedirs("static")

    tts = gTTS(feedback)
    tts.save("static/feedback.mp3")

    return render_template("dashboard.html",
                           score=score,
                           total_questions=total_questions,
                           strong_skills=strong_skills,
                           weak_skills=weak_skills,
                           detected_skills=detected_skills_global)

# -----------------------------
# RUN
# -----------------------------
import os

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))  # Render gives PORT
    app.run(host="0.0.0.0", port=port)