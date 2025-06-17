# ================================
# cover_letter_generator/cover_letter.py
# ================================
def extract_strengths(resume_text):
    lines = resume_text.split('\n')
    strengths = []
    for line in lines:
        if any(keyword in line.lower() for keyword in ["experience", "expertise", "skilled", "knowledge", "proficient"]):
            strengths.append(line.strip())
    return "\n".join(strengths[:3])  # pick top 3 lines

def generate_cover_letter(resume_text, job):
    strengths = extract_strengths(resume_text)
    return f"""Dear {job['company']},

I am writing to express my interest in the {job['title']} role located in {job['location']}. I believe my experience and skills make me a strong candidate for this position.

Key strengths and relevant experience:
{strengths}

I would welcome the opportunity to bring this expertise to your team and contribute to your continued success.

Thank you for considering my application.

Sincerely,
Your Name
"""