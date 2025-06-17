# ================================
# excel_exporter/export_excel.py
# ================================
import pandas as pd

def export_jobs_to_excel(jobs, path="/mnt/data/job_results.xlsx"):
    df = pd.DataFrame(jobs)
    df.to_excel(path, index=False)
    return path