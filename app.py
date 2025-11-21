from flask import Flask, render_template, request
from model import extract_text, extract_skills, calculate_score

app = Flask(__name__)

@app.route("/", methods=["GET", "POST"])
def index():
    score = None
    skills_found = []
    missing_skills = []
    if request.method == "POST":
        file = request.files["resume"]
        jd = request.form["jd"]
        resume_text = extract_text(file)
        skills_found, missing_skills = extract_skills(resume_text, jd)
        score = calculate_score(resume_text, jd)
    return render_template("index.html", score=score, skills=skills_found, missing=missing_skills)

if __name__ == "__main__":
    app.run(debug=True)
