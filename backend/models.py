from pydantic import BaseModel, Field
from typing import List, Dict, Optional, Any

class CategoryScores(BaseModel):
    role_relevance: int = Field(ge=0, le=100, description="Alignment with target role & keywords")
    impact_quantification: int = Field(ge=0, le=100, description="Use of metrics, numbers, and impact verbs")
    ats_readability: int = Field(ge=0, le=100, description="Formatting, sections, and parseability")
    skills_alignment: int = Field(ge=0, le=100, description="Breadth and depth of required technical skills")

class WeaknessItem(BaseModel):
    issue: str
    description: str
    severity: str = "medium"  # high, medium, low

class BulletImprovement(BaseModel):
    original: str
    improved: str
    reason: str

class InterviewQuestion(BaseModel):
    question: str
    context: str

class AnalysisResult(BaseModel):
    success: bool = True
    engine: str = "Intelligent ATS Engine"
    overall_score: int = Field(ge=0, le=100)
    category_scores: CategoryScores
    persona: str = "Career Coach"
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
    resume_text: str
    job_role: str = "Software Engineer"
    job_description: Optional[str] = ""
    persona: Optional[str] = "Career Coach"
    api_key: Optional[str] = None
