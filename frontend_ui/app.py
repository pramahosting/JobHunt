# ================================
# frontend_ui/app.py (Streamlit UI)
# ================================
import streamlit as st
import sys
import os
import io
from PyPDF2 import PdfReader
import docx2txt

# Add parent directory to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from job_scraper.job_scraper import get_all_jobs
from resume_matcher.match_resume import match_resume_to_jobs
from cover_letter_generator.cover_letter import generate_cover_letter
from excel_exporter.export_excel import export_to_excel

st.set_page_config(page_title="JobIntel Agent", layout="wide")

st.title("💼 JobIntel Agent")
st.markdown("AI-powered tool to find, match, and apply for jobs intelligently.")

# ---------------------- Resume Input Section ----------------------
with st.expander("📄 Resume Upload / Paste", expanded=True):
    resume_text = ""
    input_method = st.radio("Select Resume Input Method", ["Upload File", "Paste Text"], horizontal=True)

    if input_method == "Upload File":
        uploaded_file = st.file_uploader("Upload your resume (.pdf, .docx, .doc)", type=["pdf", "docx", "doc"])
        if uploaded_file:
            file_type = uploaded_file.type
            if file_type == "application/pdf":
                reader = PdfReader(uploaded_file)
                resume_text = "\n".join([page.extract_text() for page in reader.pages if page.extract_text()])
            elif file_type in ["application/vnd.openxmlformats-officedocument.wordprocessingml.document", "application/msword"]:
                resume_text = docx2txt.process(uploaded_file)
            else:
                st.warning("Unsupported file format.")
    else:
        resume_text = st.text_area("Paste your resume text here", height=300)

    if resume_text:
        st.success("✅ Resume loaded successfully!")

# ---------------------- Job Search Criteria Section ----------------------
with st.expander("🔍 Job Search Criteria", expanded=True):
    role = st.text_input("Role Title", value="Business Analyst")
    location = st.text_input("Location", value="Sydney")
    domain = st.text_input("Domain/Industry", value="Banking and Financial Services")
    job_type = st.selectbox("Job Type", ["", "Full-time", "Part-time", "Contract", "Temporary"])
    min_salary = st.number_input("Minimum Salary (AUD)", value=0)
    max_salary = st.number_input("Maximum Salary (AUD)", value=0)

# ---------------------- Run Agent Button ----------------------
if st.button("🚀 Run Agent"):
    if not resume_text.strip():
        st.error("Please provide your resume before proceeding.")
    else:
        with st.spinner("Scraping and analyzing jobs..."):
            all_jobs = get_all_jobs(
                role=role,
                location=location,
                domain=domain,
                job_type=job_type,
                min_salary=min_salary,
                max_salary=max_salary
            )

            matched_jobs = match_resume_to_jobs(resume_text, all_jobs)

            if not matched_jobs:
                st.warning("No matching jobs found.")
            else:
                st.success(f"✅ Found {len(matched_jobs)} matching jobs!")

                # Generate Cover Letters and Table
                export_data = []
                for i, job in enumerate(matched_jobs):
                    st.markdown(f"### 🏢 {job['title']} at {job['company']}")
                    st.markdown(f"- 📍 Location: {job['location']}")
                    st.markdown(f"- 📝 Score: **{job['score']}%**")
                    st.markdown(f"- 🔗 [Apply Now]({job['link']})")

                    cover_letter = generate_cover_letter(resume_text, job)
                    with st.expander("📄 Cover Letter"):
                        st.write(cover_letter)

                    export_data.append({
                        "Job Title": job['title'],
                        "Company": job['company'],
                        "Location": job['location'],
                        "Score": job['score'],
                        "Link": job['link'],
                        "Cover Letter": cover_letter
                    })

                # Export to Excel
                excel_file_path = export_to_excel(export_data)
                with open(excel_file_path, "rb") as f:
                    st.download_button(
                        label="📥 Download Job Matches (Excel)",
                        data=f,
                        file_name="job_matches.xlsx",
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                    )

