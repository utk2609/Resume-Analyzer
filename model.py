import re
from sentence_transformers import SentenceTransformer, util
import spacy
import PyPDF2
from rapidfuzz import fuzz

nlp = spacy.load("en_core_web_md")
model = SentenceTransformer('all-MiniLM-L6-v2')

def clean_text(t):
    t = t or ""
    t = t.lower()
    t = re.sub(r'\S+@\S+', ' ', t)
    t = re.sub(r'https?:\/\/\S+', ' ', t)
    t = re.sub(r'\d{3,}', ' ', t)
    t = re.sub(r'[^a-zA-Z0-9\s\.\,]', ' ', t)
    t = re.sub(r'\s+', ' ', t).strip()
    return t

def extract_text(pdf):
    reader = PyPDF2.PdfReader(pdf)
    text = ""
    for p in reader.pages:
        page_text = p.extract_text() or ""
        text += " " + page_text
    return clean_text(text)

def load_skills(path="skills.txt"):
    skills = []
    with open(path, encoding="utf-8") as f:
        for line in f:
            s = line.strip()
            if s:
                skills.append(s.lower())
    return skills

def fuzzy_skill_detect(text, skills, threshold=78):
    found = []
    txt = text.lower()
    for sk in skills:
        score = fuzz.partial_ratio(sk, txt)
        if score >= threshold:
            found.append(sk)
            continue
        tokens = sk.split()
        for t in tokens:
            if fuzz.partial_ratio(t, txt) >= threshold:
                found.append(sk)
                break
    return sorted(list(set(found)))

def extract_skills(resume, jd):
    skills = load_skills()
    resume_clean = clean_text(resume)
    jd_clean = clean_text(jd)
    found_resume = fuzzy_skill_detect(resume_clean, skills)
    found_jd = fuzzy_skill_detect(jd_clean, skills)
    missing = [s for s in found_jd if s not in found_resume]
    return found_resume, missing

def embedding_score(text1, text2):
    t1 = clean_text(text1)
    t2 = clean_text(text2)
    if not t1 or not t2:
        return 0.0
    e1 = model.encode(t1, convert_to_tensor=True)
    e2 = model.encode(t2, convert_to_tensor=True)
    sim = util.cos_sim(e1, e2).item()
    return max(0.0, min(1.0, sim))

def calculate_score(resume, jd, weight_embed=0.75, weight_skills=0.25):
    embed = embedding_score(resume, jd)
    skills = load_skills()
    found_resume = fuzzy_skill_detect(resume, skills)
    found_jd = fuzzy_skill_detect(jd, skills)
    if len(found_jd) == 0:
        skill_ratio = 0.0
    else:
        overlap = len([s for s in found_jd if s in found_resume])
        skill_ratio = overlap / len(found_jd)
    combined = (weight_embed * embed) + (weight_skills * skill_ratio)
    return round(combined * 100, 2)
