# ================================
# resume_matcher/match_resume.py (Updated)
# ================================
import re
import pandas as pd
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# Define keyword categories
BUSINESS_KEYWORDS = ["strategy", "risk", "stakeholder", "budget", "revenue", "regulatory", "policy", "compliance"]
FUNCTIONAL_KEYWORDS = ["reporting", "analytics", "planning", "modeling", "forecasting", "dashboard", "visualization"]
TECHNICAL_KEYWORDS = ["python", "sql", "azure", "aws", "gcp", "tableau", "powerbi", "etl", "datawarehouse", "airflow"]

def clean_and_tokenize(text):
    text = re.sub(r"[^a-zA-Z0-9 ]", " ", text)
    tokens = list(set([w.strip().lower() for w in text.split() if len(w.strip()) > 2]))
    return tokens

def classify_keywords(tokens):
    business = [t for t in tokens if t in BUSINESS_KEYWORDS]
    functional = [t for t in tokens if t in FUNCTIONAL_KEYWORDS]
    technical = [t for t in tokens if t in TECHNICAL_KEYWORDS]
    return business, functional, technical

def extract_features(text):
    tokens = clean_and_tokenize(text)
    return classify_keywords(tokens)

def compute_ats_score(resume_text, job_desc):
    vectorizer = CountVectorizer().fit_transform([resume_text, job_desc])
    score = cosine_similarity(vectorizer[0:1], vectorizer[1:2])[0][0] * 100
    return round(score, 1)

def match_resume_to_jobs(resume_text, job_list):
    matched_jobs = []

    for job in job_list:
        job_desc = job.get("description", "")
        score = compute_ats_score(resume_text, job_desc)

        # Extract features
        resume_b, resume_f, resume_t = extract_features(resume_text)
        job_b, job_f, job_t = extract_features(job_desc)

        # Matched and missing
        matched_b = set(resume_b) & set(job_b)
        matched_f = set(resume_f) & set(job_f)
        matched_t = set(resume_t) & set(job_t)

        missing_b = set(job_b) - set(resume_b)
        missing_f = set(job_f) - set(resume_f)
        missing_t = set(job_t) - set(resume_t)

        # Generate brief insights
        strengths = []
        if matched_b: strengths.append(f"Business: {', '.join(matched_b)}")
        if matched_f: strengths.append(f"Functional: {', '.join(matched_f)}")
        if matched_t: strengths.append(f"Technical: {', '.join(matched_t)}")

        improvements = []
        if missing_b: improvements.append(f"Lack of business exposure in {', '.join(missing_b)}")
        if missing_f: improvements.append(f"Improve functional skills like {', '.join(missing_f)}")
        if missing_t: improvements.append(f"Missing technical tools: {', '.join(missing_t)}")

        matched_jobs.append({
            "Job Title": job.get("Job Title") or job.get("title"),
            "Company": job.get("Company") or job.get("company"),
            "Location": job.get("Location") or job.get("location"),
            "Score (ATS)": score,
            "Strengths": "; ".join(strengths),
            "Improvement Areas": "; ".join(improvements),
            "Apply Link": job.get("Apply Link") or job.get("link")
        })

    return pd.DataFrame(sorted(matched_jobs, key=lambda x: x["Score (ATS)"], reverse=True))
