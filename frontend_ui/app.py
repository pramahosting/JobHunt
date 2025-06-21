# ================================
# frontend_ui/app.py (Streamlit UI)
# ================================
import sys
import os
import streamlit as st
import time
import html
import pandas as pd

# Set config first
st.set_page_config(layout="wide")

# === Title and CSS ===
st.markdown("""
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
    th, td {
        text-align: left !important;
        vertical-align: top !important;
        font-size: 12px !important;
    }
    th:nth-child(6), td:nth-child(6) {
        width: 20% !important;
    }
    th:nth-child(11), td:nth-child(11) {
        width: 28% !important;
    }
    </style>
    <div class="main-title">JobHunt Agent – Smart Job Search</div>
""", unsafe_allow_html=True)

st.subheader("Upload Resume")
uploaded_file = st.file_uploader("Upload", type=["pdf", "docx"], key="file_uploader", label_visibility="collapsed")

st.subheader("Enter Job Search Criteria")

col1, col2 = st.columns(2)
with col1:
    role = st.text_input("🎯 Target Role", placeholder="e.g., Data Architect", key="role")
with col2:
    location = st.selectbox("📍 Location", ["All", "Sydney", "Melbourne", "Brisbane", "Perth", "Adelaide", "Canberra", "Hobart", "Darwin"], key="location")

col3, col4 = st.columns(2)
with col3:
    industry = st.selectbox("🏠 Industry", ["All", "Banking and Financial Services", "Healthcare", "Technology", "Retail", "Government", "Manufacturing", "Mining", "Consulting"], key="industry")
with col4:
    job_type = st.selectbox("💼 Job Type", ["All", "Full-time", "Part-time", "Contract", "Temporary"], key="job_type")

col5, col6 = st.columns(2)
with col5:
    min_salary = st.number_input("💲 Min Salary", value=0, step=1000, key="min_salary")
with col6:
    max_salary = st.number_input("💲 Max Salary", value=200000, step=1000, key="max_salary")

col_run, col_reset = st.columns([1, 1])
with col_run:
    run_button = st.button("🚀 Run Agent")
with col_reset:
    reset_button = st.button("🔄 Reset")

if reset_button:
    st.session_state.clear()
    st.experimental_rerun()

if run_button:
    if not uploaded_file:
        st.warning("⚠️ Please upload your resume before running the agent.")
    elif not role:
        st.warning("⚠️ Please enter a target role before running the agent.")
    else:
        with st.spinner("🔍 Searching for matching jobs..."):
            import docx2txt
            import pdfplumber
            import fitz

            from job_scraper.job_scraper import get_all_jobs
            from resume_matcher.match_resume import match_resume_to_jobs
            from cover_letter_generator.cover_letter import generate_cover_letter
            from excel_exporter.export_excel import export_to_excel

            def extract_resume_text(file):
                if file.name.endswith(".docx"):
                    return docx2txt.process(file)
                elif file.name.endswith(".pdf"):
                    try:
                        with pdfplumber.open(file) as pdf:
                            return " ".join([page.extract_text() for page in pdf.pages if page.extract_text()])
                    except:
                        file.seek(0)
                        with fitz.open(stream=file.read(), filetype="pdf") as doc:
                            return " ".join([page.get_text() for page in doc])
                return ""

            resume_text = extract_resume_text(uploaded_file)
            jobs_df = pd.DataFrame(get_all_jobs(role, location, industry, job_type, min_salary, max_salary))

            if jobs_df.empty:
                st.warning("No jobs found. Please refine your criteria.")
            else:
                matched_jobs = match_resume_to_jobs(resume_text, jobs_df)

                # Format cover letter with first 5 lines visible, rest collapsible
                def format_cover_letter(text):
                    lines = text.split("\n")
                    visible = lines[:5]
                    hidden = lines[5:]
                    visible_html = "<div style='white-space: pre-wrap; font-family: Arial; font-size: 13px;'>" + "<br>".join(html.escape(line) for line in visible) + "</div>"
                    if hidden:
                        hidden_html = "<div style='white-space: pre-wrap; font-family: Arial; font-size: 13px; margin-top: 5px;'>" + "<br>".join(html.escape(line) for line in hidden) + "</div>"
                        return f"{visible_html}<details><summary>Show full letter</summary>{hidden_html}</details>"
                    return visible_html

                matched_jobs["Cover Letter"] = matched_jobs.apply(
                    lambda row: format_cover_letter(generate_cover_letter(resume_text, row.to_dict())), axis=1
                )

                # The Key Requirements, Resume Strengths, Improvement Areas, Summary are already bullet-formatted with capitals in match_resume.py, so display as HTML
                display_cols = [
                    "Job Title", "Company", "Location", "Date Published", "Published By",
                    "Key Requirements", "Score (ATS)", "Resume Strengths", "Improvement Areas",
                    "Summary", "Apply", "Cover Letter"
                ]
                display_cols = [col for col in display_cols if col in matched_jobs.columns]

                # Apply safe HTML render for bullet fields
                def safe_html(val):
                    if pd.isna(val):
                        return ""
                    return val.replace("\n", "<br>").replace("•", "&#8226;")  # Ensure bullets render nicely

                for col in ["Key Requirements", "Resume Strengths", "Improvement Areas", "Summary"]:
                    if col in matched_jobs.columns:
                        matched_jobs[col] = matched_jobs[col].apply(safe_html)

                # Prepare "Apply" column with clickable links
                matched_jobs["Apply"] = matched_jobs["Link"].apply(
                    lambda link: f'<a href="{link}" target="_blank" rel="noopener noreferrer">Apply</a>' if pd.notna(link) and str(link).startswith("http") else "-"
                )

                st.session_state.matched_jobs = matched_jobs
                st.session_state.excel_file = export_to_excel(matched_jobs)

if st.session_state.get("matched_jobs") is not None:
    df = st.session_state.matched_jobs

    col_msg, col_dl = st.columns([6, 1])
    with col_msg:
        st.success(f"✅ Found {len(df)} matching jobs!")
    with col_dl:
        st.download_button(
            label="📅 Download Excel",
            data=st.session_state.excel_file,
            file_name="JobMatches.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            key="download-excel"
        )

    st.markdown("### 📝 Matched Jobs")

    display_cols = [
        "Job Title", "Company", "Location", "Date Published", "Published By",
        "Key Requirements", "Score (ATS)", "Resume Strengths", "Improvement Areas",
        "Summary", "Apply", "Cover Letter"
    ]
    display_cols = [col for col in display_cols if col in df.columns]

    # Use st.write with unsafe_allow_html=True to render formatted bullets and links
    safe_df = df[display_cols].copy()

    # Escape text columns except those with HTML formatting
    html_cols = ["Key Requirements", "Resume Strengths", "Improvement Areas", "Summary", "Apply", "Cover Letter"]
    for col in safe_df.columns:
        if col not in html_cols:
            safe_df[col] = safe_df[col].astype(str).apply(lambda x: html.escape(x))

    st.write(safe_df.to_html(escape=False, index=False), unsafe_allow_html=True)
