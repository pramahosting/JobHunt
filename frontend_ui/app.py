# ================================
# frontend_ui/app.py (Streamlit UI)
# ================================
import sys
import os

# Add parent directory to Python path so modules can be found
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import streamlit as st
from job_scraper.job_scraper import get_all_jobs
from resume_matcher.match_resume import match_resume_to_job
from cover_letter_generator.cover_letter import generate_cover_letter
from excel_exporter.export_excel import export_jobs_to_excel

st.title("JobIntel Agent – Smart Job Finder")

uploaded_resume = st.file_uploader("Upload Resume (txt)", type=["txt"])
role = st.text_input("Target Role", "Business Analyst")
location = st.text_input("Location", "Sydney")
industry = st.text_input("Industry", "Banking and Financial Services")
job_type = st.selectbox("Job Type", ["", "Fulltime", "Contract", "Parttime"])
salary_min = st.number_input("Min Salary (AUD)", value=0)
salary_max = st.number_input("Max Salary (AUD)", value=200000)

if st.button("Find Jobs") and uploaded_resume:
    resume_text = uploaded_resume.read().decode("utf-8")
    jobs = get_all_jobs(role, location, industry, job_type, salary_min, salary_max)

    for job in jobs:
        job['match_score'] = match_resume_to_job(resume_text, job)
        job['cover_letter'] = generate_cover_letter(resume_text, job)

    excel_path = export_jobs_to_excel(jobs)
    st.download_button("📥 Download Excel", open(excel_path, "rb"), "job_results.xlsx")

    for job in jobs:
        st.markdown(f"### {job['title']} at {job['company']}")
        st.markdown(f"**Location:** {job['location']}")
        st.markdown(f"**Match Score:** {job['match_score']}%")
        st.markdown(f"[Apply Here]({job['link']})")
        with st.expander("Cover Letter"):
            st.text(job['cover_letter'])
else:
    st.info("Upload resume and click 'Find Jobs'")
