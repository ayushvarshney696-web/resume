import { useState, useEffect, useCallback, useMemo } from "react";
import { Target } from "lucide-react";
import "./App.css";

// Modular UI Components
import Navbar from "./components/Navbar";
import RoleAndPersonaSection from "./components/RoleAndPersonaSection";
import ResumeInputSection from "./components/ResumeInputSection";
import ScoreHeroCard from "./components/ScoreHeroCard";
import StrengthsWeaknessesGrid from "./components/StrengthsWeaknessesGrid";
import KeywordGapSection from "./components/KeywordGapSection";
import BulletRewritesSection from "./components/BulletRewritesSection";
import ActionPlanSection from "./components/ActionPlanSection";
import InterviewQuestionsSection from "./components/InterviewQuestionsSection";
import SettingsModal from "./components/SettingsModal";

// Utilities
import { generateResumeReportPdf } from "./utils/pdfGenerator";

// Smart API URL Normalization
const rawBase = (import.meta.env.VITE_API_BASE_URL || "").trim();
const API_BASE = !rawBase
  ? "/api"
  : rawBase.replace(/\/+$/, "").endsWith("/api")
  ? rawBase.replace(/\/+$/, "")
  : `${rawBase.replace(/\/+$/, "")}/api`;

const PERSONAS = [
  {
    id: "Career Coach",
    title: "Career Coach",
    icon: "🎓",
    tagline: "Supportive mentor focusing on growth, career trajectory & soft skills"
  },
  {
    id: "Strict ATS Scanner",
    title: "Strict ATS Scanner",
    icon: "🤖",
    tagline: "Rigorous algorithmic scan for parsing errors, keywords & ATS rejection risks"
  },
  {
    id: "Technical Hiring Manager",
    title: "Tech Hiring Lead",
    icon: "💻",
    tagline: "Focuses on architecture, system design, modern stack mastery & code standards"
  },
  {
    id: "Executive Recruiter",
    title: "Executive Recruiter",
    icon: "💼",
    tagline: "Evaluates business ROI, revenue impact, metrics & executive presence"
  }
];

const JOB_ROLES = [
  "Software Engineer",
  "Frontend Developer",
  "Backend Developer",
  "Full Stack Developer",
  "Data Scientist",
  "Machine Learning Engineer",
  "AI Engineer",
  "Product Manager",
  "UX/UI Designer",
  "DevOps Engineer",
  "Cloud Engineer",
  "Cybersecurity Analyst",
  "Mobile App Developer",
  "Business Analyst",
  "Custom"
];

