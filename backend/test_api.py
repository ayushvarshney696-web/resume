import io
import zipfile
import pytest
import concurrent.futures
from fastapi.testclient import TestClient
from main import app
from cache import analysis_cache

client = TestClient(app)

SAMPLE_RESUME = """
Jane Doe
Email: jane.doe@techdev.io | GitHub: github.com/janedoe | Phone: (555) 234-5678

SUMMARY
Experienced Senior Software Engineer with 6+ years designing and deploying resilient web services in Python and React.

SKILLS
Python, JavaScript, React, FastAPI, PostgreSQL, Docker, Git, CI/CD, REST APIs, System Design

EXPERIENCE
Senior Software Engineer | TechCorp (2020 - Present)
- Architected and deployed 10+ RESTful microservices in FastAPI, accelerating API response times by 40%.
- Engineered responsive client portals in React and TypeScript for 100,000+ active users.
- Automated Docker container deployments reducing release turnaround by 50%.

Software Engineer | Startup Labs (2018 - 2020)
- Developed REST APIs in Python and PostgreSQL.
- Implemented unit testing and CI/CD pipelines in Git.

EDUCATION
B.S. in Computer Science | University of Technology (2014 - 2018)
"""

JUNIOR_RESUME = """
Bob Smith
Email: bob@smith.io | GitHub: github.com/bobsmith

SUMMARY
Recent Computer Science graduate seeking Junior Frontend Developer position.

SKILLS
HTML, CSS, JavaScript, React, Git

PROJECTS
Personal Portfolio: Built responsive website using React and CSS.
Weather App: Created weather application using JavaScript fetch API.

EDUCATION
B.S. in Computer Science | State College (2023 - 2026)
"""

def create_dummy_docx(text: str) -> bytes:
    """Generate in-memory valid DOCX archive."""
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w") as z:
        xml_content = f"""<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">
  <w:body>
    <w:p><w:r><w:t>{text}</w:t></w:r></w:p>
  </w:body>
</w:document>"""
        z.writestr("word/document.xml", xml_content)
    return buf.getvalue()

def test_root_endpoint():
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "online"
    assert "features" in data
    assert data["version"] == "2.2.0"

def test_health_endpoint():
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "Software Engineer" in data["supported_roles"]
    assert "Strict ATS Scanner" in data["supported_personas"]
    assert data["max_file_size_mb"] == 5.0

def test_sample_resumes():
    response = client.get("/api/sample-resumes")
    assert response.status_code == 200
    samples = response.json()
    assert "software_engineer" in samples
    assert "data_scientist" in samples
    assert "product_manager" in samples

def test_analyze_text_json():
    payload = {
        "resume_text": SAMPLE_RESUME,
        "job_role": "Full Stack Developer",
        "job_description": "Seeking Full Stack Engineer proficient in React, Python, Docker, and CI/CD.",
        "persona": "Career Coach"
    }
    response = client.post("/api/analyze-text", json=payload)
    assert response.status_code == 200
    data = response.json()

    assert data["success"] is True
    assert 0 <= data["overall_score"] <= 100
    assert "category_scores" in data
    assert data["category_scores"]["role_relevance"] >= 50
    assert len(data["strengths"]) > 0
    assert len(data["matched_keywords"]) > 0
    assert len(data["bullet_improvements"]) > 0
    assert len(data["interview_questions"]) > 0
    assert "seniority_level" in data
    assert "Senior" in data["seniority_level"]

def test_seniority_detection_junior():
    payload = {
        "resume_text": JUNIOR_RESUME,
        "job_role": "Frontend Developer",
        "persona": "Career Coach"
    }
    response = client.post("/api/analyze-text", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "Junior" in data["seniority_level"]

def test_all_four_personas():
    personas = [
        "Career Coach",
        "Strict ATS Scanner",
        "Technical Hiring Manager",
        "Executive Recruiter"
    ]
    for p in personas:
        payload = {
            "resume_text": SAMPLE_RESUME,
            "job_role": "Software Engineer",
            "persona": p
        }
        res = client.post("/api/analyze-text", json=payload)
        assert res.status_code == 200
        assert res.json()["persona"] == p

def test_analyze_empty_text():
    response = client.post("/api/analyze-text", json={"resume_text": "   "})
    assert response.status_code in (400, 422)

def test_analyze_too_short_text():
    response = client.post("/api/analyze-text", json={"resume_text": "Hi, I am Bob."})
    assert response.status_code in (400, 422)

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

def test_analyze_txt_file_upload():
    file_bytes = SAMPLE_RESUME.encode("utf-8")
    response = client.post(
        "/api/analyze",
        data={"job_role": "Backend Developer", "persona": "Technical Hiring Manager"},
        files={"resume": ("developer_resume.txt", file_bytes, "text/plain")}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True

def test_analyze_docx_file_upload():
    docx_bytes = create_dummy_docx(SAMPLE_RESUME)
    response = client.post(
        "/api/analyze",
        data={"job_role": "Software Engineer", "persona": "Career Coach"},
        files={"resume": ("sample.docx", docx_bytes, "application/vnd.openxmlformats-officedocument.wordprocessingml.document")}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True

def test_unsupported_file_extension():
    response = client.post(
        "/api/analyze",
        data={"job_role": "Software Engineer"},
        files={"resume": ("malware.exe", b"MZ...", "application/octet-stream")}
    )
    assert response.status_code == 400
    assert "Unsupported file format" in response.json()["detail"]

def test_oversized_file_rejected():
    oversized = b"A" * (6 * 1024 * 1024)
    response = client.post(
        "/api/analyze",
        data={"job_role": "Software Engineer"},
        files={"resume": ("huge.txt", oversized, "text/plain")}
    )
    assert response.status_code == 413

def test_security_headers_present():
    response = client.get("/")
    assert response.headers.get("X-Content-Type-Options") == "nosniff"
    assert response.headers.get("X-Frame-Options") == "DENY"
    assert response.headers.get("X-XSS-Protection") == "1; mode=block"

def test_cache_hits_and_stats():
    analysis_cache.clear()
    payload = {
        "resume_text": SAMPLE_RESUME,
        "job_role": "Software Engineer",
        "persona": "Career Coach"
    }
    # First request: Miss
    res1 = client.post("/api/analyze-text", json=payload)
    assert res1.status_code == 200
    
    # Second request: Hit
    res2 = client.post("/api/analyze-text", json=payload)
    assert res2.status_code == 200

    stats = client.get("/api/cache-stats").json()
    assert stats["hits"] >= 1
    assert stats["size"] >= 1

def test_concurrent_requests():
    payload = {
        "resume_text": SAMPLE_RESUME,
        "job_role": "Software Engineer",
        "persona": "Career Coach"
    }
    
    def make_req():
        return client.post("/api/analyze-text", json=payload).status_code

    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
        futures = [executor.submit(make_req) for _ in range(5)]
        results = [f.result() for f in concurrent.futures.as_completed(futures)]
        
    assert all(code == 200 for code in results)
