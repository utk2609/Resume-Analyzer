import spacy
import PyPDF2
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

nlp = spacy.load("en_core_web_sm")

def extract_text(pdf):
    reader = PyPDF2.PdfReader(pdf)
    text = ""
    for page in reader.pages:
        text += page.extract_text()
    return text.lower()

def extract_skills(resume, jd):
    skills = open("skills.txt").read().splitlines()
    found = [s for s in skills if s.lower() in resume]
    missing = [s for s in skills if s.lower() in jd.lower() and s not in found]
    return found, missing

def calculate_score(resume, jd):
    docs = [resume, jd]
    tf = TfidfVectorizer().fit_transform(docs)
    return round(cosine_similarity(tf[0:1], tf[1:2])[0][0] * 100, 2)
