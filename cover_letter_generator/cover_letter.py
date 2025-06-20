# ================================
# cover_letter_generator/cover_letter.py
# ================================

import re

def extract_keywords(text):
    words = re.findall(r'\b\w+\b', text.lower())
    stop_words = {"the", "and", "for", "with", "in", "of", "to", "a", "on", "as", "is", "an", "be", "this", "that"}
    return [word for word in words if word not in stop_words and len(word) > 3]

def extract_candidate_name(resume_text):
    lines = [line.strip() for line in resume_text.split('\n') if line.strip()]
    for line in lines[:10]:
        if 2 <= len(line.split()) <= 4 and all(w[0].isupper() for w in line.split() if w[0].isalpha()):
            return line
    return "Your Name"

def extract_strength_sentences(resume_text, job_description, max_points=4):
    resume_lines = [line.strip() for line in resume_text.split('\n') if line.strip()]
    job_keywords = extract_keywords(job_description)
    scored_lines = []

    for line in resume_lines:
        score = sum(1 for kw in job_keywords if kw in line.lower())
        if score > 0:
            scored_lines.append((score, line))

    top_sentences = [line.lstrip("• ").rstrip('.') + '.' for _, line in sorted(scored_lines, key=lambda x: x[0], reverse=True)[:max_points]]
    return top_sentences

def generate_cover_letter(resume_text, job):
    job_title = job.get('Job Title') or job.get('title', 'the position')
    company = job.get('Company') or job.get('company', 'your organization')
    job_desc = job.get("Description") or job.get("description", "")
    candidate_name = extract_candidate_name(resume_text)
    strengths = extract_strength_sentences(resume_text, job_desc)

    # Determine if the company is a recruitment agency by keywords
    is_agency = any(word in company.lower() for word in ['recruit', 'agency', 'talent', 'staffing'])

    reasons = "\n".join([f"- {s}" for s in strengths]) if strengths else "- [Your relevant strengths here]"

    letter = f"""Dear Hiring Manager,

I am writing to express my strong interest in the {job_title} role. With proven experience aligned to your key requirements, I am confident in my ability to contribute effectively from day one.

Top reasons I am a strong fit for this role:
{reasons}
"""

    if not is_agency:
        letter += f"""\nI am particularly drawn to {company} because of its innovation, leadership, and values that align with my own.
"""

    letter += f"""\nI would welcome the opportunity to contribute my expertise and energy to your organization. Thank you for considering my application.

Warm regards,  
{candidate_name}
"""
    return letter
