# ================================
# frontend_ui/app.py (Streamlit UI)
# ================================
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import streamlit as st
from job_scraper.job_scraper import get_all_jobs
from resume_matcher.match_resume import match_resume_to_jobs
from cover_letter_generator.cover_letter import generate_cover_letter
from excel_exporter.export_excel import export_to_excel
from optimization_utils.performance_boost import (
    get_cached_jobs,
    compute_ats_scores_batch,
    export_to_excel_in_memory
)
from streamlit.runtime.scriptrunner import RerunException

import mimetypes
import docx2txt
import pdfplumber
import fitz  # PyMuPDF
import pandas as pd

# Page config
st.set_page_config(layout="wide")

st.markdown(
    """
    <style>
    .main-title {
        background-color: #007BFF;
        color: white;
        font-size: 28px;
        font-weight: 500;
        padding: 10px;
        border-radius: 6px;
        text-align: center;
        margin-top: -35px;
        margin-bottom: 10px;
    }
    .button-container {
        display: flex;
        justify-content: space-between;
        margin-bottom: 1em;
    }
    .download-container {
        display: flex;
        justify-content: flex-end;
        margin-top: 1em;
    }
    .excel-button {
        background-color: white;
        color: black;
        font-weight: 600;
        padding: 10px 20px;
        border-radius: 6px;
        text-decoration: none;
        border: 1px solid #ccc;
    }
    div.stButton > button:first-child {
        background-color: #007BFF;
        color: white;
        height: 3em;
        width: 12em;
        border-radius: 6px;
        font-weight: 600;
    }
    div.stButton > button:first-child:hover {
        background-color: #0056b3;
        color: white;
    }
    th {
        text-align: left !important;
    }
    .cover-letter-cell {
        max-height: 200px;
        overflow-y: auto;
        padding: 8px;
        background-color: #fcfcfc;
        border: 1px solid #eee;
    }

</style>
 <div class="main-title">JobHunt Agent – Smart Job Search</div>
""", unsafe_allow_html=True)

if "uploaded" not in st.session_state:
    st.session_state.uploaded = None
if "matched_jobs" not in st.session_state:
    st.session_state.matched_jobs = None

# === Upload Resume Section ===
st.subheader("Upload Resume")
st.markdown("<div style='margin-top: -75px;'></div>", unsafe_allow_html=True)

uploaded_file = st.file_uploader(
    "Upload",
    type=["pdf", "docx"],
    key="file_uploader",
    label_visibility="collapsed"
)

# Reserve stable container for upload messages with fixed height
upload_message_container = st.empty()
upload_message_height = 100  # in px, adjust as needed

if uploaded_file:
    st.session_state.uploaded = uploaded_file
    with upload_message_container.container():
        st.success("✅ Uploaded: " + uploaded_file.name)
else:
    # Reserve fixed vertical space to avoid layout jump when no message
    upload_message_container.markdown(f"<div style='height: {upload_message_height}px;'></div>", unsafe_allow_html=True)

# === Enter Search Criteria ===
st.subheader("Enter Search Criteria")

col1, col2 = st.columns(2)
with col1:
    role = st.text_input("🎯 Target Role", placeholder="e.g., Data Architect", key="role")
with col2:
    locations = ["All", "Sydney", "Melbourne", "Brisbane", "Perth", "Adelaide", "Canberra", "Hobart", "Darwin"]
    location = st.selectbox("📍 Location", locations, key="location")

col3, col4 = st.columns(2)
with col3:
    industries = ["All", "Banking and Financial Services", "Healthcare", "Technology", "Retail", "Government", "Manufacturing", "Mining", "Consulting"]
    industry = st.selectbox("🏠 Industry", industries, key="industry")
with col4:
    job_type = st.selectbox("💼 Job Type", ["All", "Full-time", "Part-time", "Contract", "Temporary"])

col5, col6 = st.columns(2)
with col5:
    min_salary = st.number_input("💲 Min Salary", value=0, step=1000)
