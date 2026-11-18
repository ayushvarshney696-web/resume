"""Resume analysis module implementing multi-factor ATS evaluation and LLM integration."""

import os
import re
import json
import logging
from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Tuple, Set

from models import AnalysisResult, CategoryScores, WeaknessItem, BulletImprovement, InterviewQuestion
from config import ROLE_KEYWORD_DATABASE, ACTION_VERBS, WEAK_PHRASES
from cache import analysis_cache

logger = logging.getLogger("ai_resume_reviewer.analyzer")
if not logger.handlers:
    handler = logging.StreamHandler()
    handler.setFormatter(logging.Formatter("[%(asctime)s] [%(levelname)s] [%(name)s]: %(message)s"))
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)

# Pre-compiled high-efficiency regex patterns
METRIC_REGEX = re.compile(
    r"(\b\d+%\b|\$\d+[\d,]*\b|\b\d+x\b|\b\d+[\d,]*\+?\b|\b\d+[\d,]*\s*(?:users|clients|ms|seconds|million|billion|downloads|queries|rps))",
    re.IGNORECASE
)
EMAIL_REGEX = re.compile(r"[\w\.-]+@[\w\.-]+\.\w+")
YEARS_EXP_REGEX = re.compile(r"(\d+)\+?\s*(?:years?|yrs?)\s*(?:of)?\s*(?:experience)?", re.IGNORECASE)
WORDS_REGEX = re.compile(r"\b[a-zA-Z0-9_.+#-]+\b")

SECTION_PATTERNS = {
    "Contact Info / Email": EMAIL_REGEX,
    "Summary / Objective": re.compile(r"\b(summary|objective|profile|about me|professional summary)\b", re.IGNORECASE),
    "Experience / Work History": re.compile(r"\b(experience|employment|work history|professional background|career history)\b", re.IGNORECASE),
    "Education": re.compile(r"\b(education|university|college|b\.tech|bachelor|master|degree|phd|diploma)\b", re.IGNORECASE),
    "Skills": re.compile(r"\b(skills|technical skills|competencies|technologies|stack|tools)\b", re.IGNORECASE),
    "Projects": re.compile(r"\b(projects|personal projects|portfolio|key achievements|open source)\b", re.IGNORECASE)
}

ACTION_VERB_PATTERNS = [re.compile(r"\b" + verb + r"\b", re.IGNORECASE) for verb in ACTION_VERBS]


# =====================================================================
# Strategy Pattern: Persona Evaluators
# =====================================================================
class PersonaStrategy(ABC):
    """Abstract Strategy representing an evaluation persona."""

    @property
    @abstractmethod
    def name(self) -> str:
        """Persona display name."""
        pass

    @property
    @abstractmethod
    def prompt_guidance(self) -> str:
        """Guidance instructions injected into LLM prompt."""
        pass

    @abstractmethod
    def adjust_score(self, base_score: int, impact_score: int, relevance_score: int) -> int:
        """Persona-specific algorithmic score weighting."""
        pass


class CareerCoachStrategy(PersonaStrategy):
    @property
    def name(self) -> str:
        return "Career Coach"

    @property
    def prompt_guidance(self) -> str:
        return "Adopt an encouraging, growth-oriented mentor persona. Highlight latent potential, recommend high-value certifications, and focus on practical steps to elevate confidence and skills."

    def adjust_score(self, base_score: int, impact_score: int, relevance_score: int) -> int:
        return min(98, base_score + 4)


class StrictATSScannerStrategy(PersonaStrategy):
    @property
    def name(self) -> str:
        return "Strict ATS Scanner"

    @property
    def prompt_guidance(self) -> str:
        return "Adopt a rigorous, automated ATS scanner persona. Scrutinize keyword density, standard section headers, parsing readability, and flag formatting or vague descriptions with zero tolerance."

    def adjust_score(self, base_score: int, impact_score: int, relevance_score: int) -> int:
        return max(25, base_score - 6)


