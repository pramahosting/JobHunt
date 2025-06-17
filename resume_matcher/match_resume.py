# ================================
# resume_matcher/match_resume.py
# ================================
from difflib import SequenceMatcher
import re

def clean_text(text):
    if not text:
        return ""
    return re.sub(r'\s+', ' ', text.lower().strip())

def compute_score(resume_text, job_description):
    resume_clean = clean_text(resume_text)
    job_clean = clean_text(job_description)
    return int(SequenceMatcher(None, resume_clean, job_clean).ratio() * 100)

def match_resume_to_jobs(resume_text, job_list):
    matched_jobs = []
    resume_clean = clean_text(resume_text)

    for job in job_list:
        job_desc = clean_text(job.get("description", ""))
        score = compute_score(resume_clean, job_desc)

        if score >= 50:  # Only include reasonable matches
            matched_jobs.append({
                "title": job.get("title"),
                "company": job.get("company"),
                "location": job.get("location"),
                "description": job.get("description"),
                "link": job.get("link"),
                "score": score
            })

    # Sort jobs by score descending
    return sorted(matched_jobs, key=lambda x: x["score"], reverse=True)