with col6:
    max_salary = st.number_input("💲 Max Salary", value=200000, step=1000)

# === Extract Resume Text ===
def extract_resume_text(uploaded_file):
    if uploaded_file:
        if uploaded_file.name.endswith((".docx", ".doc")):
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

# === Run & Reset Buttons ===
col_run, col_reset = st.columns([1, 1])
with col_run:
    run_button = st.button("🚀 Run Agent")
with col_reset:
    reset_button = st.button("🔄 Reset")

def reset_all():
    for key in ["uploaded", "matched_jobs", "role", "location", "industry", "job_type", "min_salary", "max_salary"]:
        if key in st.session_state:
            del st.session_state[key]

def rerun():
    sys.exit("Rerun")

if reset_button:
    # Clear session state
    for key in st.session_state.keys():
        del st.session_state[key]
    rerun()

if run_button:
    if not uploaded_file:
        st.warning("Please upload your resume.")
    elif not role:
        st.warning("Please enter the target role.")
    else:
        with st.spinner("🔍 Searching for matching jobs..."):
            jobs = get_all_jobs(role, location, industry, job_type, min_salary, max_salary)
            if isinstance(jobs, list):
                jobs = pd.DataFrame(jobs)
            if jobs.empty:
                st.warning("No jobs found. Please refine your criteria.")
                st.stop()

            matched_jobs = match_resume_to_jobs(resume_text, jobs)

            if matched_jobs.empty:
                st.warning("No matching jobs found.")
                st.stop()

            if isinstance(matched_jobs, list):
                matched_jobs = pd.DataFrame(matched_jobs)

            matched_jobs["Cover Letter"] = matched_jobs.apply(
                lambda row: "<div class='cover-letter-cell'><div style='white-space: pre-wrap; font-family: Arial; font-size: 13px;'>" +
                            generate_cover_letter(resume_text, row.to_dict()).replace("\n", "<br>") +
                            "</div></div>",
                axis=1
            )

            st.session_state.matched_jobs = matched_jobs
            st.session_state.excel_file = export_to_excel(matched_jobs)

# === Display Matched Jobs ===
if st.session_state.matched_jobs is not None:
    matched_jobs = st.session_state.matched_jobs

    col_msg, col_dl = st.columns([5, 1])
    with col_msg:
        st.success(f"✅ Found {len(matched_jobs)} matching jobs!")
    with col_dl:
        if st.session_state.get("excel_file") is not None:
            st.download_button(
                label="📅 Download Excel",
                data=st.session_state.excel_file,
                file_name="JobMatches.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                key="download-excel",
                help="Download matched jobs in Excel format"
            )

    if "Link" in matched_jobs.columns and matched_jobs["Link"].notna().any():
        matched_jobs["Link"] = matched_jobs["Link"]
    elif "Apply Link" in matched_jobs.columns:
        matched_jobs["Link"] = matched_jobs["Apply Link"]
    else:
        matched_jobs["Link"] = "-"

    matched_jobs["Apply"] = matched_jobs["Link"].apply(
        lambda link: f'<a href="{link}" target="_blank">Apply</a>' if pd.notna(link) and str(link).startswith("http") else "-"
    )

    st.markdown("### 📝 Matched Jobs")

    columns_to_show = [col for col in [
        "Job Title", "Company", "Location", "Date Published", "Published By", "Key Requirements", "Score (ATS)", "Resume Strengths", "Improvement Areas", "Apply", "Cover Letter"
    ] if col in matched_jobs.columns]

    def clean_for_html(df):
        return df.applymap(lambda x: str(x).encode('ascii', 'ignore').decode('ascii') if pd.notna(x) else "")

    cleaned_matched_jobs = clean_for_html(matched_jobs[columns_to_show])
    st.write(cleaned_matched_jobs.to_html(escape=False, index=False), unsafe_allow_html=True)




