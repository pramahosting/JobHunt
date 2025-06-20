# ================================
# optimization_utils/performance_boost.py
# ================================

import time
import pandas as pd
from io import BytesIO
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import streamlit as st

# --- Caching job scraping ---
@st.cache_data(show_spinner=False)
def get_cached_jobs(get_all_jobs_func, *args, **kwargs):
    """Cache wrapper for job scraping."""
    return get_all_jobs_func(*args, **kwargs)

# --- Export Excel In-Memory ---
def export_to_excel_in_memory(df):
    """Exports DataFrame to Excel and returns bytes for download."""
    output = BytesIO()
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        df.to_excel(writer, index=False)
    output.seek(0)
    return output

# --- Fast ATS Scoring in Batch ---
def compute_ats_scores_batch(resume_text, job_descriptions):
    """Compute cosine similarity scores for multiple job descriptions."""
    texts = [resume_text] + job_descriptions
    vectorized = CountVectorizer().fit_transform(texts)
    resume_vec = vectorized[0]
    job_vecs = vectorized[1:]
    scores = cosine_similarity(resume_vec, job_vecs).flatten() * 100
    return [round(s, 1) for s in scores]

# --- Time Tracker ---
def log_duration(label):
    """Decorator to log duration of a function call."""
    def decorator(func):
        def wrapper(*args, **kwargs):
            start = time.time()
            result = func(*args, **kwargs)
            st.write(f"⏱️ {label} took {time.time() - start:.2f} seconds")
            return result
        return wrapper
    return decorator