class TechnicalHiringManagerStrategy(PersonaStrategy):
    @property
    def name(self) -> str:
        return "Technical Hiring Manager"

    @property
    def prompt_guidance(self) -> str:
        return "Adopt an experienced Lead Architect / VP of Engineering persona. Evaluate technical depth, system design evidence, codebase maintainability, production scalability, and modern stack mastery."

    def adjust_score(self, base_score: int, impact_score: int, relevance_score: int) -> int:
        return int((relevance_score * 0.6) + (impact_score * 0.4))


class ExecutiveRecruiterStrategy(PersonaStrategy):
    @property
    def name(self) -> str:
        return "Executive Recruiter"

    @property
    def prompt_guidance(self) -> str:
        return "Adopt an executive headhunter persona. Focus heavily on business ROI, quantifiable metrics, scale, revenue acceleration, cost reductions, and senior leadership presence."

    def adjust_score(self, base_score: int, impact_score: int, relevance_score: int) -> int:
        return int((impact_score * 0.55) + (relevance_score * 0.45))


PERSONA_STRATEGIES: Dict[str, PersonaStrategy] = {
    "Career Coach": CareerCoachStrategy(),
    "Strict ATS Scanner": StrictATSScannerStrategy(),
    "Technical Hiring Manager": TechnicalHiringManagerStrategy(),
    "Executive Recruiter": ExecutiveRecruiterStrategy()
}


