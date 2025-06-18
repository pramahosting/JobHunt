# ================================
# job_scraper/job_scraper.py
# ================================
import streamlit as st
import requests
import pandas as pd

# Your Adzuna API credentials
ADZUNA_APP_ID = "638c0962"
ADZUNA_APP_KEY = "04681adc21daeda69c41b271627d448a"

st.set_page_config(page_title="Australian Job Search", layout="centered")

st.title("🇦🇺 Australian Job Search Portal (Powered by Adzuna API)")

# Job search form
with st.form("job_search_form"):
    col1, col2 = st.columns(2)
    with col1:
        job_query = st.text_input("Role / Keywords", "Data Architect")
    with col2:
        location = st.selectbox(
            "Location",
            ["All", "Sydney", "Melbourne", "Brisbane", "Perth", "Adelaide", "Canberra", "Hobart", "Darwin"],
            index=0,
        )
    submitted = st.form_submit_button("🔍 Search Jobs")

if submitted:
    st.info("Searching jobs...")

    base_url = "https://api.adzuna.com/v1/api/jobs/au/search/1"
    params = {
        "app_id": ADZUNA_APP_ID,
        "app_key": ADZUNA_APP_KEY,
        "results_per_page": 20,
        "what": job_query,
        "content-type": "application/json",
    }
    if location != "All":
        params["where"] = location

    try:
        response = requests.get(base_url, params=params)
        response.raise_for_status()
        job_data = response.json()

        if job_data.get("results"):
            jobs = job_data["results"]
            df = pd.DataFrame(
                [
                    {
                        "Job Title": job.get("title"),
                        "Company": job.get("company", {}).get("display_name"),
                        "Published": job.get("created")[:10] if job.get("created") else "N/A",
                        "Location": job.get("location", {}).get("display_name"),
                        "Job Type": job.get("contract_time") or "N/A",
                        "Source": "Adzuna",
                        "Link": job.get("redirect_url"),
                    }
                    for job in jobs
                ]
            )
            st.success(f"✅ Found {len(df)} job(s)")
            st.dataframe(df)
        else:
            st.warning("❌ No jobs found. Try different keywords or location.")

    except Exception as e:
        st.error(f"❌ Failed to fetch jobs: {e}")
