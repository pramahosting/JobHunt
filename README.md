JobHunt Agent 💡

JobHunt Agent is a full-stack AI-powered job matching tool that:

Scrapes real-time jobs using Browse AI & ScraperAPI.

Matches your uploaded resume with job descriptions.

Scores suitability based on tools, experience, skills, and responsibilities.

Generates personalized cover letters.

Allows direct job application via portal link.

Exports a downloadable Excel sheet with all results.

🌐 Live Demo

To deploy this project on Render.com:

✅ Prerequisites

Python 3.9 or later

requirements.txt present

Streamlit account (for UI)

🔧 Build & Start Command (Render)

pip install -r requirements.txt
streamlit run frontend_ui/app.py

🔍 Features

Smart Scraping from:

indeed.com.au via ScraperAPI

(Stub for Browse AI ready)

Filtering: Role, Location, Industry, Job Type, Salary Range

Matching Engine: Resume matched on:

Tools & Tech

Years of experience

Responsibilities

Soft skills

Cover Letter Generator: Uses top strengths

Export to Excel: Includes title, company, score, link, and letter

🔄 Project Structure

jobintel-agent/
├── job_scraper/
│   └── job_scraper.py
├── resume_matcher/
│   └── match_resume.py
├── cover_letter_generator/
│   └── cover_letter.py
├── excel_exporter/
│   └── export_excel.py
├── frontend_ui/
│   └── app.py
├── requirements.txt
└── README.md

🚀 Getting Started Locally

Clone the repo:

git clone https://github.com/your-username/jobintel-agent.git
cd jobintel-agent

Install dependencies:

pip install -r requirements.txt

Run the app:

streamlit run frontend_ui/app.py

🌐 API Keys Setup

Ensure your job_scraper.py includes the API keys:

BROWSE_AI_API_KEY = "your-browseai-key"
SCRAPER_API_KEY = "your-scraperapi-key"

💳 Free APIs Used

ScraperAPI

Browse AI

🦄 Suggested AI Tools for Agent Building

This app can be built and deployed using:

Streamlit – Free & fast for UI.

Render – Free tier supports Streamlit apps.

Hugging Face Spaces – Another excellent no-cost deploy option for ML apps.

🚀 Future Enhancements

Integrate actual Browse AI Robot

Add support for PDF/Docx resumes

Improve NLP for stronger matching

Add pagination + multi-source scraping

✅ License

MIT License