# =====================================================================
# Main Resume Analyzer Service
# =====================================================================
class ResumeAnalyzer:
    """
    Core resume review service combining Gemini Generative AI
    with high-efficiency deterministic NLP fallback logic and in-memory LRU caching.
    """

    def __init__(self):
        self.default_api_key = os.getenv("GEMINI_API_KEY", "").strip()

    def analyze(
        self,
        resume_text: str,
        job_role: str = "Software Engineer",
        job_description: str = "",
        persona: str = "Career Coach",
        user_api_key: Optional[str] = None
    ) -> AnalysisResult:
        """
        Evaluate candidate resume with caching, LLM execution, and offline fallback.

        Args:
            resume_text: Raw text of the resume.
            job_role: Target job title.
            job_description: Optional target job description for contextual matching.
            persona: Advisor persona name.
            user_api_key: Optional override for Gemini API key.

        Returns:
            AnalysisResult containing scores, strengths, weaknesses, and rewrites.

        Time Complexity: O(N) where N is text length.
        Space Complexity: O(K) where K is number of unique keywords.
        """
        cache_key = analysis_cache.compute_key(
            resume_text, job_role, job_description, persona, user_api_key
        )
        cached = analysis_cache.get(cache_key)
        if cached:
            logger.info("Cache hit for analysis key: %s...", cache_key[:12])
            return cached

        active_key = (user_api_key or self.default_api_key or "").strip()

        # Try Gemini AI if a non-placeholder key is provided
        if active_key and not active_key.startswith("AIzaAIzaSyBaVJE0"):
            try:
                ai_result = self._analyze_with_gemini(
                    resume_text=resume_text,
                    job_role=job_role,
                    job_description=job_description,
                    persona=persona,
                    api_key=active_key
                )
                if ai_result:
                    analysis_cache.put(cache_key, ai_result)
                    return ai_result
            except Exception as e:
                logger.warning("Gemini AI evaluation failed (%s), falling back to offline ATS Engine.", str(e))

        # Deterministic Fallback Engine
        offline_result = self._analyze_offline_engine(
            resume_text=resume_text,
            job_role=job_role,
            job_description=job_description,
            persona=persona
        )
        analysis_cache.put(cache_key, offline_result)
        return offline_result

    def _determine_seniority(self, text_lower: str) -> str:
        """Detect candidate seniority from years of experience and titles."""
        years_matches = YEARS_EXP_REGEX.findall(text_lower)
        max_years = 0
        for y in years_matches:
            try:
                val = int(y)
                if val > max_years:
                    max_years = val
            except ValueError:
                pass

        if max_years >= 8 or re.search(r"\b(principal|staff|director|head of|lead architect|vp)\b", text_lower):
            return "Lead / Principal (8+ yrs)"
        elif max_years >= 5 or re.search(r"\b(senior|lead)\b", text_lower):
            return "Senior (5-8 yrs)"
        elif max_years >= 2 or re.search(r"\b(mid-level|intermediate)\b", text_lower):
            return "Mid-Level (2-5 yrs)"
        else:
            return "Junior (0-2 yrs)"

    def _analyze_with_gemini(
        self,
        resume_text: str,
        job_role: str,
        job_description: str,
        persona: str,
        api_key: str
    ) -> Optional[AnalysisResult]:
        strategy = PERSONA_STRATEGIES.get(persona, PERSONA_STRATEGIES["Career Coach"])
        persona_guide = strategy.prompt_guidance

        prompt = f"""
You are an expert AI Career Strategist and ATS Specialist acting with the persona: {persona}.
{persona_guide}

Analyze this resume for the target role: "{job_role}".
Job Description Context (if provided): "{job_description if job_description else 'Standard industry benchmarks for ' + job_role}"

You MUST respond strictly with a valid JSON object matching this schema:
{{
  "overall_score": <number 0-100>,
  "category_scores": {{
    "role_relevance": <number 0-100>,
    "impact_quantification": <number 0-100>,
    "ats_readability": <number 0-100>,
    "skills_alignment": <number 0-100>
  }},
  "persona": "{persona}",
  "seniority_level": "<Junior (0-2 yrs) | Mid-Level (2-5 yrs) | Senior (5-8 yrs) | Lead / Principal (8+ yrs)>",
  "ats_pass_probability": "<High (>80%) | Moderate (65-79%) | Low (<65%)>",
  "summary": "<2-3 sentence executive assessment>",
  "strengths": ["<strength 1>", "<strength 2>", "<strength 3>", "<strength 4>"],
  "weaknesses": [
    {{"issue": "<title>", "description": "<actionable explanation>", "severity": "high"|"medium"|"low"}}
  ],
  "matched_keywords": ["<keyword 1>", "<keyword 2>", "<keyword 3>"],
  "missing_keywords": ["<keyword 1>", "<keyword 2>", "<keyword 3>"],
  "bullet_improvements": [
    {{"original": "<weak bullet from resume>", "improved": "<enhanced Google XYZ formula rewrite>", "reason": "<why this converts better>"}}
  ],
  "action_plan": [
    "<Immediate action 1>",
    "<Immediate action 2>",
    "<Immediate action 3>",
    "<Longer term recommendation>"
  ],
  "interview_questions": [
    {{"question": "<targeted interview question based on resume gaps or projects>", "context": "<why hiring managers will ask this>"}}
  ]
}}

Resume Content:
\"\"\"
{resume_text[:6000]}
\"\"\"
"""
        response_text = ""
        try:
            from google import genai
            client = genai.Client(api_key=api_key)
            response = client.models.generate_content(
                model="gemini-2.0-flash",
                contents=prompt
            )
            response_text = response.text or ""
        except Exception:
            import google.generativeai as genai_legacy
            genai_legacy.configure(api_key=api_key)
            model = genai_legacy.GenerativeModel("gemini-1.5-flash")
            response = model.generate_content(prompt)
            response_text = response.text or ""

        if not response_text:
            return None

        clean_json = response_text.strip()
        if "```json" in clean_json:
            clean_json = clean_json.split("```json", 1)[1].split("```", 1)[0].strip()
        elif "```" in clean_json:
            clean_json = clean_json.split("```", 1)[1].split("```", 1)[0].strip()

        data = json.loads(clean_json)
        raw_markdown = self._generate_markdown_report(data, persona, job_role, "Gemini 2.0 Flash AI")

        score = int(data.get("overall_score", 75))
        pass_prob = "High (>80%)" if score >= 80 else ("Moderate (65-79%)" if score >= 65 else "Low (<65%)")

        return AnalysisResult(
            success=True,
            engine="Gemini 2.0 Flash AI",
            overall_score=score,
            category_scores=CategoryScores(**data.get("category_scores", {
                "role_relevance": 75,
                "impact_quantification": 70,
                "ats_readability": 80,
                "skills_alignment": 75
            })),
            persona=persona,
            seniority_level=data.get("seniority_level", self._determine_seniority(resume_text.lower())),
            ats_pass_probability=data.get("ats_pass_probability", pass_prob),
            word_count=len(WORDS_REGEX.findall(resume_text)),
            summary=data.get("summary", ""),
            strengths=data.get("strengths", []),
            weaknesses=[WeaknessItem(**w) for w in data.get("weaknesses", [])],
            matched_keywords=data.get("matched_keywords", []),
            missing_keywords=data.get("missing_keywords", []),
            bullet_improvements=[BulletImprovement(**b) for b in data.get("bullet_improvements", [])],
            action_plan=data.get("action_plan", []),
            interview_questions=[InterviewQuestion(**q) for q in data.get("interview_questions", [])],
            raw_markdown=raw_markdown
        )

    def _analyze_offline_engine(
        self,
        resume_text: str,
        job_role: str,
        job_description: str,
        persona: str
    ) -> AnalysisResult:
        """
        Deep deterministic ATS evaluation utilizing pre-compiled vectors and O(1) matching.
        """
        text_lower = resume_text.lower()
        words = WORDS_REGEX.findall(text_lower)
        word_count = len(words)
        seniority = self._determine_seniority(text_lower)

        strategy = PERSONA_STRATEGIES.get(persona, PERSONA_STRATEGIES["Career Coach"])

        # 1. Target Role & Keyword matching
        role_data = ROLE_KEYWORD_DATABASE.get(job_role, {
            "required": ["problem solving", "communication", "git", "project management", "collaboration"],
            "recommended": ["agile", "documentation", "leadership", "analysis", "system design"]
        })

        expected_keywords = list(role_data["required"] + role_data["recommended"])

        if job_description.strip():
            desc_words = WORDS_REGEX.findall(job_description.lower())
            custom_terms = [
                w for w in set(desc_words)
                if len(w) > 4 and w not in ["experience", "responsibilities", "requirements", "candidate", "skills", "ability"]
            ]
            expected_keywords.extend(custom_terms[:8])

        expected_keywords = list(dict.fromkeys(expected_keywords))

        # Fast keyword membership
        matched_keywords = [kw for kw in expected_keywords if kw in text_lower]
        missing_keywords = [kw for kw in expected_keywords if kw not in text_lower]

        kw_match_ratio = len(matched_keywords) / max(len(expected_keywords), 1)
        skills_score = min(100, int(kw_match_ratio * 105))

        # 2. Metric & Impact Quantification scoring
        metric_matches = METRIC_REGEX.findall(text_lower)
        metric_count = len(metric_matches)

        action_verb_count = sum(1 for pat in ACTION_VERB_PATTERNS if pat.search(text_lower))
        weak_phrase_matches = [p for p in WEAK_PHRASES if p in text_lower]

        base_impact = 40 if "experience" in text_lower else 20
        impact_score = base_impact + (metric_count * 8) + (action_verb_count * 5) - (len(weak_phrase_matches) * 6)
        impact_score = max(25, min(98, int(impact_score)))

        # 3. Section and Structure Readability scoring
        sections = {name: bool(pat.search(resume_text)) for name, pat in SECTION_PATTERNS.items()}
        found_sections = sum(1 for present in sections.values() if present)
        readability_score = min(100, int((found_sections / len(sections)) * 90) + 10)

        # 4. Role Relevance
        relevance_score = min(100, int((skills_score * 0.65) + (impact_score * 0.35)))

        # 5. Composite Base Score
        base_score = int(
            (relevance_score * 0.35) +
            (skills_score * 0.30) +
            (impact_score * 0.20) +
            (readability_score * 0.15)
        )

        # 6. Apply Strategy Pattern for Persona Weighting
        overall_score = strategy.adjust_score(base_score, impact_score, relevance_score)

        # Pass Probability
        pass_prob = "High (>80%)" if overall_score >= 80 else ("Moderate (65-79%)" if overall_score >= 65 else "Low (<65%)")

        # Key Strengths
        strengths = []
        if matched_keywords:
            strengths.append(f"Demonstrates strong foundation in {job_role} core proficiencies ({', '.join(matched_keywords[:4])}).")
        if metric_count >= 2:
            strengths.append(f"Features {metric_count}+ quantified metrics and performance outcomes.")
        if action_verb_count >= 3:
            strengths.append("Employs assertive, active power verbs conveying ownership and impact.")
        if sections["Experience / Work History"] and sections["Skills"]:
            strengths.append("Clear structural section hierarchy that automated ATS parsers tokenize smoothly.")
        if not strengths:
            strengths.append(f"Clear orientation towards {job_role} roles with baseline professional structure.")
            strengths.append("Standard readable typography and linear flow suitable for parsing.")

        # Weaknesses
        weaknesses = []
        if missing_keywords:
            weaknesses.append(WeaknessItem(
                issue="Missing Core Role Keywords",
                description=f"Your profile lacks mentions of high-demand industry keywords: {', '.join(missing_keywords[:4])}. ATS filters may rank your submission lower.",
                severity="high"
            ))
        if metric_count < 2:
            weaknesses.append(WeaknessItem(
                issue="Low Quantifiable Metrics",
                description="Bullet points focus on job duties rather than measurable outcomes (% improved, $ saved, latency reduced, users scaled).",
                severity="medium"
            ))
        if weak_phrase_matches:
            weaknesses.append(WeaknessItem(
                issue="Passive or Vague Phrasing",
                description=f"Detected passive phrasing like '{weak_phrase_matches[0]}'. Replace with high-impact power verbs.",
                severity="medium"
            ))
        if not sections["Summary / Objective"]:
            weaknesses.append(WeaknessItem(
                issue="Missing Targeted Professional Summary",
                description="Add a 3-line executive elevator pitch summarizing years of experience, core tech stack, and notable wins.",
                severity="low"
            ))

        # Bullet Rewrites (Google XYZ Formula)
        bullet_improvements = [
            BulletImprovement(
                original="Responsible for developing backend APIs and fixing bugs.",
                improved="Architected and deployed 15+ RESTful microservice endpoints in FastAPI, reducing API response times by 32% and eliminating critical production bugs.",
                reason="Converts passive responsibility into quantified architectural achievement using the Google XYZ formula."
            ),
            BulletImprovement(
                original="Worked with frontend team on web application features.",
                improved="Engineered 8+ responsive React components with TypeScript and Tailwind CSS, improving Lighthouse accessibility score to 98/100 for 50,000+ monthly active users.",
                reason="Specifies exact stack, measurable accessibility metric, and scale of end users."
            )
        ]

        # Strategic Action Plan
        action_plan = [
            f"Embed missing top keywords ({', '.join(missing_keywords[:3]) if missing_keywords else 'cloud architecture'}) into your Skills and Project bullet points.",
            "Transform every bullet point into the Google XYZ formula: 'Accomplished [X], as measured by [Y], by doing [Z]'.",
            f"Tailor your top headline to explicitly state: '{job_role} | {', '.join(matched_keywords[:3]) if matched_keywords else 'Technical Specialist'}'.",
            "Prepare code walkthroughs and architectural trade-off rationales for your featured projects."
        ]

        # Targeted Interview Questions
        interview_questions = [
            InterviewQuestion(
                question=f"Can you walk me through the most technically challenging problem you solved in your recent projects relating to {job_role}?",
                context="Hiring managers want to evaluate your depth of troubleshooting, trade-offs, and perseverance."
            ),
            InterviewQuestion(
                question="How do you balance delivering quick MVP features versus paying down architectural technical debt?",
                context="Assesses seniority, business alignment, and long-term code quality mindset."
            ),
            InterviewQuestion(
                question=f"How would you integrate {missing_keywords[0] if missing_keywords else 'CI/CD best practices'} into your current development workflow?",
                context="Probes areas where the resume indicated potential room for growth."
            )
        ]

        summary = (
            f"Candidate presents a {seniority} profile for {job_role} with an overall ATS fit score of {overall_score}/100 ({pass_prob} ATS pass probability). "
            f"The profile demonstrates competence in {matched_keywords[0] if matched_keywords else 'core technical skills'}, but needs additional metric quantification and targeted inclusion of {', '.join(missing_keywords[:2]) if missing_keywords else 'modern practices'} to maximize interview callbacks."
        )

        category_scores = CategoryScores(
            role_relevance=relevance_score,
            impact_quantification=impact_score,
            ats_readability=readability_score,
            skills_alignment=skills_score
        )

        raw_markdown = self._generate_markdown_report({
            "overall_score": overall_score,
            "category_scores": category_scores.model_dump(),
            "seniority_level": seniority,
            "ats_pass_probability": pass_prob,
            "summary": summary,
            "strengths": strengths,
            "weaknesses": [w.model_dump() for w in weaknesses],
            "matched_keywords": matched_keywords,
            "missing_keywords": missing_keywords,
            "bullet_improvements": [b.model_dump() for b in bullet_improvements],
            "action_plan": action_plan,
            "interview_questions": [q.model_dump() for q in interview_questions]
        }, persona, job_role, "Intelligent ATS Engine")

        return AnalysisResult(
            success=True,
            engine="Intelligent Built-in ATS Engine",
            overall_score=overall_score,
            category_scores=category_scores,
            persona=persona,
            seniority_level=seniority,
            ats_pass_probability=pass_prob,
            word_count=word_count,
            summary=summary,
            strengths=strengths,
            weaknesses=weaknesses,
            matched_keywords=matched_keywords,
            missing_keywords=missing_keywords,
            bullet_improvements=bullet_improvements,
            action_plan=action_plan,
            interview_questions=interview_questions,
            raw_markdown=raw_markdown
        )

    def _generate_markdown_report(self, data: dict, persona: str, job_role: str, engine: str) -> str:
        score = data.get("overall_score", 75)
        cats = data.get("category_scores", {})
        seniority = data.get("seniority_level", "Mid-Level")
        pass_prob = data.get("ats_pass_probability", "Moderate")

        md = [
            f"# 🎯 Resume Review & ATS Strategy Report",
            f"**Target Role:** `{job_role}` | **Advisor Persona:** `{persona}` | **Seniority Level:** `{seniority}`",
            f"**ATS Pass Probability:** `{pass_prob}` | **Engine:** `{engine}`\n",
            f"## 🏆 Overall ATS Match Score: **{score} / 100**\n",
            "### 📊 Dimension Scores",
            f"- **Role Relevance & Alignment:** {cats.get('role_relevance', 75)}/100",
            f"- **Impact & Quantification:** {cats.get('impact_quantification', 70)}/100",
            f"- **ATS Readability & Structure:** {cats.get('ats_readability', 85)}/100",
            f"- **Skills Alignment:** {cats.get('skills_alignment', 80)}/100\n",
            f"### 📝 Executive Summary\n{data.get('summary', '')}\n",
            "### ✅ Key Strengths"
        ]
        for s in data.get("strengths", []):
            md.append(f"- {s}")
        md.append("")

        md.append("### ⚠️ Critical Improvement Areas")
        for w in data.get("weaknesses", []):
            issue = w.get("issue", "Issue")
            desc = w.get("description", "")
            sev = w.get("severity", "medium").upper()
            md.append(f"- **[{sev}] {issue}:** {desc}")
        md.append("")

        matched = data.get("matched_keywords", [])
        missing = data.get("missing_keywords", [])
        if matched or missing:
            md.append("### 🔑 Keyword Gap Analysis")
            if matched:
                md.append(f"- **Found in Resume:** {', '.join(matched)}")
            if missing:
                md.append(f"- **Missing Recommended:** {', '.join(missing)}")
            md.append("")

        improvements = data.get("bullet_improvements", [])
        if improvements:
            md.append("### ✍️ Actionable Bullet Rewrites (Google XYZ Formula)")
            for item in improvements:
                md.append(f"- **Before:** _{item.get('original')}_")
                md.append(f"  **After:** **{item.get('improved')}**")
                md.append(f"  _Why it works:_ {item.get('reason')}\n")

        plan = data.get("action_plan", [])
        if plan:
            md.append("### 🚀 Strategic Action Plan")
            for idx, step in enumerate(plan, 1):
                md.append(f"{idx}. {step}")
            md.append("")

        questions = data.get("interview_questions", [])
        if questions:
            md.append("### 💡 Recommended Interview Prep Questions")
            for q in questions:
                md.append(f"- **Q:** {q.get('question')}")
                md.append(f"  _Context:_ {q.get('context')}")
            md.append("")

        return "\n".join(md)
