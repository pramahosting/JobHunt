# ================================
# cover_letter_generator/cover_letter.py
# ================================

import re

def extract_keywords(text):
    words = re.findall(r'\b\w+\b', text.lower())
    stop_words = {"the", "and", "for", "with", "in", "of", "to", "a", "on", "as", "is", "an", "be", "this", "that"}
    keywords = [word for word in words if word not in stop_words and len(word) > 3]
    return list(set(keywords))[:20]

def extract_strengths(resume_text, job_description):
    resume_lines = resume_text.split('\n')
    job_keywords = extract_keywords(job_description)
    strengths = []

    for line in resume_lines:
        line_clean = line.strip().lower()
        if any(keyword in line_clean for keyword in job_keywords):
            strengths.append(line.strip())

    return strengths[:3] if strengths else []

def extract_name(resume_text):
    # Assume name is in the first non-empty line and contains 2-4 words with each capitalized
    lines = [line.strip() for line in resume_text.split('\n') if line.strip()]
    for line in lines:
        if 2 <= len(line.split()) <= 4 and all(word[0].isupper() for word in line.split() if word):
            return line
    return "Your Name"

def generate_cover_letter(resume_text, job):
    job_title = job.get('Job Title') or job.get('title', 'the position')
    company = job.get('Company') or job.get('company', 'your organization')
    location = job.get('Location') or job.get('location', 'your location')
    job_desc = job.get("description", "")
    candidate_name = extract_name(resume_text)

    strengths = extract_strengths(resume_text, job_desc)
    strengths_formatted = "\n".join([f"- {s}" for s in strengths]) if strengths else "- [Your key strengths here]"

    return f"""Dear {company},\n
I am writing to express my strong interest in the **{job_title}** role based in {location}. With proven experience aligned to your key requirements, I am confident in my ability to contribute effectively to your team from day one.\n
**Top reasons I am a strong fit for this role:**\n
{strengths_formatted}\n
I am particularly drawn to {company} because of its innovation, leadership, and values that align with my own. I bring a track record of delivering impactful results and driving business value through data-driven solutions and cross-functional collaboration.\n
I would welcome the opportunity to contribute my expertise and energy to your organization. Thank you for considering my application.\n
Warm regards,\n
{candidate_name}
"""
