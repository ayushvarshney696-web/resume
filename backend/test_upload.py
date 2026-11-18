import sys
import io
import requests

BACKEND_URL = "http://127.0.0.1:8000"

SAMPLE_RESUME = """
Alex Chen
Email: alex.chen@devmail.com | Portfolio: alexchen.dev | GitHub: github.com/alexchen

SUMMARY
Senior Backend & Cloud Engineer with 5+ years designing highly available distributed systems. Expert in Python, Go, Kubernetes, and AWS architecture.

TECHNICAL SKILLS
- Languages: Python, Go, SQL, Bash
- Frameworks & Libs: FastAPI, Flask, SQLAlchemy, Celery, gRPC
- Cloud & Infrastructure: AWS (ECS, S3, RDS, Lambda), Docker, Kubernetes, Terraform, CI/CD, Redis, PostgreSQL

WORK EXPERIENCE
Lead Backend Engineer | FinTech Cloud (2022 - Present)
- Architected high-throughput payment processing engine in FastAPI and Redis handling 8,500 requests/second with 99.99% uptime.
- Reduced AWS infrastructure spend by 28% ($120,000/year) by containerizing workloads and implementing auto-scaling on Kubernetes.
- Automated CI/CD pipelines using GitHub Actions and Docker, reducing release deployment cycle by 45%.

Software Engineer | NextGen Systems (2019 - 2022)
- Developed RESTful APIs in Python and PostgreSQL for 250,000 active enterprise users.
- Optimized slow database queries by indexing and query rewriting, reducing p95 latency by 60%.

EDUCATION
B.S. in Computer Science | University of Illinois at Urbana-Champaign (2015 - 2019)
"""

def test_health():
    print("-> Checking Backend Health...")
    try:
        res = requests.get(f"{BACKEND_URL}/api/health", timeout=5)
        print(f"   Status Code: {res.status_code}")
        print(f"   Response: {res.json()}\n")
        return res.status_code == 200
    except requests.exceptions.ConnectionError:
        print(f"❌ Backend server not running at {BACKEND_URL}.")
        print("   Start it using: uvicorn main:app --reload\n")
        return False

def test_analyze_text():
    print("-> Testing JSON Text Analysis Endpoint...")
    payload = {
        "resume_text": SAMPLE_RESUME,
        "job_role": "Backend Developer",
        "job_description": "Seeking a Backend Engineer skilled in Python, FastAPI, Docker, and AWS.",
        "persona": "Career Coach"
    }
    res = requests.post(f"{BACKEND_URL}/api/analyze-text", json=payload, timeout=10)
    print(f"   Status Code: {res.status_code}")
    data = res.json()
    print(f"   Overall Score: {data.get('overall_score')}/100")
    print(f"   Category Scores: {data.get('category_scores')}")
    print(f"   Strengths Found: {len(data.get('strengths', []))}")
    print(f"   Missing Keywords: {data.get('missing_keywords', [])[:3]}\n")

def test_analyze_upload():
    print("-> Testing File Upload Endpoint (/api/analyze)...")
    file_bytes = SAMPLE_RESUME.encode("utf-8")
    files = {
        "resume": ("sample_resume.txt", io.BytesIO(file_bytes), "text/plain")
    }
    data = {
        "job_role": "Cloud Engineer",
        "persona": "Strict ATS Scanner"
    }
    res = requests.post(f"{BACKEND_URL}/api/analyze", data=data, files=files, timeout=10)
    print(f"   Status Code: {res.status_code}")
    result = res.json()
    print(f"   Persona: {result.get('persona')}")
    print(f"   Overall Score: {result.get('overall_score')}/100\n")

if __name__ == "__main__":
    print("==================================================")
    print("       AI Resume Reviewer - Backend Verification  ")
    print("==================================================\n")
    if test_health():
        test_analyze_text()
        test_analyze_upload()
        print("✅ All backend live tests completed successfully!")
    else:
        print("ℹ️ To run live tests, start the server with: cd backend && python -m uvicorn main:app --reload")
