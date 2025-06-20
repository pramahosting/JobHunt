# ================================
# excel_exporter/export_excel.py
# ================================
import pandas as pd
from io import BytesIO

def export_to_excel(job_data):
    df = pd.DataFrame(job_data)
    output = BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False)
    output.seek(0)
    return output

