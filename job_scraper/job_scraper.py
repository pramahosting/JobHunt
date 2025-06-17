# ================================
# job_scraper/job_scraper.py
# ================================
import requests
from bs4 import BeautifulSoup

BROWSE_AI_API_KEY = "c3f0520f-7cae-43cb-b7ec-73dc6757c085:5b83d934-3682-417e-ab28-da85cb3ff151"
SCRAPER_API_KEY = "0d986fc52b25c0447a11c22ead6237dc"

def get_jobs_from_scraperapi(role, location, industry, job_type, salary_min, salary_max):
    query = role.replace(" ", "+")
    location_query = "" if location.lower() == "anywhere in australia" else location
    base_url = f"https://au.indeed.com/jobs?q={query}&l={location_query}"

    if industry.lower() != "all industry":
        base_url += f"&ind={industry.replace(' ', '+')}"
    if job_type:
        base_url += f"&jt={job_type.lower()}"
    if salary_min:
        base_url += f"&salary={salary_min}"
    if salary_max:
        base_url += f"&salary_max={salary_max}"

    proxy_url = f"http://api.scraperapi.com?api_key={SCRAPER_API_KEY}&url={base_url}"
    try:
        response = requests.get(proxy_url)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")
        cards = soup.select("a.tapItem")
        jobs = []
        for card in cards[:15]:
            title = card.select_one("h2.jobTitle span")
            company = card.select_one("span.companyName")
            location_elem = card.select_one("div.companyLocation")
            job = {
                "title": title.text.strip() if title else "Unknown",
                "company": company.text.strip() if company else "Unknown",
                "location": location_elem.text.strip() if location_elem else location,
                "description": "",
                "link": "https://au.indeed.com" + card.get("href"),
                "requirements": []
            }
            jobs.append(job)
        return jobs
    except Exception as e:
        print("ScraperAPI error:", e)
        return []

def get_jobs_from_browse_ai(role, location):
    return []  # Stub (Replace with real Browse AI robot logic)

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
    jobs += get_jobs_from_scraperapi(role, location, industry, job_type, salary_min, salary_max)
    jobs += get_jobs_from_browse_ai(role, location)
    return deduplicate_jobs(jobs)