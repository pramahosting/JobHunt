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

import mimetypes
import docx2txt
import pdfplumber
import fitz  # PyMuPDF
import pandas as pd

st.set_page_config(layout="wide")
st.markdown(
    """
    <style>
    .main-title {
        background-color: #007BFF;  /* Bootstrap Primary Blue */
        color: white;
        font-size: 28px;
        font-weight: 700;
        padding: 12px;
        border-radius: 6px;
        text-align: center;
        margin-top: -30px;  /* ⬅️ Reduce top space */
        margin-bottom: 15px;
    }
    </style>
    <div class="main-title">JobHunt Agent – Smart Job Search</div>
    """,
    unsafe_allow_html=True
)

# Draw a 2px thick horizontal line below the title
#st.markdown("""
#    <hr style="border:none; height:2px; background-color:#000000; margin-top:5px; margin-bottom:20px;">
#""", unsafe_allow_html=True)

# === Upload Resume (with uploader bar and messages) ===
st.subheader("Upload Resume")

# Reduce space between heading and uploader
st.markdown("<div style='margin-top: -25px;'></div>", unsafe_allow_html=True)

if "uploaded" not in st.session_state:
    st.session_state.uploaded = None

# Always show uploader bar with collapsed label to avoid extra space
uploaded_file = st.file_uploader(
    "Upload", 
    type=["pdf", "docx", "doc"], 
    key="file_uploader", 
    label_visibility="collapsed"
)

# === Reserve message space ===
message_container = st.empty()

# === Upload logic and message rendering ===
if uploaded_file:
    st.session_state.uploaded = uploaded_file
    with message_container.container():
        st.markdown(f"<b>{uploaded_file.name}</b><br><small>{round(uploaded_file.size / 1024, 1)}KB</small>", unsafe_allow_html=True)
        st.success("✅ Uploaded: " + uploaded_file.name)
elif st.session_state.uploaded:
    uploaded_file = st.session_state.uploaded
    with message_container.container():
        st.markdown(f"<b>{uploaded_file.name}</b><br><small>{round(uploaded_file.size / 1024, 1)}KB</small>", unsafe_allow_html=True)
        st.success("✅ Uploaded: " + uploaded_file.name)
else:
    # Pre-reserve blank space to prevent layout shift
    with message_container.container():
        st.markdown("<div style='height: 90px;'></div>", unsafe_allow_html=True)

# === Enter Search Criteria ===
st.subheader("Enter Job Search Criteria")
with st.container():
    col1, col2 = st.columns(2)
    with col1:
        role = st.text_input("🎯 Target Role", placeholder="e.g., Data Architect")

    with col2:
        locations = ["All", "Sydney", "Melbourne", "Brisbane", "Perth", "Adelaide", "Canberra", "Hobart", "Darwin"]
        location = st.selectbox("📍 Location", options=locations)

    col3, col4 = st.columns(2)
    with col3:
        industries = ["All", "Banking and Financial Services", "Healthcare", "Technology", "Retail", "Government", "Manufacturing", "Mining", "Consulting"]
        industry = st.selectbox("🏭 Industry", options=industries)

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

# === Custom CSS for Blue Run Agent Button ===
st.markdown("""
<style>
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
</style>
""", unsafe_allow_html=True)

# === Run Agent ===
run_button = st.button("🚀 Run Agent")

if run_button:
    if not uploaded_file:
        st.warning("Please upload your resume.")
    elif not role:
        st.warning("Please enter the target role.")
    else:
        with st.spinner("🔍 Searching for matching jobs..."):
            jobs = get_all_jobs(role, location, industry, job_type, min_salary, max_salary)

            if isinstance(jobs, list):
                if len(jobs) == 0:
                    st.warning("No jobs found. Please refine your criteria.")
                    st.stop()
                jobs = pd.DataFrame(jobs)

            if jobs.empty:
                st.warning("No jobs found. Please refine your criteria.")
                st.stop()

            matched_jobs = match_resume_to_jobs(resume_text, jobs)

            if matched_jobs.empty:
                st.warning("No matching jobs found.")
                st.stop()

            matched_jobs["Cover Letter"] = matched_jobs.apply(
                lambda row: generate_cover_letter(resume_text, row.get("description", "")), axis=1
            )

            excel_file = export_to_excel(matched_jobs)

            st.success(f"✅ Found {len(matched_jobs)} matching jobs!")
            st.download_button("📅 Download Excel Results", data=excel_file.getvalue(), file_name="JobMatches.xlsx")

            st.dataframe(
                matched_jobs[["Job Title", "Company", "Location", "Score", "Apply Link", "Cover Letter"]],
                use_container_width=True
            )

