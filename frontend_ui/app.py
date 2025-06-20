# ================================
# frontend_ui/app.py (Streamlit UI)
# ================================
import sys
import os
import streamlit as st
import time
import html

# Set config first
st.set_page_config(layout="wide")

# Timing start
#start_time = time.time()

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
        width: 20% !important;  /* Reduced width of Key Requirements column */
    }
    th:nth-child(11), td:nth-child(11) {
        width: 28% !important;  /* Slightly wider Cover Letter column */
    }
    </style>
    <div class="main-title">JobHunt Agent – Smart Job Search</div>
""", unsafe_allow_html=True)

# === Upload Section ===
st.subheader("Upload Resume")
uploaded_file = st.file_uploader("Upload", type=["pdf", "docx"], key="file_uploader", label_visibility="collapsed")

# === Job Search Criteria ===
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

# === Run & Reset Buttons ===
col_run, col_reset = st.columns([1, 1])
with col_run:
    run_button = st.button("🚀 Run Agent")
with col_reset:
    reset_button = st.button("🔄 Reset")

if reset_button:
    uploaded_file = None
    st.session_state.clear()
    st.rerun()

# === Conditional Processing Only After Run ===
if run_button:
    with st.spinner("🔍 Searching for matching jobs..."):
        import pandas as pd
        import docx2txt
        import pdfplumber
        import fitz  # PyMuPDF

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

            def format_key_requirements(text):
                items = [i.strip().capitalize() for i in text.replace("\n", ",").split(",") if i.strip()]
                visible = items[:3]
                hidden = items[3:]
                visible_html = "<ul>" + "".join(f"<li>{html.escape(i)}</li>" for i in visible) + "</ul>"
                if hidden:
                    hidden_html = "<ul>" + "".join(f"<li>{html.escape(i)}</li>" for i in hidden) + "</ul>"
                    return f"{visible_html}<details><summary>Show more</summary>{hidden_html}</details>"
                return visible_html

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
            matched_jobs["Key Requirements"] = matched_jobs["Key Requirements"].apply(format_key_requirements)
            matched_jobs["Apply"] = matched_jobs["Link"].apply(
                lambda link: f'<a href="{link}" target="_blank">Apply</a>' if pd.notna(link) and str(link).startswith("http") else "-"
            )

            st.session_state.matched_jobs = matched_jobs
            st.session_state.excel_file = export_to_excel(matched_jobs)

# === Display Results ===
if st.session_state.get("matched_jobs") is not None:
    df = st.session_state.matched_jobs

    col_msg, col_dl = st.columns([6, 1])
    with col_msg:
        st.success(f"✅ Found {len(df)} matching jobs!")
    with col_dl:
        st.download_button(
            label="📥 Download Excel",
            data=st.session_state.excel_file,
            file_name="JobMatches.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            key="download-excel"
        )
    st.markdown("### 📝 Matched Jobs")

    display_cols = ["Job Title", "Company", "Location", "Date Published", "Published By", "Key Requirements",
                    "Score (ATS)", "Resume Strengths", "Improvement Areas", "Apply", "Cover Letter"]
    display_cols = [col for col in display_cols if col in df.columns]

    safe_df = df[display_cols].applymap(lambda x: str(x).encode('ascii', 'ignore').decode('ascii') if pd.notna(x) else "")
    st.write(safe_df.to_html(escape=False, index=False), unsafe_allow_html=True)

# Final load timing
#st.write("\n---")
#st.write(f"✅ Total Page Load Time (seconds): {round(time.time() - start_time, 3)}")





