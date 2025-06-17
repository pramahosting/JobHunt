# ================================
# frontend_ui/app.py (Streamlit UI)
# ================================
import streamlit as st
from job_scraper.job_scraper import get_all_jobs
from resume_matcher.match_resume import match_resume_to_jobs
from cover_letter_generator.cover_letter import generate_cover_letter
from excel_exporter.export_excel import export_to_excel

import docx2txt
import fitz  # PyMuPDF
import tempfile
import base64

st.set_page_config(page_title="JobIntel Agent", layout="wide")
st.title("💼 JobIntel Agent")

# Function to extract text from resume file
def extract_text_from_resume(uploaded_file, file_type):
    if file_type == "docx":
        try:
            return docx2txt.process(uploaded_file)
        except Exception:
            return "Could not read .docx file"

    elif file_type == "pdf":
        try:
            with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
                tmp_file.write(uploaded_file.read())
                tmp_file_path = tmp_file.name

            doc = fitz.open(tmp_file_path)
            text = ""
            for page in doc:
                text += page.get_text()
            return text
        except Exception:
            return "Could not read PDF file"

    elif file_type == "doc":
        return "Legacy .doc format not supported directly. Please convert to .docx"

    return "Unsupported format"

# Upload Resume Box
with st.container():
    st.header("📄 Upload Your Resume")
    uploaded_file = st.file_uploader("Upload your resume (.pdf or .docx)", type=["pdf", "docx"])
    pasted_resume = st.text_area("Or paste your resume text here")

resume_text = ""
if uploaded_file:
    file_type = uploaded_file.name.split(".")[-1].lower()
    resume_text = extract_text_from_resume(uploaded_file, file_type)
    if "Could not" in resume_text or "Unsupported" in resume_text:
        st.error(resume_text)
        resume_text = ""
    else:
        st.success("Resume uploaded and processed successfully.")
        st.text_area("Extracted Resume Text", resume_text, height=250)
elif pasted_resume:
    resume_text = pasted_resume
    st.success("Resume pasted and ready.")

# Job Search Criteria Box
with st.container():
    st.header("🎯 Job Search Criteria")
    role = st.text_input("Target Role", value="Business Analyst")
    location = st.text_input("Location", value="Sydney")
    domain = st.text_input("Industry/Domain", value="Banking and Financial Services")
    job_type = st.selectbox("Job Type", ["Any", "Full-time", "Part-time", "Contract"])
    salary_min = st.number_input("Minimum Salary", min_value=0, value=80000, step=1000)
    salary_max = st.number_input("Maximum Salary", min_value=0, value=200000, step=1000)

# Run Agent Button
if st.button("🚀 Run JobIntel Agent") and resume_text:
    with st.spinner("Scraping jobs and matching resume..."):
        job_list = get_all_jobs(role, location, domain, job_type, salary_min, salary_max)
        matched_jobs = match_resume_to_jobs(resume_text, job_list)

        if matched_jobs:
            # Generate cover letters
            for job in matched_jobs:
                job["cover_letter"] = generate_cover_letter(resume_text, job)

            # Export to Excel
            excel_file_path = export_to_excel(matched_jobs)
            excel_filename = excel_file_path.split("/")[-1]

            # Show download link
            with open(excel_file_path, "rb") as f:
                excel_data = f.read()
            b64 = base64.b64encode(excel_data).decode()
            href = f'<a href="data:application/octet-stream;base64,{b64}" download="{excel_filename}" style="font-size:18px;">📥 Download Excel Report</a>'
            st.markdown(href, unsafe_allow_html=True)

            # Show results
            st.subheader("📊 Matching Job Results")
            for job in matched_jobs:
                st.markdown(f"**{job['title']}** at *{job['company']}* - {job['location']}")
                st.markdown(f"✅ Match Score: **{job['score']}%**")
                st.markdown(f"📝 Cover Letter:\n{job['cover_letter']}")
                st.markdown(f"🔗 [Apply Here]({job['link']})", unsafe_allow_html=True)
                st.markdown("---")
        else:
            st.warning("No strong matches found.")
elif st.button("🚀 Run JobIntel Agent"):
    st.warning("Please upload or paste your resume first.")

