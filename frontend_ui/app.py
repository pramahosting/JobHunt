# ================================
# frontend_ui/app.py (Streamlit UI)
# ================================
# frontend_ui/app.py

import streamlit as st
from job_scraper.job_scraper import get_all_jobs
from resume_matcher.match_resume import match_resume_to_jobs
from cover_letter_generator.cover_letter import generate_cover_letter
from excel_exporter.export_excel import export_to_excel

import os
import mimetypes
import docx2txt
import pdfplumber
import fitz  # PyMuPDF
import pandas as pd

st.set_page_config(layout="wide")
st.title("📌 JobIntel Agent – Smart Resume Matcher")

# --- Upload Resume ---
with st.container():
    st.subheader("📄 Upload Resume")
    uploaded_file = st.file_uploader("Upload your resume (.pdf, .docx)", type=["pdf", "docx", "doc"])
    if uploaded_file:
        st.markdown(f"✅ Uploaded: **{uploaded_file.name}**")

# --- Enter Search Criteria ---
with st.container():
    st.subheader("🔍 Enter Search Criteria")

    col1, col2 = st.columns(2)
    with col1:
        role = st.text_input("🎯 Target Role", placeholder="e.g., Data Architect")

    with col2:
        locations = ["All", "Sydney", "Melbourne", "Brisbane", "Perth", "Adelaide", "Canberra", "Hobart", "Darwin"]
        location = st.selectbox("📍 Location", options=locations)

    col3, col4 = st.columns(2)
    with col3:
        industries = ["All", "Banking and Financial Services", "Healthcare", "Technology", "Retail", "Government"]
        industry = st.selectbox("🏭 Industry", options=industries)

    with col4:
        job_type = st.selectbox("💼 Job Type", ["All", "Full-time", "Part-time", "Contract", "Temporary"])

    col5, col6 = st.columns(2)
    with col5:
        min_salary = st.number_input("💲 Min Salary", value=0, step=1000)
    with col6:
        max_salary = st.number_input("💲 Max Salary", value=200000, step=1000)

# --- Extract Resume Text ---
def extract_resume_text(uploaded_file):
    if uploaded_file:
        mime_type, _ = mimetypes.guess_type(uploaded_file.name)
        if uploaded_file.name.endswith(".docx") or uploaded_file.name.endswith(".doc"):
            try:
                return docx2txt.process(uploaded_file)
            except Exception:
                return ""
        elif uploaded_file.name.endswith(".pdf"):
            try:
                with pdfplumber.open(uploaded_file) as pdf:
                    return " ".join([page.extract_text() for page in pdf.pages if page.extract_text()])
            except Exception:
                try:
                    with fitz.open(stream=uploaded_file.read(), filetype="pdf") as doc:
                        return " ".join(page.get_text() for page in doc)
                except Exception:
                    return ""
    return ""

resume_text = extract_resume_text(uploaded_file)

# --- Run Agent ---
if st.button("🚀 Run JobIntel Agent") and resume_text and role:
    with st.spinner("🔍 Searching for matching jobs..."):
        jobs = get_all_jobs(role, location, industry, job_type, min_salary, max_salary)

        if not jobs:
            st.warning("No jobs found. Please refine your criteria.")
        else:
            matched_jobs = match_resume_to_jobs(resume_text, jobs)
            matched_jobs["Cover Letter"] = matched_jobs.apply(
                lambda row: generate_cover_letter(resume_text, row.get("description", "")), axis=1
            )

            excel_file = export_to_excel(matched_jobs)

            # --- Display Results ---
            st.success(f"✅ Found {len(matched_jobs)} matching jobs!")
            st.download_button("📥 Download Excel Results", data=excel_file.getvalue(), file_name="JobMatches.xlsx")

            st.dataframe(matched_jobs[["Job Title", "Company", "Location", "Score", "Apply Link", "Cover Letter"]],
                         use_container_width=True)
else:
    st.info("Please upload your resume and enter the target role to proceed.")

