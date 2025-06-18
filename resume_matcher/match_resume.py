# ================================
# resume_matcher/match_resume.py
# ================================
from difflib import SequenceMatcher
import re
import pandas as pd  # ✅ Added

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
        if not isinstance(job, dict):
            continue

        job_desc = clean_text(job.get("description", ""))
        score = compute_score(resume_clean, job_desc)

        if score >= 50:
            matched_jobs.append({
                "Job Title": job.get("Job Title") or job.get("title"),
                "Company": job.get("Company") or job.get("company"),
                "Location": job.get("Location") or job.get("location"),
                "description": job.get("description"),
                "link": job.get("Apply Link") or job.get("link"),
                "score": score
            })

    # ✅ Return as DataFrame
    return pd.DataFrame(sorted(matched_jobs, key=lambda x: x["score"], reverse=True))
