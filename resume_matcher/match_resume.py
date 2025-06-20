# ================================
# resume_matcher/match_resume.py
# ================================
import re
import pandas as pd
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# ================================
# Keyword Categories (Expanded)
# ================================

# Business/Strategic Keywords – very broad, all industries & domains
BUSINESS_KEYWORDS = [
    "strategy", "strategic", "risk", "stakeholder", "budget", "revenue", "regulatory", "policy",
    "compliance", "governance", "roadmap", "kpi", "roi", "leadership", "operations", "profit",
    "market", "growth", "forecast", "benchmarking", "business case", "transformation",
    "program", "project", "initiative", "change management", "innovation", "customer experience",
    "business development", "vendor management", "contract negotiation", "cost reduction",
    "process improvement", "organizational design", "corporate social responsibility",
    "sustainability", "digital transformation", "mergers and acquisitions", "due diligence",
    "enterprise architecture", "portfolio management", "budgeting", "performance metrics",
    "competitive analysis", "brand management", "business intelligence"
]

# Functional/Domain Skills – broad + industry-specific + emerging functions
FUNCTIONAL_KEYWORDS = [
    "reporting", "analytics", "planning", "modeling", "forecasting", "dashboard", "visualization",
    "crm", "erp", "supply chain", "procurement", "sales", "marketing", "customer service",
    "inventory", "quality assurance", "compliance monitoring", "financial analysis",
    "claims", "underwriting", "actuarial", "policy administration", "loan processing",
    "portfolio management", "accounting", "payroll", "billing", "audit", "hris", "talent management",
    "recruitment", "employee relations", "training and development", "learning and development",
    "compensation and benefits", "corporate communications", "risk management", "credit analysis",
    "logistics", "warehouse management", "health and safety", "environmental compliance",
    "data governance", "content management", "social media management", "product management",
    "customer success", "vendor relations", "business process outsourcing", "facility management"
]

# Technical Tools & Platforms – very broad + modern tech + cloud + automation + programming + BI
TECHNICAL_KEYWORDS = [
    "python", "r", "sql", "nosql", "azure", "aws", "gcp", "tableau", "powerbi", "qlik", "looker",
    "databricks", "snowflake", "dataiku", "airflow", "dbt", "spark", "hadoop", "kafka", "rest api",
    "flask", "django", "react", "angular", "vue", "html", "css", "javascript", "typescript",
    "git", "jenkins", "linux", "docker", "kubernetes", "terraform", "ansible", "puppet",
    "ci/cd", "machine learning", "deep learning", "llm", "nlp", "pytorch", "tensorflow",
    "excel", "vba", "sas", "matlab", "oracle", "sap", "salesforce", "workday", "service now",
    "power automate", "robotic process automation", "automation anywhere", "blue prism",
    "virtualization", "networking", "cybersecurity", "penetration testing", "blockchain",
    "iot", "devops", "microservices", "api management", "big data", "etl", "data warehouse",
    "data lake", "business intelligence", "cloud computing", "software development",
    "qa testing", "agile methodologies", "scrum", "kanban", "jira"
]

# Educational Degrees – very broad academic disciplines, business, science, tech, healthcare, humanities
EDUCATION_KEYWORDS = [
    "phd", "doctorate", "masters", "msc", "mba", "bachelors", "bsc", "be", "ba", "bcom", "mcom",
    "ca", "cpa", "cfa", "engineering", "statistics", "mathematics", "economics", "data science",
    "computer science", "information systems", "business administration", "finance", "accounting",
    "psychology", "human resources", "supply chain", "public health", "law", "medicine", "education",
    "environmental science", "social work", "marketing", "communications", "biology", "chemistry",
    "physics", "geology", "nursing", "pharmacy", "architecture", "journalism", "graphic design",
    "fine arts", "political science", "international relations", "anthropology", "history"
]

# Certifications – cross domain & sector popular certs
CERTIFICATION_KEYWORDS = [
    "pmp", "prince2", "scrum master", "safe", "agile", "six sigma", "csm", "itil",
    "aws certified", "azure fundamentals", "azure data engineer", "google cloud certified",
    "cfa", "frcpa", "cisa", "cissp", "cbap", "ccba", "cda", "dataiku certified",
    "tableau certified", "power bi certified", "google analytics", "salesforce admin",
    "sap fico", "sap mm", "workday certified", "python certification", "sql certification",
    "network+", "security+", "ccna", "ccnp", "aws solutions architect", "azure solutions architect",
    "machine learning certification", "deep learning certification", "risk management professional",
    "financial risk manager", "chartered accountant", "certified internal auditor",
    "human resources certification", "digital marketing certification", "leadership certification",
    "cloud practitioner", "cybersecurity analyst", "data analyst certification", "devops certification"
]

