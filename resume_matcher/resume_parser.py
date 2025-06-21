import re

# === Expanded Functional Keywords ===
FUNCTIONAL_KEYWORDS = [
    "data modeling", "data governance", "metadata", "mdm", "master data management",
    "data quality", "compliance", "regulatory reporting", "audit", "risk management",
    "business intelligence", "bi", "forecasting", "planning", "budgeting", "financial analysis",
    "reporting", "analytics", "market analysis", "customer insights", "crm",
    "sales operations", "supply chain", "procurement", "product management",
    "process improvement", "process optimization", "project management",
    "change management", "stakeholder management", "vendor management",
    "contract negotiation", "service delivery", "organizational design",
    "performance metrics", "data strategy", "enterprise architecture",
    "business architecture", "portfolio management", "customer experience",
    "business development", "strategic planning", "transformation programs",
    "agile methodology", "scrum", "kanban", "lean", "six sigma",
    "training and development", "talent management", "employee relations",
    "human resources", "learning and development", "customer success",
    "facility management", "health and safety", "environmental compliance",
    "social media management", "content management", "product lifecycle",
    "quality assurance", "claims management", "underwriting", "loan processing",
    "actuarial analysis", "policy administration", "credit analysis",
    "logistics", "warehouse management", "billing", "payroll", "accounting",
    "taxation", "financial reporting", "corporate communications",
    "data asset management", "data stewardship", "metadata management",
    "service management", "incident management", "problem management"
]

# === Expanded Technical Keywords ===
TECHNICAL_KEYWORDS = [
    "python", "r", "sql", "nosql", "java", "c#", "c++", "scala", "go", "bash", "powershell",
    "html", "css", "javascript", "typescript",
    "azure", "aws", "gcp", "ibm cloud", "oracle cloud", "sap cloud",
    "azure data factory", "azure synapse", "azure purview", "aws lambda", "aws s3",
    "google bigquery", "google dataflow",
    "spark", "hadoop", "kafka", "airflow", "dbt", "databricks", "snowflake",
    "dataiku", "flink", "hive", "presto", "impala", "elastic search",
    "elasticsearch", "cassandra", "mongodb", "redis", "rabbitmq", "apache beam",
    "etl", "data warehouse", "data lake", "data mesh",
    "power bi", "tableau", "qlik", "looker", "microstrategy", "sas",
    "excel", "vba", "matlab", "spss", "stata",
    "jenkins", "git", "docker", "kubernetes", "terraform", "ansible", "puppet",
    "chef", "ci/cd", "circleci", "azure devops", "github actions",
    "tensorflow", "pytorch", "scikit-learn", "keras", "xgboost", "lightgbm",
    "nlp", "llm", "openai", "chatgpt", "gpt-3", "transformers", "machine learning",
    "deep learning", "computer vision", "reinforcement learning", "data science",
    "cybersecurity", "penetration testing", "networking", "firewalls",
    "vpn", "encryption", "cloud security", "identity management",
    "sap", "oracle", "salesforce", "workday", "service now", "jira", "confluence",
    "power automate", "robotic process automation", "automation anywhere", "blue prism",
    "virtualization", "microservices", "api management", "big data", "etl",
    "software development", "qa testing", "agile methodologies", "scrum", "kanban"
]

# === Expanded Soft Skills ===
SOFT_SKILL_KEYWORDS = [
    "leadership", "stakeholder engagement", "strategic planning", "team leadership",
    "mentoring", "coaching", "communication", "collaboration", "cross-functional",
    "consulting", "business acumen", "change management", "problem solving",
    "decision making", "conflict resolution", "negotiation", "influencing",
    "client management", "vendor management", "presentation skills",
    "project management", "time management", "adaptability", "innovation",
    "customer focus", "results driven", "continuous improvement", "critical thinking",
    "emotional intelligence", "business development", "service delivery",
    "training and development", "workshop facilitation", "relationship building",
    "team building", "performance management", "agile mindset", "risk management"
]

EDUCATION_KEYWORDS = [
    "phd", "doctorate", "masters", "msc", "mba", "bachelors", "bsc", "be", "ba", "bcom", "mcom",
    "ca", "cpa", "cfa", "engineering", "statistics", "mathematics", "economics", "data science",
    "computer science", "information systems", "business administration", "finance", "accounting",
    "psychology", "human resources", "supply chain", "public health", "law", "medicine", "education",
    "environmental science", "social work", "marketing", "communications", "biology", "chemistry",
    "physics", "geology", "nursing", "pharmacy", "architecture", "journalism", "graphic design",
    "fine arts", "political science", "international relations", "anthropology", "history"
]

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

ALL_KEYWORDS = set(
    kw.lower() for kw in (
        FUNCTIONAL_KEYWORDS + TECHNICAL_KEYWORDS + SOFT_SKILL_KEYWORDS + EDUCATION_KEYWORDS + CERTIFICATION_KEYWORDS
    )
)

def extract_name(resume_text):
    lines = resume_text.strip().splitlines()
    for line in lines[:10]:
        # skip lines with digits, emails, phones, urls, address keywords
        if line.strip() and not re.search(r"\d|@|http|linkedin|address|phone|email", line, re.IGNORECASE):
            return line.strip()
    return "Unknown"

def split_into_sentences(text):
    # Basic sentence splitter on punctuation + line breaks
    sentences = re.split(r'(?<=[.!?])\s+|\n+', text)
    return [s.strip() for s in sentences if s.strip()]

def find_skill_sentences(text, keywords, max_sentences=15):
    sentences = split_into_sentences(text)
    found = []
    seen = set()
    for keyword in keywords:
        key_lower = keyword.lower()
        for sent in sentences:
            if key_lower in sent.lower() and sent not in seen:
                found.append(sent)
                seen.add(sent)
                if len(found) >= max_sentences:
                    return found
    return found

def format_as_bullets(sentences):
    if not sentences:
        return ["• Not Found"]
    return [f"• {sentence.strip()}" for sentence in sentences]

def parse_resume(resume_text):
    name = extract_name(resume_text)

    functional = find_skill_sentences(resume_text, FUNCTIONAL_KEYWORDS)
    technical = find_skill_sentences(resume_text, TECHNICAL_KEYWORDS)
    soft = find_skill_sentences(resume_text, SOFT_SKILL_KEYWORDS)
    education = find_skill_sentences(resume_text, EDUCATION_KEYWORDS)
    certifications = find_skill_sentences(resume_text, CERTIFICATION_KEYWORDS)

    return {
        "Applicant Name": name,
        "Functional Skills": format_as_bullets(functional),
        "Technical Skills": format_as_bullets(technical),
        "Soft Skills": format_as_bullets(soft),
        "Education": format_as_bullets(education),
        "Certifications": format_as_bullets(certifications)
    }
