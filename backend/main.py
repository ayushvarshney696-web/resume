import os
from typing import Optional
from fastapi import FastAPI, File, UploadFile, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

from models import AnalysisResult, TextAnalysisRequest
from parser import extract_resume_text
from analyzer import ResumeAnalyzer, ROLE_KEYWORD_DATABASE

# Load environment variables
load_dotenv()

app = FastAPI(
    title="AI Resume Reviewer & Career Strategist API",
    description="Intelligent ATS scoring, keyword gap analysis, bullet enhancement, and interview preparation assistant.",
    version="2.0.0"
)

# Enable CORS for all local and deployed origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

analyzer = ResumeAnalyzer()

SAMPLE_RESUMES = {
    "software_engineer": {
        "title": "Software Engineer (Full Stack)",
        "role": "Software Engineer",
        "text": """John Doe
Email: john.doe@example.com | Phone: (555) 019-2834 | GitHub: github.com/johndoe | LinkedIn: linkedin.com/in/johndoe

PROFESSIONAL SUMMARY
Results-driven Software Engineer with 3+ years of experience building modern web applications, scalable REST APIs, and microservices. Proficient in React, Python, FastAPI, and PostgreSQL.

SKILLS
- Languages: Python, JavaScript, TypeScript, SQL, HTML5, CSS3
- Frameworks & Libraries: React, Node.js, FastAPI, Express, Tailwind CSS
- Databases & Tools: PostgreSQL, MongoDB, Redis, Docker, Git, CI/CD, Linux

PROFESSIONAL EXPERIENCE
Software Developer | Acme Tech Solutions (2022 - Present)
- Architected and deployed 12+ RESTful microservices using FastAPI and PostgreSQL, reducing query latency by 35%.
- Built responsive user dashboards in React and TypeScript, serving over 150,000 monthly active users.
- Automated CI/CD deployment pipelines using GitHub Actions and Docker, cutting deployment cycle times from 45 minutes to 10 minutes.
- Responsible for fixing bugs and assisting junior team members with code reviews.

Junior Developer | Innovate Soft (2021 - 2022)
- Developed frontend UI components using React and Redux.
- Worked on database migrations and optimized SQL queries.
- Participated in daily agile standups and sprint planning.

EDUCATION
B.Tech in Computer Science & Engineering | State University (2017 - 2021)
GPA: 3.8/4.0
"""
    },
    "data_scientist": {
        "title": "Data Scientist & ML Specialist",
        "role": "Data Scientist",
        "text": """Sarah Connor
Email: sarah.connor@example.com | Portfolio: sconnor.ai | GitHub: github.com/sconnor

SUMMARY
Data Scientist with 4 years of expertise in predictive modeling, natural language processing, and deep learning. Proven track record of operationalizing machine learning models into production systems.

TECHNICAL SKILLS
- Programming: Python, R, SQL, Bash
- ML & Deep Learning: Scikit-Learn, PyTorch, TensorFlow, Hugging Face Transformers, Pandas, NumPy
- MLOps & Cloud: Docker, AWS S3/EC2, MLflow, FastAPI, BigQuery

EXPERIENCE
Machine Learning Scientist | DataCore Analytics (2022 - Present)
- Engineered an end-to-end customer churn prediction model using XGBoost, increasing retention by 18% and saving $450,000 annually.
- Spearheaded transformer-based sentiment analysis pipeline for 2.5 million customer reviews with 94.2% accuracy.
- Built automated feature store and model evaluation scripts using Python and MLflow.

Data Analyst | Insight Dynamics (2020 - 2022)
- Conducted exploratory data analysis on 10M+ transaction records using SQL and Pandas.
- Designed interactive executive dashboards in Tableau for C-suite decision-making.

EDUCATION
M.S. in Data Science | Tech Institute of California (2018 - 2020)
B.S. in Applied Mathematics | University of Michigan (2014 - 2018)
"""
    },
    "product_manager": {
        "title": "Technical Product Manager",
        "role": "Product Manager",
        "text": """Alex Morgan
Email: alex.morgan@product.io | LinkedIn: linkedin.com/in/alexmorganpm

PROFILE
Strategic Product Manager with 5 years leading cross-functional engineering and design teams. Specialized in B2B SaaS, product discovery, metrics tracking, and go-to-market strategies.

CORE COMPETENCIES
- Product Strategy, Agile/Scrum, User Research, OKRs, KPI Tracking, Roadmapping
- A/B Testing, Wireframing, SQL, Jira, Mixpanel, Figma

EXPERIENCE
Senior Product Manager | CloudScale Inc. (2022 - Present)
- Owned product roadmap for enterprise billing SaaS platform, driving $3.2M ARR growth within 14 months.
- Conducted 60+ user discovery interviews and launched redesign reducing customer onboarding churn by 27%.
- Defined and tracked weekly core North Star metrics across 4 cross-functional development squads.

Product Owner | NextGen Apps (2019 - 2022)
- Managed sprint backlog and prioritized user stories in Jira for team of 9 engineers.
- Increased user feature adoption by 40% via targeted A/B test experiments.

EDUCATION
B.A. in Economics & Business | Northwestern University (2015 - 2019)
"""
    }
}

