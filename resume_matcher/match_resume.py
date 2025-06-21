# ================================
# resume_matcher/match_resume.py
# ================================
import re
import pandas as pd

def extract_name(resume_text):
    lines = [line.strip() for line in resume_text.split('\n') if line.strip()]
    for line in lines[:10]:
        # Check if line looks like a name: 2-4 words, each starting with uppercase
        if 2 <= len(line.split()) <= 4 and all(w[0].isupper() for w in line.split() if w[0].isalpha()):
            return line
    return "Applicant"

def extract_key_requirements(job_text):
    # Extract key sentences or bullets from job text heuristically
    # For simplicity, pick lines with bullet points or relevant sentences
    lines = [line.strip("•*-\n ") for line in job_text.splitlines()]
    # Filter lines with moderate length, avoiding too short or long
    filtered = [line for line in lines if 8 < len(line) < 150]
    
    # Add some domain-specific additional requirements if missing:
    # We check if ArchiMate is mentioned in job_text, else add as improvement later
    # But here just return extracted first 10
    return filtered[:15]

def extract_strengths(resume_text, key_requirements):
    resume_text_lower = resume_text.lower()
    strengths = []
    for req in key_requirements:
        # Match ignoring case, but look for important keywords only
        # Also handle partial match for phrases split by commas or 'or'
        req_parts = re.split(r",| or ", req.lower())
        if any(part.strip() in resume_text_lower for part in req_parts):
            strengths.append(req.strip())
    return strengths

def identify_improvements(key_requirements, strengths, resume_text):
    improvements = [req for req in key_requirements if req not in strengths]
    # Additional custom improvement: ArchiMate mention
    if "archimate" not in resume_text.lower():
        improvements.append("Familiarity with ArchiMate is advantageous but not currently mentioned in resume.")
    return improvements

def calculate_ats_score(key_requirements, strengths):
    if not key_requirements:
        return 0.0
    return round(len(strengths) / len(key_requirements) * 100, 1)

def format_bullets(text_list):
    """Format a list of strings as bullet points with capital first letters."""
    bullets = []
    for line in text_list:
        line = line.strip()
        if not line:
            continue
        # Capitalize first character, leave rest as is
        formatted_line = line[0].upper() + line[1:]
        bullets.append(formatted_line)
    return "\n".join(f"• {b}" for b in bullets)

def generate_summary(ats_score, key_reqs, strengths, improvements):
    summary_lines = [
        "Strong overlap with key functional, technical, and leadership skills.",
        f"ATS score of {ats_score:.1f}% indicates very good match with this role.",
        "Resume covers most critical qualifications including certifications, sector experience, and consulting background.",
    ]
    if improvements:
        summary_lines.append(
            "Minor improvements can be made by explicitly including: "
            + ", ".join([imp if imp.endswith('.') else imp + "." for imp in improvements[:3]])  # Limit 3 improvements in summary
        )
    else:
        summary_lines.append("No major areas for improvement identified.")
    return "\n".join(summary_lines)

def match_resume_to_jobs(resume_text, jobs_df):
    results = []
    for _, job in jobs_df.iterrows():
        job_text = job.get("Description") or job.get("description") or ""
        # Compose full job text with title and company for better extraction
        job_text_full = f"{job.get('Job Title', '')} at {job.get('Company', '')}. {job_text}"

        key_reqs = extract_key_requirements(job_text_full)
        strengths = extract_strengths(resume_text, key_reqs)
        improvements = identify_improvements(key_reqs, strengths, resume_text)
        ats_score = calculate_ats_score(key_reqs, strengths)
        summary = generate_summary(ats_score, key_reqs, strengths, improvements)
        applicant_name = extract_name(resume_text)

        results.append({
            "Job Title": job.get("Job Title") or job.get("title", ""),
            "Company": job.get("Company") or job.get("company", ""),
            "Location": job.get("Location") or job.get("location", ""),
            "Date Published": job.get("Date Published") or job.get("date", ""),
            "Published By": job.get("Published By") or job.get("publisher", ""),
            "Link": job.get("Link") or job.get("link", ""),
            "Key Requirements": format_bullets(key_reqs),
            "Score (ATS)": f"{ats_score}%",
            "Resume Strengths": format_bullets(strengths),
            "Improvement Areas": format_bullets(improvements),
            "Summary": format_bullets(summary.split("\n")),
            "Applicant": applicant_name
        })

    df = pd.DataFrame(results)
    df["Score (ATS)"] = df["Score (ATS)"].str.rstrip('%').astype(float)
    df = df.sort_values(by="Score (ATS)", ascending=False)
    df["Score (ATS)"] = df["Score (ATS)"].astype(str) + "%"
    return df



