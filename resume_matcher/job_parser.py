import requests
from bs4 import BeautifulSoup

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
        BUSINESS_KEYWORDS + FUNCTIONAL_KEYWORDS + TECHNICAL_KEYWORDS + EDUCATION_KEYWORDS + CERTIFICATION_KEYWORDS
    )
)


def fetch_job_description(url):
    headers = {"User-Agent": "Mozilla/5.0"}
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, "html.parser")
    desc_div = soup.find("div", class_="job-description") or soup.find("div", id="job-description")
    if not desc_div:
        # fallback: return whole page text
        return soup.get_text(separator="\n")
    paragraphs = desc_div.find_all(["p", "li"])
    lines = [p.get_text(separator=" ", strip=True) for p in paragraphs if p.get_text(strip=True)]
    return "\n".join(lines)

def extract_key_requirements(job_desc_text):
    lines = job_desc_text.splitlines()
    requirements = []
    seen = set()
    for line in lines:
        clean_line = line.strip()
        if len(clean_line) < 10:
            continue
        lower_line = clean_line.lower()
        if any(k in lower_line for k in ALL_KEYWORDS):
            if clean_line not in seen:
                requirements.append(f"• {clean_line}")
                seen.add(clean_line)
    if not requirements:
        requirements = ["• No key requirements extracted."]
    return requirements

def parse_job_posting(url):
    jd_text = fetch_job_description(url)
    reqs = extract_key_requirements(jd_text)
    return reqs
