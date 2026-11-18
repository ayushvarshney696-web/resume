from pydantic import BaseModel, Field
from typing import List, Dict, Optional, Any

class CategoryScores(BaseModel):
    role_relevance: int = Field(ge=0, le=100, description="Alignment with target role & keywords")
    impact_quantification: int = Field(ge=0, le=100, description="Use of metrics, numbers, and impact verbs")
    ats_readability: int = Field(ge=0, le=100, description="Formatting, sections, and parseability")
    skills_alignment: int = Field(ge=0, le=100, description="Breadth and depth of required technical skills")

class WeaknessItem(BaseModel):
    issue: str = Field(description="Short title of the weakness")
    description: str = Field(description="Detailed explanation with actionable fix")
    severity: str = Field(default="medium", description="Severity: high | medium | low")

class BulletImprovement(BaseModel):
    original: str = Field(description="Weak bullet point identified from resume")
    improved: str = Field(description="Polished bullet rewrite using Google XYZ formula")
    reason: str = Field(description="Why this rewrite converts better")

class InterviewQuestion(BaseModel):
    question: str = Field(description="Targeted interview question")
    context: str = Field(description="Why interviewers will ask this based on candidate gaps")

class AnalysisResult(BaseModel):
    success: bool = True
    engine: str = "Intelligent ATS Engine"
    overall_score: int = Field(ge=0, le=100)
    category_scores: CategoryScores
    persona: str = "Career Coach"
    seniority_level: str = "Mid-Level (2-5 yrs)"
    ats_pass_probability: str = "Moderate"
    word_count: int = 0
    summary: str
    strengths: List[str]
    weaknesses: List[WeaknessItem]
    matched_keywords: List[str]
    missing_keywords: List[str]
    bullet_improvements: List[BulletImprovement]
    action_plan: List[str]
    interview_questions: List[InterviewQuestion]
    raw_markdown: str

class TextAnalysisRequest(BaseModel):
    resume_text: str = Field(min_length=20, max_length=150000, description="Resume text content")
    job_role: str = Field(default="Software Engineer", max_length=100)
    job_description: Optional[str] = Field(default="", max_length=50000)
    persona: Optional[str] = Field(default="Career Coach", max_length=50)
    api_key: Optional[str] = Field(default=None, max_length=200)
