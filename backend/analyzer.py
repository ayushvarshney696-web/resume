import os
import re
import json
from typing import Dict, List, Optional, Tuple
from models import AnalysisResult, CategoryScores, WeaknessItem, BulletImprovement, InterviewQuestion

ROLE_KEYWORD_DATABASE: Dict[str, Dict[str, List[str]]] = {
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
        "recommended": ["rag", "fine-tuning", "fastapi", "docker", "agentic workflows", "embeddings", "openai/gemini api"]
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

ACTION_VERBS = [
    "spearheaded", "architected", "engineered", "optimized", "developed", "deployed",
    "implemented", "accelerated", "automated", "streamlined", "orchestrated", "reduced",
    "increased", "boosted", "delivered", "mentored", "designed", "scaled", "negotiated"
]

WEAK_PHRASES = [
    "responsible for", "helped with", "worked on", "assisted in", "participated in",
    "handled tasks", "duties included", "familiar with", "involved in"
]

class ResumeAnalyzer:
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
        Analyze resume using Gemini AI if key is available;
        otherwise use the intelligent offline ATS & Career heuristic engine.
        """
        active_key = (user_api_key or self.default_api_key or "").strip()

        # Try Gemini AI if a key appears present
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
                    return ai_result
            except Exception as e:
                print(f"Gemini AI evaluation failed ({str(e)}), falling back to offline ATS Engine.")

        # Robust, high-fidelity fallback ATS & Heuristic Engine
        return self._analyze_offline_engine(
            resume_text=resume_text,
            job_role=job_role,
            job_description=job_description,
            persona=persona
        )

    def _analyze_with_gemini(
        self,
        resume_text: str,
        job_role: str,
        job_description: str,
        persona: str,
        api_key: str
    ) -> Optional[AnalysisResult]:
        """Call Gemini model via google.genai or google.generativeai."""
        persona_instructions = {
            "Career Coach": "Adopt an encouraging, growth-oriented mentor persona. Highlight latent potential, recommend high-value certifications, and focus on practical steps to elevate confidence and skills.",
            "Strict ATS Scanner": "Adopt a rigorous, automated ATS scanner persona. Scrutinize keyword density, standard section headers, parsing readability, and flag formatting or vague descriptions with zero tolerance.",
            "Technical Hiring Manager": "Adopt an experienced Lead Architect / VP of Engineering persona. Evaluate technical depth, system design evidence, codebase maintainability, production scalability, and modern stack mastery.",
            "Executive Recruiter": "Adopt an executive headhunter persona. Focus heavily on business ROI, quantifiable metrics, scale, revenue acceleration, cost reductions, and senior leadership presence."
        }
        persona_guide = persona_instructions.get(persona, persona_instructions["Career Coach"])

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
        # 1. Try google.genai
        try:
            from google import genai
            client = genai.Client(api_key=api_key)
            response = client.models.generate_content(
                model="gemini-2.0-flash",
                contents=prompt
            )
            response_text = response.text or ""
        except Exception:
            # 2. Try google.generativeai
            import google.generativeai as genai_legacy
            genai_legacy.configure(api_key=api_key)
            model = genai_legacy.GenerativeModel("gemini-1.5-flash")
            response = model.generate_content(prompt)
            response_text = response.text or ""

        if not response_text:
            return None

        # Clean JSON markdown fences
        clean_json = response_text.strip()
        if "```json" in clean_json:
            clean_json = clean_json.split("```json", 1)[1].split("```", 1)[0].strip()
        elif "```" in clean_json:
            clean_json = clean_json.split("```", 1)[1].split("```", 1)[0].strip()

        data = json.loads(clean_json)
        raw_markdown = self._generate_markdown_report(data, persona, job_role, "Gemini 2.0 Flash AI")

        return AnalysisResult(
            success=True,
            engine="Gemini 2.0 Flash AI",
            overall_score=int(data.get("overall_score", 75)),
            category_scores=CategoryScores(**data.get("category_scores", {
                "role_relevance": 75,
                "impact_quantification": 70,
                "ats_readability": 80,
                "skills_alignment": 75
            })),
            persona=persona,
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
        Deep deterministic ATS and NLP scoring engine.
        Evaluates keyword alignment, quantification ratio, action verbs,
        section structure, and persona-specific recommendations.
        """
        text_lower = resume_text.lower()
        
        # 1. Target Role & Keyword matching
        role_data = ROLE_KEYWORD_DATABASE.get(job_role, {
            "required": ["problem solving", "communication", "git", "project management", "collaboration"],
            "recommended": ["agile", "documentation", "leadership", "analysis", "system design"]
        })
        
        expected_keywords = list(role_data["required"] + role_data["recommended"])
        
        # Also extract keywords from user-provided job description
        if job_description.strip():
            desc_words = re.findall(r"\b[a-zA-Z]{3,}\b", job_description.lower())
            custom_terms = [w for w in set(desc_words) if len(w) > 4 and w not in ["experience", "responsibilities", "requirements", "candidate", "skills", "ability"]]
            expected_keywords.extend(custom_terms[:8])
            
        expected_keywords = list(dict.fromkeys(expected_keywords))  # deduplicate
        
        matched_keywords = [kw for kw in expected_keywords if kw in text_lower]
        missing_keywords = [kw for kw in expected_keywords if kw not in text_lower]
        
        kw_match_ratio = len(matched_keywords) / max(len(expected_keywords), 1)
        skills_score = min(100, int(kw_match_ratio * 105))
        
        # 2. Metric & Impact Quantification scoring
        metric_matches = re.findall(
            r"(\b\d+%\b|\$\d+[\d,]*\b|\b\d+x\b|\b\d+[\d,]*\+?\b|\b\d+[\d,]*\s*(?:users|clients|ms|seconds|million|billion|downloads|queries|rps))",
            text_lower
        )
        metric_count = len(metric_matches)
        
        action_verb_count = sum(1 for verb in ACTION_VERBS if re.search(r"\b" + verb + r"\b", text_lower))
        weak_phrase_matches = [p for p in WEAK_PHRASES if p in text_lower]
        
        # Base impact score from presence of active experience and quantified outcomes
        base_impact = 40 if "experience" in text_lower else 20
        impact_score = base_impact + (metric_count * 8) + (action_verb_count * 5) - (len(weak_phrase_matches) * 6)
        impact_score = max(25, min(98, int(impact_score)))
        
        # 3. Section and Structure Readability scoring
        sections = {
            "Contact Info / Email": bool(re.search(r"[\w\.-]+@[\w\.-]+\.\w+", resume_text)),
            "Summary / Objective": bool(re.search(r"\b(summary|objective|profile|about me)\b", text_lower)),
            "Experience / Work History": bool(re.search(r"\b(experience|employment|work history|professional background)\b", text_lower)),
            "Education": bool(re.search(r"\b(education|university|college|b\.tech|bachelor|master|degree)\b", text_lower)),
            "Skills": bool(re.search(r"\b(skills|technical skills|competencies|technologies)\b", text_lower)),
            "Projects": bool(re.search(r"\b(projects|personal projects|portfolio|key achievements)\b", text_lower))
        }
        
        found_sections = sum(1 for present in sections.values() if present)
        readability_score = min(100, int((found_sections / len(sections)) * 90) + 10)
        
        # 4. Role Relevance
        relevance_score = min(100, int((skills_score * 0.65) + (impact_score * 0.35)))
        
        # 5. Composite Overall Score
        overall_score = int(
            (relevance_score * 0.35) +
            (skills_score * 0.30) +
            (impact_score * 0.20) +
            (readability_score * 0.15)
        )
        
        # Persona weighting adjustments
        if persona == "Strict ATS Scanner":
            overall_score = max(30, overall_score - 5)  # Tougher ATS grading
        elif persona == "Career Coach":
            overall_score = min(98, overall_score + 3)  # More encouraging
        
        # Generate Strengths
        strengths = []
        if matched_keywords:
            strengths.append(f"Strong alignment with foundational {job_role} competencies ({', '.join(matched_keywords[:4])}).")
        if metric_count >= 2:
            strengths.append(f"Demonstrated impact with {metric_count}+ quantified metrics and performance outcomes.")
        if action_verb_count >= 3:
            strengths.append("Effective use of active, assertive verbs that convey leadership and ownership.")
        if sections["Experience / Work History"] and sections["Skills"]:
            strengths.append("Clear structural hierarchy that standard ATS parsers can easily tokenize.")
        if not strengths:
            strengths.append(f"Clear intent towards {job_role} with demonstrable foundational background.")
            strengths.append("Resume contains readable section flow suitable for human and machine review.")

        # Generate Weaknesses
        weaknesses = []
        if missing_keywords:
            weaknesses.append(WeaknessItem(
                issue="Missing Core Role Keywords",
                description=f"Your resume lacks mentions of key industry terms: {', '.join(missing_keywords[:4])}. ATS filters may rank your profile lower.",
                severity="high"
            ))
        if metric_count < 2:
            weaknesses.append(WeaknessItem(
                issue="Low Quantifiable Metrics",
                description="Descriptions focus heavily on job responsibilities rather than measurable business outcomes (% improved, $ saved, latency reduced).",
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
                description="Add a 3-line professional elevator pitch highlighting years of experience, core tech stack, and notable wins.",
                severity="low"
            ))

        # Generate Actionable Bullet Rewrites
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

        # Generate Action Plan based on persona
        action_plan = [
            f"Embed missing top keywords ({', '.join(missing_keywords[:3]) if missing_keywords else 'modern design patterns'}) into your Skills and Project bullet points.",
            "Transform every bullet point into the Google XYZ formula: 'Accomplished [X], as measured by [Y], by doing [Z]'.",
            f"Tailor your top headline to explicitly state: '{job_role} | {', '.join(matched_keywords[:3]) if matched_keywords else 'Technical Specialist'}'.",
            "Prepare code walkthroughs and architectural trade-off rationales for your featured projects."
        ]

        # Tailored Interview Questions
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

        # Executive Summary
        summary = (
            f"Candidate displays strong baseline capabilities for a {job_role} position with an overall ATS fit score of {overall_score}/100. "
            f"The profile features solid {matched_keywords[0] if matched_keywords else 'technical'} foundation, but needs more quantified metrics and targeted inclusion of keywords like {', '.join(missing_keywords[:2]) if missing_keywords else 'modern cloud practices'} to maximize interview callbacks."
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
        
        md = []
        md.append(f"# 🎯 Resume Review & ATS Strategy Report")
        md.append(f"**Target Role:** `{job_role}` | **Advisor Persona:** `{persona}` | **Engine:** `{engine}`\n")
        md.append(f"## 🏆 Overall ATS Match Score: **{score} / 100**\n")
        
        md.append("### 📊 Dimension Scores")
        md.append(f"- **Role Relevance & Alignment:** {cats.get('role_relevance', 75)}/100")
        md.append(f"- **Impact & Quantification:** {cats.get('impact_quantification', 70)}/100")
        md.append(f"- **ATS Readability & Structure:** {cats.get('ats_readability', 85)}/100")
        md.append(f"- **Skills Alignment:** {cats.get('skills_alignment', 80)}/100\n")
        
        md.append(f"### 📝 Executive Summary\n{data.get('summary', '')}\n")
        
        md.append("### ✅ Key Strengths")
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
