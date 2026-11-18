import io
import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

SAMPLE_RESUME = """
Jane Doe
Email: jane.doe@techdev.io | GitHub: github.com/janedoe

SUMMARY
Experienced Full Stack Developer with 4 years designing and deploying resilient web services in Python and React.

SKILLS
Python, JavaScript, React, FastAPI, PostgreSQL, Docker, Git, CI/CD, REST APIs

EXPERIENCE
Senior Software Engineer | TechCorp (2022 - Present)
- Architected and deployed 10+ RESTful microservices in FastAPI, accelerating API response times by 40%.
- Engineered responsive client portals in React and TypeScript for 100,000+ active users.
- Automated Docker container deployments reducing release turnaround by 50%.

EDUCATION
B.S. in Computer Science | University of Technology (2018 - 2022)
"""

def test_root_endpoint():
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "online"
    assert "features" in data

def test_health_endpoint():
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "Software Engineer" in data["supported_roles"]
    assert "Career Coach" in data["supported_personas"]

def test_sample_resumes():
    response = client.get("/api/sample-resumes")
    assert response.status_code == 200
    samples = response.json()
    assert "software_engineer" in samples
    assert "data_scientist" in samples

def test_analyze_text_json():
    payload = {
        "resume_text": SAMPLE_RESUME,
        "job_role": "Full Stack Developer",
        "job_description": "Looking for a developer with React, Python, Docker, and CI/CD skills.",
        "persona": "Career Coach"
    }
    response = client.post("/api/analyze-text", json=payload)
    assert response.status_code == 200
    data = response.json()
    
    assert data["success"] is True
    assert 0 <= data["overall_score"] <= 100
    assert "category_scores" in data
    assert data["category_scores"]["role_relevance"] > 50
    assert len(data["strengths"]) > 0
    assert len(data["matched_keywords"]) > 0
    assert len(data["bullet_improvements"]) > 0
    assert len(data["interview_questions"]) > 0

def test_analyze_empty_text():
    response = client.post("/api/analyze-text", json={"resume_text": ""})
    assert response.status_code == 400

def test_analyze_multipart_text():
    response = client.post(
        "/api/analyze",
        data={
            "resume_text": SAMPLE_RESUME,
            "job_role": "Software Engineer",
            "persona": "Strict ATS Scanner"
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert data["persona"] == "Strict ATS Scanner"
    assert data["overall_score"] > 0

def test_analyze_txt_file_upload():
    file_bytes = SAMPLE_RESUME.encode("utf-8")
    response = client.post(
        "/api/analyze",
        data={"job_role": "Backend Developer", "persona": "Technical Hiring Manager"},
        files={"resume": ("my_resume.txt", file_bytes, "text/plain")}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["persona"] == "Technical Hiring Manager"
