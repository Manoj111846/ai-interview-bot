from flask import Flask, render_template, request
import PyPDF2
import random

app = Flask(__name__)

skills_db = [
"python","java","html","css","javascript","sql","machine learning"
]

questions_db = {

"python":[
"What is Python?",
"What are Python data types?",
"What is list comprehension?",
"What is lambda function?"
],

"java":[
"What is Java?",
"What is JVM?",
"What is OOP?",
"What is inheritance?"
],

"sql":[
"What is SQL?",
"What is normalization?",
"What is primary key?",
"What is join?"
],

"machine learning":[
"What is machine learning?",
"What is supervised learning?",
"What is overfitting?",
"What is neural network?"
]

}

detected_skills_global = []
generated_questions_global = []

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/upload")
def upload():
    return render_template("upload.html")

@app.route("/analyze", methods=["POST"])
def analyze():

    global detected_skills_global
    global generated_questions_global

    file = request.files["resume"]

    reader = PyPDF2.PdfReader(file)

    text = ""

    for page in reader.pages:
        text += page.extract_text()

    detected_skills = []

    for skill in skills_db:
        if skill in text.lower():
            detected_skills.append(skill)

    generated_questions = []

    for skill in detected_skills:
        if skill in questions_db:
            generated_questions.extend(questions_db[skill])

    generated_questions = random.sample(generated_questions, min(3, len(generated_questions)))

    detected_skills_global = detected_skills
    generated_questions_global = generated_questions

    return render_template("skills.html", skills=detected_skills)

@app.route("/start_interview")
def start_interview():

    return render_template(
        "interview.html",
        questions=generated_questions_global
    )

@app.route("/evaluate", methods=["POST"])
def evaluate():

    answers = request.form.getlist("answers")

    score = 0

    for ans in answers:
        if len(ans.strip()) > 5:
            score += 10

    total_questions = len(answers)

    strong_skills = []
    weak_skills = []

    if score >= 20:
        strong_skills = ["Python","SQL"]
        weak_skills = ["Machine Learning"]
    else:
        strong_skills = ["Basic Programming"]
        weak_skills = ["Python","Machine Learning"]

    feedback = "Practice weak skills to improve interview performance."

    return render_template(
        "dashboard.html",
        score=score,
        feedback=feedback,
        strong_skills=strong_skills,
        weak_skills=weak_skills,
        total_questions=total_questions
    )
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
    app.run(debug=True)