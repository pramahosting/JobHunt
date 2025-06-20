# ================================
# job_scraper/job_scraper.py
# ================================
import requests
import pandas as pd
import streamlit as st
import re
from datetime import datetime, timedelta

# --- Adzuna API credentials ---
ADZUNA_APP_ID = "638c0962"
ADZUNA_APP_KEY = "04681adc21daeda69c41b271627d448a"

# --- Classify Company Type ---
def classify_company_type(company_name: str) -> str:
    if not company_name or not isinstance(company_name, str):
        return "Unknown"

    name = company_name.lower()

    # Known agency/company name overrides
    known_agencies = [
        "michael page", "hays", "randstad", "adecco", "manpower", "robert half",
        "hudson", "kelly services", "peoplebank", "talent international", "aquent",
        "workpac", "drake", "programmed", "page personnel", "chandler macleod"
    ]
    known_consulting = [
        "accenture", "deloitte", "kpmg", "ey", "pwc", "capgemini", "cognizant",
        "infosys", "tcs", "ibm", "bain", "boston consulting group", "mckinsey"
    ]

    if any(agency in name for agency in known_agencies):
        return "Recruitment Agency"
    if any(consultant in name for consultant in known_consulting):
        return "Consulting Company"

    # Keyword-based fallback
    recruitment_keywords = [
        "recruitment", "staffing", "talent", "hiring", "headhunter", "search", "jobs", "placement", "resourcing"
    ]
    consulting_keywords = [
        "consulting", "consultants", "advisory", "strategy", "solutions", "analytics", "services"
    ]

    if any(word in name for word in recruitment_keywords):
        return "Recruitment Agency"
    elif any(word in name for word in consulting_keywords):
        return "Consulting Company"
    else:
        return "Business"

# --- Normalize Location to Main City ---
def normalize_location(location: str) -> str:
    if not location:
        return ""
    parts = location.split(",")
    return parts[-1].strip() if len(parts) > 1 else location.strip()

# --- Extract Key Requirements from Description ---
def extract_key_requirements(description):
    if not description:
        return ""

    bullet_points = re.findall(r"(?:-|\*|\•)\s?([^\n\r]+)", description)
    if bullet_points:
        return "; ".join(bullet_points[:5])

    lines = [line.strip() for line in description.split("\n") if line.strip()]
    return " ".join(lines[:3])

# --- Get Jobs from Adzuna API ---
def get_jobs_from_adzuna(role, location, job_type, salary_min, salary_max):
    base_url = "https://api.adzuna.com/v1/api/jobs/au/search/1"
    params = {
        "app_id": ADZUNA_APP_ID,
        "app_key": ADZUNA_APP_KEY,
        "results_per_page": 20,
        "what": role,
        "content-type": "application/json",
    }

    if location and location.lower() != "all":
        params["where"] = location

    if job_type and job_type.lower() != "all":
        params["full_time"] = "1" if job_type.lower() == "full-time" else "0"

    if salary_min:
        params["salary_min"] = salary_min

    if salary_max:
        params["salary_max"] = salary_max

    try:
        response = requests.get(base_url, params=params)
        response.raise_for_status()
        data = response.json()

        jobs = []
        today = datetime.utcnow()
        cutoff_date = today - timedelta(days=15)

        for job in data.get("results", []):
            created_str = job.get("created", "")[:10]
            try:
                created_date = datetime.strptime(created_str, "%Y-%m-%d")
            except:
                continue

            if created_date < cutoff_date:
                continue

            description = job.get("description", "")
            company_name = job.get("company", {}).get("display_name", "Unknown")
            raw_location = job.get("location", {}).get("display_name", location)

            jobs.append({
                "Job Title": job.get("title", "Unknown"),
                "Company": company_name,
                "Published": created_str,
                "Location": normalize_location(raw_location),
                "Job Type": job.get("contract_time", "N/A"),
                "Source": classify_company_type(company_name),
                "Description": description,
                "Requirements": extract_key_requirements(description),
                "Apply Link": job.get("redirect_url", "")
            })

        return jobs

    except Exception as e:
        st.error(f"❌ Adzuna API error: {e}")
        return []

# --- Remove Duplicate Jobs ---
def deduplicate_jobs(job_list):
    seen = set()
    unique_jobs = []
    for job in job_list:
        key = (job['Job Title'].lower(), job['Company'].lower(), job['Apply Link'])
        if key not in seen:
            seen.add(key)
            unique_jobs.append(job)
    return unique_jobs

# --- Get All Jobs ---
def get_all_jobs(role, location, industry, job_type, salary_min, salary_max):
    jobs = get_jobs_from_adzuna(role, location, job_type, salary_min, salary_max)
    deduped_jobs = deduplicate_jobs(jobs)
    return pd.DataFrame(deduped_jobs)
