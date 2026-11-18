"""Configuration settings and constants for the AI Resume Reviewer application."""

import os
from typing import Dict, List, Final
from dotenv import load_dotenv

load_dotenv()

# Server & Security Limits
PORT: Final[int] = int(os.getenv("PORT", 8000))
MAX_FILE_SIZE: Final[int] = 5 * 1024 * 1024          # 5 MB
MAX_TEXT_LENGTH: Final[int] = 120_000               # 120k characters
MAX_XML_DECOMPRESSION_BYTES: Final[int] = 10 * 1024 * 1024  # 10 MB
MAX_PDF_PAGES: Final[int] = 30
CACHE_MAX_SIZE: Final[int] = 100                    # Cache last 100 analyses

# Supported Formats
ALLOWED_EXTENSIONS: Final[set] = {".pdf", ".docx", ".doc", ".txt", ".md"}

# Pre-indexed Role Competency Database
ROLE_KEYWORD_DATABASE: Final[Dict[str, Dict[str, List[str]]]] = {
    "Software Engineer": {
        "required": ["data structures", "algorithms", "git", "ci/cd", "unit testing", "system design", "rest api"],
        "recommended": ["docker", "kubernetes", "agile", "microservices", "sql", "nosql", "linux", "cloud"]
    },
    "Frontend Developer": {
        "required": ["javascript", "react", "html5", "css3", "typescript", "responsive design", "state management"],
        "recommended": ["next.js", "tailwind css", "webpack", "vite", "web performance", "accessibility", "jest", "cypress"]
    },
    "Backend Developer": {
        "required": ["python", "node.js", "java", "sql", "postgresql", "restful apis", "database design"],
        "recommended": ["docker", "redis", "kafka", "graphql", "microservices", "fastapi", "spring boot", "aws"]
    },
    "Full Stack Developer": {
        "required": ["javascript", "react", "node.js", "python", "sql", "git", "rest apis"],
        "recommended": ["typescript", "docker", "aws", "nosql", "ci/cd", "next.js", "tailwind", "system design"]
    },
    "Data Scientist": {
        "required": ["python", "machine learning", "pandas", "numpy", "sql", "scikit-learn", "data visualization"],
        "recommended": ["tensorflow", "pytorch", "deep learning", "statistics", "seaborn", "tableau", "bigquery", "feature engineering"]
    },
    "Machine Learning Engineer": {
        "required": ["python", "pytorch", "tensorflow", "deep learning", "mlops", "model deployment", "scikit-learn"],
        "recommended": ["docker", "kubernetes", "cuda", "onnx", "hugging face", "vector databases", "ci/cd for ml"]
    },
    "AI Engineer": {
        "required": ["python", "llms", "prompt engineering", "langchain", "transformers", "vector databases", "api integration"],
        "recommended": ["rag", "fine-tuning", "fastapi", "docker", "agentic workflows", "embeddings", "gemini api"]
    },
    "Product Manager": {
        "required": ["product strategy", "agile", "scrum", "user research", "roadmapping", "kpi tracking", "stakeholder management"],
        "recommended": ["a/b testing", "sql", "jira", "wireframing", "go-to-market", "okrs", "customer journey mapping"]
    },
    "UX/UI Designer": {
        "required": ["figma", "wireframing", "prototyping", "user research", "usability testing", "design systems"],
        "recommended": ["adobe xd", "accessibility", "wcag", "information architecture", "interaction design", "responsive design"]
    },
    "DevOps Engineer": {
        "required": ["docker", "kubernetes", "ci/cd", "terraform", "linux", "aws", "git"],
        "recommended": ["ansible", "prometheus", "grafana", "helm", "bash", "jenkins", "infrastructure as code", "azure"]
    },
    "Cloud Engineer": {
        "required": ["aws", "azure", "gcp", "cloud architecture", "networking", "security", "terraform"],
        "recommended": ["serverless", "iam", "cloudformation", "cost optimization", "docker", "vpn", "linux"]
    },
    "Cybersecurity Analyst": {
        "required": ["network security", "vulnerability assessment", "incident response", "siem", "firewalls", "risk management"],
        "recommended": ["wireshark", "penetration testing", "nist framework", "soc", "cryptography", "zero trust", "iso 27001"]
    },
    "Mobile App Developer": {
        "required": ["react native", "flutter", "swift", "kotlin", "mobile ui", "rest apis", "app store deployment"],
        "recommended": ["state management", "offline storage", "push notifications", "ci/cd for mobile", "firebase", "sqlite"]
    },
    "Business Analyst": {
        "required": ["requirements gathering", "process modeling", "data analysis", "sql", "excel", "stakeholder communication"],
        "recommended": ["tableau", "power bi", "bpmn", "agile", "user stories", "jira", "cost-benefit analysis"]
    }
}

ACTION_VERBS: Final[List[str]] = [
    "spearheaded", "architected", "engineered", "optimized", "developed", "deployed",
    "implemented", "accelerated", "automated", "streamlined", "orchestrated", "reduced",
    "increased", "boosted", "delivered", "mentored", "designed", "scaled", "negotiated"
]

WEAK_PHRASES: Final[List[str]] = [
    "responsible for", "helped with", "worked on", "assisted in", "participated in",
    "handled tasks", "duties included", "familiar with", "involved in"
]
