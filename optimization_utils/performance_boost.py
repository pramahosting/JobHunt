# ================================
# optimization_utils/performance_boost.py
# ================================
import streamlit as st
from job_scraper.job_scraper import get_all_jobs

@st.cache_data(ttl=3600)
def get_cached_jobs(*args, **kwargs):
    return get_all_jobs(*args, **kwargs)

@st.cache_data
def compute_ats_scores_batch(resume_text, jobs_df):
    from resume_matcher.match_resume import match_resume_to_jobs
    return match_resume_to_jobs(resume_text, jobs_df)

def export_to_excel_in_memory(df):
    from io import BytesIO
    import pandas as pd
    output = BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False, sheet_name='Matched Jobs')
    output.seek(0)
    return output.read()