@app.get("/")
async def root():
    return {
        "status": "online",
        "service": "AI Resume Reviewer & Career Strategist API",
        "version": "2.0.0",
        "features": [
            "ATS Compatibility Scoring",
            "Keyword Gap Identification",
            "Quantified Impact Evaluation",
            "Google XYZ Bullet Enhancement",
            "Interview Question Generation",
            "Multiple Dynamic Personas",
            "Dual AI Engine (Gemini 2.0 Flash + Offline Intelligent ATS Engine)"
        ]
    }

@app.get("/api/health")
async def health_check():
    gemini_key_set = bool(os.getenv("GEMINI_API_KEY", "").strip())
    return {
        "status": "healthy",
        "gemini_configured": gemini_key_set,
        "supported_roles": list(ROLE_KEYWORD_DATABASE.keys()),
        "supported_personas": [
            "Career Coach",
            "Strict ATS Scanner",
            "Technical Hiring Manager",
            "Executive Recruiter"
        ]
    }

@app.get("/api/sample-resumes")
async def get_sample_resumes():
    return SAMPLE_RESUMES

@app.post("/api/analyze", response_model=AnalysisResult)
async def analyze_resume_upload(
    resume: Optional[UploadFile] = File(None),
    resume_text: Optional[str] = Form(None),
    job_role: str = Form("Software Engineer"),
    job_description: Optional[str] = Form(""),
    persona: Optional[str] = Form("Career Coach"),
    api_key: Optional[str] = Form(None)
):
    extracted_text = ""
    file_type = "Pasted Text"

    if resume:
        content = await resume.read()
        if not content:
            raise HTTPException(status_code=400, detail="Uploaded file is empty.")
        extracted_text, file_type = extract_resume_text(resume.filename, content)
    elif resume_text and resume_text.strip():
        extracted_text = resume_text.strip()
    else:
        raise HTTPException(
            status_code=400,
            detail="Please provide a resume by uploading a file or pasting resume text."
        )

    if not extracted_text.strip():
        raise HTTPException(
            status_code=400,
            detail="Could not extract readable text from the file. Please upload a standard PDF, DOCX, or text file."
        )

    result = analyzer.analyze(
        resume_text=extracted_text,
        job_role=job_role,
        job_description=job_description or "",
        persona=persona or "Career Coach",
        user_api_key=api_key
    )

    return result

@app.post("/api/analyze-text", response_model=AnalysisResult)
async def analyze_text_endpoint(req: TextAnalysisRequest):
    if not req.resume_text or not req.resume_text.strip():
        raise HTTPException(status_code=400, detail="Resume text cannot be empty.")

    return analyzer.analyze(
        resume_text=req.resume_text.strip(),
        job_role=req.job_role or "Software Engineer",
        job_description=req.job_description or "",
        persona=req.persona or "Career Coach",
        user_api_key=req.api_key
    )

# Backward-compatibility alias
@app.post("/upload-resume", response_model=AnalysisResult)
async def upload_resume_alias(file: UploadFile = File(...)):
    content = await file.read()
    extracted_text, _ = extract_resume_text(file.filename, content)
    return analyzer.analyze(resume_text=extracted_text, job_role="Software Engineer")

@app.post("/upload-text", response_model=AnalysisResult)
async def upload_text_alias(resume_text: str = Form(...)):
    return analyzer.analyze(resume_text=resume_text, job_role="Software Engineer")
