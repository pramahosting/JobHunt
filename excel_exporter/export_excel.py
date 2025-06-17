# ================================
# excel_exporter/export_excel.py
# ================================
import pandas as pd
import os
from datetime import datetime

def export_to_excel(job_data, filename_prefix="job_matches"):
    df = pd.DataFrame(job_data)

    # Define default path
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{filename_prefix}_{timestamp}.xlsx"
    filepath = os.path.join("frontend_ui", filename)

    # Save to Excel
    df.to_excel(filepath, index=False)
    return filepath
