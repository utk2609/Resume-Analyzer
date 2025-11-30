from flask import Flask, render_template, request
from model import extract_text, extract_skills, calculate_score

app = Flask(__name__)

def score_status(score):
    try:
        s = float(score)
    except:
        return "Unknown"
    if s >= 75:
        return "Good"
    if s >= 50:
        return "Average"
    return "Needs Improvement"

@app.route("/", methods=["GET", "POST"])
def index():
    score = None
    skills_found = []
    missing_skills = []
    resume_preview = ""
    error = None
    if request.method == "POST":
        file = request.files.get("resume")
        jd = request.form.get("jd", "")
        if not file or file.filename == "":
            error = "Please upload a PDF resume."
        else:
            try:
                resume_text = extract_text(file)
                resume_preview = resume_text[:1500] + ("..." if len(resume_text) > 1500 else "")
                skills_found, missing_skills = extract_skills(resume_text, jd)
                score = calculate_score(resume_text, jd)
            except Exception as e:
                error = str(e)
    status = score_status(score) if score is not None else None
    return render_template("index.html", score=score, skills=skills_found, missing=missing_skills, status=status, preview=resume_preview, error=error)

if __name__ == "__main__":
    app.run(debug=True)
