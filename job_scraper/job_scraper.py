# ================================
# job_scraper/job_scraper.py
# ================================
import requests
import pandas as pd  # ✅ ADDED: To convert job list to DataFrame

# Adzuna API credentials
ADZUNA_APP_ID = "638c0962"
ADZUNA_APP_KEY = "04681adc21daeda69c41b271627d448a"

# --- Get Jobs from Adzuna API ---
def get_jobs_from_adzuna(role, location, industry, job_type, salary_min, salary_max):
    base_url = "https://api.adzuna.com/v1/api/jobs/au/search/1"
    params = {
        "app_id": ADZUNA_APP_ID,
        "app_key": ADZUNA_APP_KEY,
        "results_per_page": 50,
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
        for job in data.get("results", []):
            jobs.append({
                "Job Title": job.get("title", "Unknown"),
                "Company": job.get("company", {}).get("display_name", "Unknown"),
                "Location": job.get("location", {}).get("display_name", location),
                "description": job.get("description", ""),
                "Score": 0,
                "Apply Link": job.get("redirect_url", ""),
                "Source": "Adzuna"
            })
        return jobs

    except Exception as e:
        print("Adzuna API error:", e)
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
    jobs = []
    jobs += get_jobs_from_adzuna(role, location, industry, job_type, salary_min, salary_max)
    deduped_jobs = deduplicate_jobs(jobs)

    # ✅✅✅ MODIFICATION: Convert to DataFrame before returning
    return pd.DataFrame(deduped_jobs)



