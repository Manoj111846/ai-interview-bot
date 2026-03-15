from flask import Flask, render_template, request, redirect
import PyPDF2
import random
import sqlite3
import os

app=Flask(__name__)

skills_db=["python","java","sql"]

questions_db={

"python":[
"What is Python?",
"What is list?"
],

"java":[
"What is JVM?",
"What is OOP?"
],

"sql":[
"What is SQL?",
"What is primary key?"
]

}

detected_skills_global=[]
generated_questions_global=[]


def init_db():

    conn=sqlite3.connect("database.db")

    cursor=conn.cursor()

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


@app.route("/")
def home():

    return render_template("index.html")


@app.route("/login",methods=["GET","POST"])
def login():

    if request.method=="POST":

        return redirect("/upload")

    return render_template("login.html")


@app.route("/register",methods=["GET","POST"])
def register():

    if request.method=="POST":

        return redirect("/login")

    return render_template("register.html")


@app.route("/upload")
def upload():

    return render_template("upload.html")


@app.route("/analyze",methods=["POST"])
def analyze():

    global detected_skills_global
    global generated_questions_global

    file=request.files["resume"]

    reader=PyPDF2.PdfReader(file)

    text=""

    for page in reader.pages:

        if page.extract_text():

            text+=page.extract_text()

    text=text.lower()

    detected_skills=[]

    for skill in skills_db:

        if skill in text:

            detected_skills.append(skill)

    questions=[]

    for skill in detected_skills:

        if skill in questions_db:

            questions.extend(questions_db[skill])

    if len(questions)>3:

        questions=random.sample(questions,3)

    detected_skills_global=detected_skills
    generated_questions_global=questions

    return render_template("skills.html",skills=detected_skills)


@app.route("/start_interview")
def start_interview():

    return render_template("interview.html",questions=generated_questions_global)


@app.route("/evaluate",methods=["POST"])
def evaluate():

    answers=request.form.getlist("answers")

    score=0

    for ans in answers:

        if len(ans.strip())>5:

            score+=10

    total_questions=len(answers)

    conn=sqlite3.connect("database.db")

    cursor=conn.cursor()

    cursor.execute(
    "INSERT INTO results(score,total_questions) VALUES(?,?)",
    (score,total_questions)
    )

    conn.commit()

    conn.close()

    return render_template("dashboard.html",score=score,total_questions=total_questions)


@app.route("/history")
def history():

    conn=sqlite3.connect("database.db")

    cursor=conn.cursor()

    cursor.execute("SELECT * FROM results")

    data=cursor.fetchall()

    conn.close()

    return render_template("history.html",data=data)


if __name__=="__main__":

    port=int(os.environ.get("PORT",10000))

    app.run(host="0.0.0.0",port=port)