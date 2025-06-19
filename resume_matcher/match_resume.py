# ================================
# resume_matcher/match_resume.py
# ================================
from difflib import SequenceMatcher
import re
import pandas as pd
from collections import Counter

def clean_text(text):
    if not text:
        return ""
    return re.sub(r'\s+', ' ', text.lower().strip())

def extract_keywords(text):
    words = re.findall(r'\b[a-zA-Z]{3,}\b', text.lower())
    return Counter(words)

def compute_ats_score(resume_text, job_description):
    resume_keywords = extract_keywords(resume_text)
    job_keywords = extract_keywords(job_description)

    matched_keywords = set(resume_keywords.keys()) & set(job_keywords.keys())
    total_keywords = len(job_keywords)

    if total_keywords == 0:
        return 0, [], "N/A", "N/A"

    score = int((len(matched_keywords) / total_keywords) * 100)
    top_matches = sorted(matched_keywords, key=lambda x: job_keywords[x], reverse=True)[:5]
    missing_keywords = set(job_keywords.keys()) - set(resume_keywords.keys())
    improvement_tips = sorted(missing_keywords, key=lambda x: job_keywords[x], reverse=True)[:5]

    return score, top_matches, ", ".join(top_matches), ", ".join(improvement_tips)

def match_resume_to_jobs(resume_text, job_list):
    matched_jobs = []
    resume_clean = clean_text(resume_text)

    for job in job_list:
        if not isinstance(job, dict):
            continue

        job_desc = clean_text(job.get("description", ""))
        score, matched_keywords, match_summary, improvement_tips = compute_ats_score(resume_clean, job_desc)

        matched_jobs.append({
            "Job Title": job.get("Job Title") or job.get("title"),
            "Company": job.get("Company") or job.get("company"),
            "Location": job.get("Location") or job.get("location"),
            "description": job.get("description"),
            "Apply Link": job.get("Apply Link") or job.get("link"),
            "Score": score,
            "Matching Areas": match_summary,
            "Resume Strengths": f"{len(matched_keywords)} keyword(s) matched",
            "Improvement Tips": f"Consider including: {improvement_tips}"
        })

    return pd.DataFrame(sorted(matched_jobs, key=lambda x: x["Score"], reverse=True))


