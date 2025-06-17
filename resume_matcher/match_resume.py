# ================================
# resume_matcher/match_resume.py
# ================================
import re

def extract_keywords(text):
    soft_skills = ["communication", "collaboration", "leadership", "problem solving", "teamwork"]
    tools = ["excel", "tableau", "power bi", "sql", "python", "jira", "confluence"]
    experience_matches = re.findall(r"(\d+)\+?\s+years?", text.lower())
    return {
        "soft_skills": [s for s in soft_skills if s in text.lower()],
        "tools": [t for t in tools if t in text.lower()],
        "experience_years": sum(map(int, experience_matches)) if experience_matches else 0,
        "responsibilities": [line.strip() for line in text.split("\n") if any(word in line.lower() for word in ["led", "managed", "developed", "analyzed", "designed"])]
    }

def match_resume_to_job(resume_text, job):
    resume_features = extract_keywords(resume_text)
    job_features = extract_keywords(job.get("description", ""))

    match_score = 0
    total_weights = 0

    if resume_features['soft_skills'] and job_features['soft_skills']:
        common = set(resume_features['soft_skills']) & set(job_features['soft_skills'])
        match_score += len(common) * 10
        total_weights += 30

    if resume_features['tools'] and job_features['tools']:
        common = set(resume_features['tools']) & set(job_features['tools'])
        match_score += len(common) * 10
        total_weights += 30

    if resume_features['experience_years'] and job_features['experience_years']:
        years_match = min(resume_features['experience_years'], job_features['experience_years']) / max(resume_features['experience_years'], job_features['experience_years'])
        match_score += years_match * 20
        total_weights += 20

    if resume_features['responsibilities'] and job_features['responsibilities']:
        common = set(resume_features['responsibilities']) & set(job_features['responsibilities'])
        match_score += len(common) * 5
        total_weights += 20

    return round((match_score / total_weights) * 100) if total_weights else 0
