# ================================
# job_scraper/job_scraper.py
# ================================
import requests

# Adzuna API credentials
ADZUNA_APP_ID = "638c0962"
ADZUNA_APP_KEY = "04681adc21daeda69c41b271627d448a"

def get_jobs_from_adzuna(role, location, industry, job_type, salary_min, salary_max):
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
        for job in data.get("results", []):
            jobs.append({
                "title": job.get("title", "Unknown"),
                "company": job.get("company", {}).get("display_name", "Unknown"),
                "location": job.get("location", {}).get("display_name", location),
                "description": job.get("description", ""),
                "link": job.get("redirect_url", ""),
                "requirements": [],  # Not directly available from Adzuna API
                "source": "Adzuna"
            })
        return jobs

    except Exception as e:
        print("Adzuna API error:", e)
        return []

def deduplicate_jobs(job_list):
    seen = set()
    unique_jobs = []
    for job in job_list:
        key = (job['title'].lower(), job['company'].lower(), job['link'])
        if key not in seen:
            seen.add(key)
            unique_jobs.append(job)
    return unique_jobs

def get_all_jobs(role, location, industry, job_type, salary_min, salary_max):
    jobs = []
    jobs += get_jobs_from_adzuna(role, location, industry, job_type, salary_min, salary_max)
    return deduplicate_jobs(jobs)