export default function App() {
  const [activeTab, setActiveTab] = useState("upload");
  const [selectedPersona, setSelectedPersona] = useState("Career Coach");
  const [selectedJobRole, setSelectedJobRole] = useState("Software Engineer");
  const [customJobRole, setCustomJobRole] = useState("");
  const [jobDescription, setJobDescription] = useState("");
  const [resumeFile, setResumeFile] = useState(null);
  const [pastedText, setPastedText] = useState("");
  const [userApiKey, setUserApiKey] = useState(
    () => localStorage.getItem("ai_resume_api_key") || ""
  );
  const [showSettings, setShowSettings] = useState(false);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [analysisResult, setAnalysisResult] = useState(null);
  const [copied, setCopied] = useState(false);
  const [sampleResumes, setSampleResumes] = useState({});
  const [errorMessage, setErrorMessage] = useState("");

  const finalJobRole = useMemo(
    () => (selectedJobRole === "Custom" ? customJobRole : selectedJobRole),
    [selectedJobRole, customJobRole]
  );

  const hasInput = useMemo(
    () => (activeTab === "upload" ? Boolean(resumeFile) : Boolean(pastedText.trim())),
    [activeTab, resumeFile, pastedText]
  );

  useEffect(() => {
    fetch(`${API_BASE}/sample-resumes`)
      .then((res) => (res.ok ? res.json() : {}))
      .then((data) => setSampleResumes(data))
      .catch(() => {});
  }, []);

  const handleSaveApiKey = useCallback((key) => {
    setUserApiKey(key);
    if (key.trim()) {
      localStorage.setItem("ai_resume_api_key", key.trim());
    } else {
      localStorage.removeItem("ai_resume_api_key");
    }
    setShowSettings(false);
  }, []);

  const handleLoadSample = useCallback((key) => {
    const sample = sampleResumes[key];
    if (!sample) return;
    setActiveTab("paste");
    setPastedText(sample.text);
    if (JOB_ROLES.includes(sample.role)) {
      setSelectedJobRole(sample.role);
    } else {
      setSelectedJobRole("Custom");
      setCustomJobRole(sample.role);
    }
    setErrorMessage("");
  }, [sampleResumes]);

  const handleFileChange = useCallback((e) => {
    if (e.target.files && e.target.files[0]) {
      setResumeFile(e.target.files[0]);
      setErrorMessage("");
    }
  }, []);

  const runAnalysis = useCallback(async () => {
    if (!finalJobRole.trim()) {
      setErrorMessage("Please select or enter a target job role.");
      return;
    }
    if (!hasInput) {
      setErrorMessage(
        activeTab === "upload"
          ? "Please select a resume file to upload (PDF, DOCX, TXT)."
          : "Please paste your resume text."
      );
      return;
    }

    setIsAnalyzing(true);
    setErrorMessage("");

    try {
      let res;
      if (activeTab === "upload" && resumeFile) {
        const formData = new FormData();
        formData.append("resume", resumeFile);
        formData.append("job_role", finalJobRole);
        formData.append("job_description", jobDescription);
        formData.append("persona", selectedPersona);
        if (userApiKey) formData.append("api_key", userApiKey);

        res = await fetch(`${API_BASE}/analyze`, {
          method: "POST",
          body: formData
        });
      } else {
        const payload = {
          resume_text: pastedText,
          job_role: finalJobRole,
          job_description: jobDescription,
          persona: selectedPersona,
          api_key: userApiKey || null
        };

        res = await fetch(`${API_BASE}/analyze-text`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(payload)
        });
      }

      if (!res.ok) {
        const errData = await res.json().catch(() => ({}));
        throw new Error(errData.detail || "Analysis request failed.");
      }

      const data = await res.json();
      setAnalysisResult(data);
    } catch (err) {
      setErrorMessage(err.message || "Failed to analyze resume. Please try again.");
    } finally {
      setIsAnalyzing(false);
    }
  }, [finalJobRole, hasInput, activeTab, resumeFile, pastedText, jobDescription, selectedPersona, userApiKey]);

  const copyToClipboard = useCallback(() => {
    if (!analysisResult) return;
    const textToCopy = analysisResult.raw_markdown || JSON.stringify(analysisResult, null, 2);
    navigator.clipboard.writeText(textToCopy);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  }, [analysisResult]);

  const handleDownloadPdf = useCallback(() => {
    generateResumeReportPdf(analysisResult, finalJobRole, selectedPersona);
  }, [analysisResult, finalJobRole, selectedPersona]);

  return (
    <div className="main-wrapper">
      <Navbar
        onOpenSettings={() => setShowSettings(true)}
        isApiKeyConfigured={Boolean(userApiKey)}
      />

      <main className="workspace-container">
        {/* Left Column: Configuration & Input */}
        <section className="input-column" aria-label="Resume configuration and input">
          <div className="panel-card">
            <RoleAndPersonaSection
              jobRoles={JOB_ROLES}
              selectedJobRole={selectedJobRole}
              setSelectedJobRole={setSelectedJobRole}
              customJobRole={customJobRole}
              setCustomJobRole={setCustomJobRole}
              personas={PERSONAS}
              selectedPersona={selectedPersona}
              setSelectedPersona={setSelectedPersona}
              jobDescription={jobDescription}
              setJobDescription={setJobDescription}
            />

            <ResumeInputSection
              onLoadSample={handleLoadSample}
              activeTab={activeTab}
              setActiveTab={setActiveTab}
              resumeFile={resumeFile}
              setResumeFile={setResumeFile}
              onFileChange={handleFileChange}
              pastedText={pastedText}
              setPastedText={setPastedText}
              isAnalyzing={isAnalyzing}
              onRunAnalysis={runAnalysis}
              hasInput={hasInput}
              errorMessage={errorMessage}
              selectedPersona={selectedPersona}
            />
          </div>
        </section>

        {/* Right Column: AI Assistant Report Dashboard */}
        <section
          className="results-column"
          aria-label="Analysis report results"
          aria-live="polite"
        >
          {analysisResult ? (
            <div className="results-panel">
              <ScoreHeroCard
                analysisResult={analysisResult}
                onDownloadPdf={handleDownloadPdf}
                onCopyMarkdown={copyToClipboard}
                copied={copied}
              />

              <div className="report-card">
                <h3 className="section-title">
                  <Target size={18} className="section-icon" aria-hidden="true" /> Executive Assessment
                </h3>
                <p className="summary-text">{analysisResult.summary}</p>
              </div>

              <StrengthsWeaknessesGrid
                strengths={analysisResult.strengths}
                weaknesses={analysisResult.weaknesses}
              />

              <KeywordGapSection
                matchedKeywords={analysisResult.matched_keywords}
                missingKeywords={analysisResult.missing_keywords}
              />

              <BulletRewritesSection
                bulletImprovements={analysisResult.bullet_improvements}
              />

              <ActionPlanSection
                actionPlan={analysisResult.action_plan}
              />

              <InterviewQuestionsSection
                interviewQuestions={analysisResult.interview_questions}
              />
            </div>
          ) : (
            <div className="placeholder-panel">
              <div className="placeholder-content">
                <span className="placeholder-hero-icon" aria-hidden="true">📄</span>
                <h3 className="placeholder-title">Ready to Review Your Resume</h3>
                <p className="placeholder-text">
                  Choose your target role, select an AI advisor persona, and upload or paste your resume on the left.
                </p>
                <div className="feature-checklist">
                  <div className="check-item">✓ Multi-Factor ATS Scoring (0-100)</div>
                  <div className="check-item">✓ Real-time Keyword Gap Detection</div>
                  <div className="check-item">✓ Google XYZ Impact Bullet Rewrites</div>
                  <div className="check-item">✓ High-Fidelity Multi-Page PDF Export</div>
                  <div className="check-item">✓ Works 100% Offline or with Gemini AI</div>
                </div>
              </div>
            </div>
          )}
        </section>
      </main>

      <SettingsModal
        show={showSettings}
        onClose={() => setShowSettings(false)}
        currentKey={userApiKey}
        onSaveKey={handleSaveApiKey}
      />
    </div>
  );
}