def clean_and_tokenize(text):
    text = re.sub(r"[^a-zA-Z0-9 ]", " ", text)
    tokens = list(set([w.strip().lower() for w in text.split() if len(w.strip()) > 2]))
    return tokens

def classify_keywords(tokens):
    business = [t for t in tokens if t in BUSINESS_KEYWORDS]
    functional = [t for t in tokens if t in FUNCTIONAL_KEYWORDS]
    technical = [t for t in tokens if t in TECHNICAL_KEYWORDS]
    education = [t for t in tokens if t in EDUCATION_KEYWORDS]
    certifications = [t for t in tokens if t in CERTIFICATION_KEYWORDS]
    return business, functional, technical, education, certifications

def extract_features(text):
    tokens = clean_and_tokenize(text)
    return classify_keywords(tokens)

def compute_ats_score(resume_text, job_desc):
    vectorizer = CountVectorizer().fit_transform([resume_text, job_desc])
    score = cosine_similarity(vectorizer[0:1], vectorizer[1:2])[0][0] * 100
    return round(score, 1)

def match_resume_to_jobs(resume_text, job_list):
    matched_jobs = []

    # If DataFrame, convert to list of dicts
    if isinstance(job_list, pd.DataFrame):
        job_list = job_list.to_dict(orient="records")

    for job in job_list:
        if not isinstance(job, dict):
            continue

        job_desc = str(job.get("Description") or job.get("description") or "")
        score = compute_ats_score(resume_text, job_desc)

        resume_b, resume_f, resume_t, resume_e, resume_c = classify_keywords(clean_and_tokenize(resume_text))
        job_b, job_f, job_t, job_e, job_c = classify_keywords(clean_and_tokenize(job_desc))

        matched_b = set(resume_b) & set(job_b)
        matched_f = set(resume_f) & set(job_f)
        matched_t = set(resume_t) & set(job_t)
        matched_e = set(resume_e) & set(job_e)
        matched_c = set(resume_c) & set(job_c)

        missing_b = set(job_b) - set(resume_b)
        missing_f = set(job_f) - set(resume_f)
        missing_t = set(job_t) - set(resume_t)
        missing_e = set(job_e) - set(resume_e)
        missing_c = set(job_c) - set(resume_c)

        strengths = []
        if matched_b:
            strengths.append(f"Business: {', '.join(sorted(matched_b))}")
        if matched_f:
            strengths.append(f"Functional: {', '.join(sorted(matched_f))}")
        if matched_t:
            strengths.append(f"Technical: {', '.join(sorted(matched_t))}")
        if matched_e:
            strengths.append(f"Education: {', '.join(sorted(matched_e))}")
        if matched_c:
            strengths.append(f"Certifications: {', '.join(sorted(matched_c))}")

        improvements = []
        if missing_b:
            improvements.append(f"Lack of business exposure in {', '.join(sorted(missing_b))}")
        if missing_f:
            improvements.append(f"Improve functional skills like {', '.join(sorted(missing_f))}")
        if missing_t:
            improvements.append(f"Missing technical tools: {', '.join(sorted(missing_t))}")
        if missing_e:
            improvements.append(f"Consider education in {', '.join(sorted(missing_e))}")
        if missing_c:
            improvements.append(f"Add certifications such as {', '.join(sorted(missing_c))}")

        matched_jobs.append({
            "Job Title": job.get("Job Title") or job.get("title", ""),
            "Company": job.get("Company") or job.get("company", ""),
            "Location": job.get("Location") or job.get("location", ""),
            "Score (ATS)": score,
            "Strengths": "; ".join(strengths[:2]),
            "Improvement Areas": "; ".join(improvements[:2]),
            "Link": job.get("Link") or job.get("Apply Link") or job.get("link", "")
        })

    # Handle no matches
    if not matched_jobs:
        matched_jobs.append({
            "Job Title": "No Match",
            "Company": "-",
            "Location": "-",
            "Score (ATS)": 0,
            "Strengths": "No matching keywords found",
            "Improvement Areas": "Resume needs more relevant content",
            "Link": "-"
        })

    return pd.DataFrame(sorted(matched_jobs, key=lambda x: x["Score (ATS)"], reverse=True))

