import { useState, useEffect } from "react";
import { PDFDocument, rgb, StandardFonts } from "pdf-lib";
import {
  FileText,
  UploadCloud,
  CheckCircle2,
  AlertTriangle,
  Download,
  Copy,
  Sparkles,
  RefreshCw,
  Target,
  Briefcase,
  Award,
  BookOpen,
  HelpCircle,
  Key,
  X,
  Check,
  UserCheck,
  Percent
} from "lucide-react";
import "./App.css";

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
  const [activeTab, setActiveTab] = useState("upload"); // 'upload' | 'paste'
  const [selectedPersona, setSelectedPersona] = useState("Career Coach");
  const [selectedJobRole, setSelectedJobRole] = useState("Software Engineer");
  const [customJobRole, setCustomJobRole] = useState("");
  const [jobDescription, setJobDescription] = useState("");
  const [resumeFile, setResumeFile] = useState(null);
  const [pastedText, setPastedText] = useState("");
  const [userApiKey, setUserApiKey] = useState(
    localStorage.getItem("ai_resume_api_key") || ""
  );
  const [showSettings, setShowSettings] = useState(false);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [analysisResult, setAnalysisResult] = useState(null);
  const [copied, setCopied] = useState(false);
  const [sampleResumes, setSampleResumes] = useState({});
  const [errorMessage, setErrorMessage] = useState("");

  const finalJobRole = selectedJobRole === "Custom" ? customJobRole : selectedJobRole;
  const hasInput = activeTab === "upload" ? Boolean(resumeFile) : Boolean(pastedText.trim());

  useEffect(() => {
    fetch(`${API_BASE}/sample-resumes`)
      .then((res) => (res.ok ? res.json() : {}))
      .then((data) => setSampleResumes(data))
      .catch(() => {});
  }, []);

  const handleSaveApiKey = (key) => {
    setUserApiKey(key);
    if (key.trim()) {
      localStorage.setItem("ai_resume_api_key", key.trim());
    } else {
      localStorage.removeItem("ai_resume_api_key");
    }
    setShowSettings(false);
  };

  const loadSample = (key) => {
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
  };

  const handleFileChange = (e) => {
    if (e.target.files && e.target.files[0]) {
      setResumeFile(e.target.files[0]);
      setErrorMessage("");
    }
  };

  const runAnalysis = async () => {
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
  };

  const copyToClipboard = () => {
    if (!analysisResult) return;
    const textToCopy = analysisResult.raw_markdown || JSON.stringify(analysisResult, null, 2);
    navigator.clipboard.writeText(textToCopy);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const downloadReportPdf = async () => {
    if (!analysisResult) return;

    try {
      const pdfDoc = await PDFDocument.create();
      const helvetica = await pdfDoc.embedFont(StandardFonts.Helvetica);
      const helveticaBold = await pdfDoc.embedFont(StandardFonts.HelveticaBold);

      const pageWidth = 595.28;
      const pageHeight = 841.89;
      const margin = 50;
      const contentWidth = pageWidth - margin * 2;

      let currentPage = pdfDoc.addPage([pageWidth, pageHeight]);
      let y = pageHeight - margin;

      const checkPageBreak = (neededHeight) => {
        if (y - neededHeight < margin + 30) {
          drawFooter(currentPage, helvetica, pdfDoc.getPageCount());
          currentPage = pdfDoc.addPage([pageWidth, pageHeight]);
          y = pageHeight - margin;
          drawMiniHeader(currentPage, helveticaBold);
          y -= 30;
        }
      };

      const drawFooter = (page, font, pageNum) => {
        page.drawText(`AI Resume Reviewer | Confidential Report | Page ${pageNum}`, {
          x: margin,
          y: margin - 15,
          size: 8,
          font,
          color: rgb(0.5, 0.5, 0.5)
        });
      };

      const drawMiniHeader = (page, font) => {
        page.drawText(`Target Role: ${finalJobRole} | Advisor: ${selectedPersona} | Score: ${analysisResult.overall_score}/100`, {
          x: margin,
          y: pageHeight - 35,
          size: 9,
          font,
          color: rgb(0.3, 0.4, 0.5)
        });
      };

      const writeWrapped = (text, size, font, color = rgb(0.1, 0.1, 0.1), lineSpacing = 1.3) => {
        const words = text.split(" ");
        let line = "";
        for (const word of words) {
          const testLine = line ? `${line} ${word}` : word;
          const textWidth = font.widthOfTextAtSize(testLine, size);
          if (textWidth > contentWidth) {
            checkPageBreak(size * lineSpacing);
            currentPage.drawText(line, { x: margin, y, size, font, color });
            y -= size * lineSpacing;
            line = word;
          } else {
            line = testLine;
          }
        }
        if (line) {
          checkPageBreak(size * lineSpacing);
          currentPage.drawText(line, { x: margin, y, size, font, color });
          y -= size * lineSpacing;
        }
      };

      // Banner
      currentPage.drawRectangle({
        x: margin,
        y: y - 55,
        width: contentWidth,
        height: 60,
        color: rgb(0.05, 0.35, 0.65)
      });

      currentPage.drawText("AI Resume Review & Career Strategy Report", {
        x: margin + 15,
        y: y - 25,
        size: 16,
        font: helveticaBold,
        color: rgb(1, 1, 1)
      });

      currentPage.drawText(`Target: ${finalJobRole}  |  Seniority: ${analysisResult.seniority_level || 'Mid'}  |  Score: ${analysisResult.overall_score}/100`, {
        x: margin + 15,
        y: y - 45,
        size: 9.5,
        font: helvetica,
        color: rgb(0.9, 0.95, 1)
      });

      y -= 75;

      // Executive Summary
      checkPageBreak(40);
      currentPage.drawText("EXECUTIVE ASSESSMENT", {
        x: margin,
        y,
        size: 12,
        font: helveticaBold,
        color: rgb(0.05, 0.35, 0.65)
      });
      y -= 16;
      writeWrapped(analysisResult.summary, 10, helvetica);
      y -= 14;

      // Dimension Scores
      checkPageBreak(50);
      currentPage.drawText("ATS DIMENSION SCORES", {
        x: margin,
        y,
        size: 12,
        font: helveticaBold,
        color: rgb(0.05, 0.35, 0.65)
      });
      y -= 16;
      const cats = analysisResult.category_scores || {};
      const scoreLine = `Role Relevance: ${cats.role_relevance || 0}/100  |  Impact & Metrics: ${cats.impact_quantification || 0}/100  |  ATS Readability: ${cats.ats_readability || 0}/100  |  Skills Match: ${cats.skills_alignment || 0}/100`;
      writeWrapped(scoreLine, 9, helveticaBold, rgb(0.2, 0.2, 0.2));
      y -= 14;

      // Strengths
      if (analysisResult.strengths?.length) {
        checkPageBreak(40);
        currentPage.drawText("KEY STRENGTHS", {
          x: margin,
          y,
          size: 12,
          font: helveticaBold,
          color: rgb(0.1, 0.5, 0.2)
        });
        y -= 16;
        for (const s of analysisResult.strengths) {
          writeWrapped(`•  ${s}`, 9.5, helvetica);
          y -= 4;
        }
        y -= 10;
      }

      // Weaknesses
      if (analysisResult.weaknesses?.length) {
        checkPageBreak(40);
        currentPage.drawText("CRITICAL IMPROVEMENT AREAS", {
          x: margin,
          y,
          size: 12,
          font: helveticaBold,
          color: rgb(0.7, 0.2, 0.1)
        });
        y -= 16;
        for (const w of analysisResult.weaknesses) {
          writeWrapped(`•  [${w.severity.toUpperCase()}] ${w.issue}: ${w.description}`, 9.5, helvetica);
          y -= 4;
        }
        y -= 10;
      }

      // Actionable Rewrites
      if (analysisResult.bullet_improvements?.length) {
        checkPageBreak(50);
        currentPage.drawText("GOOGLE XYZ FORMULA BULLET REWRITES", {
          x: margin,
          y,
          size: 12,
          font: helveticaBold,
          color: rgb(0.05, 0.35, 0.65)
        });
        y -= 16;
        for (const b of analysisResult.bullet_improvements) {
          writeWrapped(`Original: "${b.original}"`, 9, helvetica, rgb(0.4, 0.4, 0.4));
          writeWrapped(`Optimized: "${b.improved}"`, 9.5, helveticaBold, rgb(0.05, 0.3, 0.6));
          writeWrapped(`Why it works: ${b.reason}`, 8.5, helvetica, rgb(0.3, 0.3, 0.3));
          y -= 8;
        }
        y -= 6;
      }

      // Strategic Action Plan
      if (analysisResult.action_plan?.length) {
        checkPageBreak(40);
        currentPage.drawText("STRATEGIC ACTION PLAN", {
          x: margin,
          y,
          size: 12,
          font: helveticaBold,
          color: rgb(0.05, 0.35, 0.65)
        });
        y -= 16;
        analysisResult.action_plan.forEach((step, idx) => {
          writeWrapped(`${idx + 1}.  ${step}`, 9.5, helvetica);
          y -= 4;
        });
        y -= 10;
      }

      // Interview Prep
      if (analysisResult.interview_questions?.length) {
        checkPageBreak(40);
        currentPage.drawText("RECOMMENDED INTERVIEW PREPARATION", {
          x: margin,
          y,
          size: 12,
          font: helveticaBold,
          color: rgb(0.05, 0.35, 0.65)
        });
        y -= 16;
        for (const q of analysisResult.interview_questions) {
          writeWrapped(`Q: ${q.question}`, 9.5, helveticaBold, rgb(0.15, 0.15, 0.15));
          writeWrapped(`Context: ${q.context}`, 8.5, helvetica, rgb(0.4, 0.4, 0.4));
          y -= 6;
        }
      }

      drawFooter(currentPage, helvetica, pdfDoc.getPageCount());

      const pdfBytes = await pdfDoc.save();
      const blob = new Blob([pdfBytes], { type: "application/pdf" });
      const filename = `AI_Resume_Review_${finalJobRole.replace(/\s+/g, "_")}.pdf`;
      const url = URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = filename;
      document.body.appendChild(a);
      a.click();
      setTimeout(() => {
        document.body.removeChild(a);
        URL.revokeObjectURL(url);
      }, 2000);
    } catch (err) {
      console.error("PDF generation failed:", err);
      alert("Failed to generate PDF. You can use 'Copy Markdown' instead.");
    }
  };

  const getScoreColor = (score) => {
    if (score >= 80) return "score-green";
    if (score >= 65) return "score-amber";
    return "score-red";
  };

  return (
    <div className="main-wrapper">
      {/* Top Navbar */}
      <header className="navbar" role="banner">
        <div className="nav-container">
          <div className="nav-brand">
            <span className="brand-logo" aria-hidden="true">🎯</span>
            <div>
              <h1 className="brand-title">AI Resume Reviewer</h1>
              <span className="brand-subtitle">Smart Career Advisor & ATS Strategist</span>
            </div>
          </div>
          <div className="nav-actions">
            <button
              className="settings-trigger-btn"
              onClick={() => setShowSettings(true)}
              aria-label="Configure AI settings and Gemini API key"
            >
              <Key size={16} aria-hidden="true" />
              <span>{userApiKey ? "API Key Configured" : "AI Settings"}</span>
            </button>
          </div>
        </div>
      </header>

      {/* Main Workspace */}
      <main className="workspace-container">
        {/* Left Column: Input Panel */}
        <section className="input-column" aria-label="Resume configuration and input">
          <div className="panel-card">
            <div className="panel-header">
              <h2 className="panel-title">
                <Briefcase size={20} className="header-icon" aria-hidden="true" /> Target Role & Context
              </h2>
              <span className="step-badge">Step 1</span>
            </div>

            {/* Role Selector */}
            <div className="form-group">
              <label htmlFor="role-select" className="form-label">Target Job Role</label>
              <select
                id="role-select"
                className="custom-select"
                value={selectedJobRole}
                onChange={(e) => setSelectedJobRole(e.target.value)}
              >
                {JOB_ROLES.map((role) => (
                  <option key={role} value={role}>{role}</option>
                ))}
              </select>
            </div>

            {selectedJobRole === "Custom" && (
              <div className="form-group">
                <label htmlFor="custom-role-input" className="form-label">Enter Custom Role Title</label>
                <input
                  id="custom-role-input"
                  type="text"
                  className="custom-input"
                  placeholder="e.g. Solutions Architect / Staff iOS Engineer"
                  value={customJobRole}
                  onChange={(e) => setCustomJobRole(e.target.value)}
                />
              </div>
            )}

            {/* Advisor Persona Selector */}
            <fieldset className="form-group">
              <legend className="form-label">Choose Advisor Persona</legend>
              <div className="persona-grid" role="radiogroup" aria-label="Advisor Persona">
                {PERSONAS.map((p) => (
                  <button
                    key={p.id}
                    type="button"
                    role="radio"
                    aria-checked={selectedPersona === p.id}
                    className={`persona-card ${selectedPersona === p.id ? "selected" : ""}`}
                    onClick={() => setSelectedPersona(p.id)}
                  >
                    <span className="persona-icon" aria-hidden="true">{p.icon}</span>
                    <span className="persona-title">{p.title}</span>
                  </button>
                ))}
              </div>
              <p className="persona-hint">
                {PERSONAS.find((p) => p.id === selectedPersona)?.tagline}
              </p>
            </fieldset>

            {/* Job Description (Optional) */}
            <div className="form-group">
              <label htmlFor="job-desc-input" className="form-label">
                Target Job Description <span className="label-optional">(Optional, for custom keyword gap matching)</span>
              </label>
              <textarea
                id="job-desc-input"
                className="custom-textarea"
                rows={3}
                placeholder="Paste key requirements or job description from LinkedIn/Indeed..."
                value={jobDescription}
                onChange={(e) => setJobDescription(e.target.value)}
              />
            </div>

            <div className="divider" role="separator" />

            {/* Step 2: Resume Content */}
            <div className="panel-header">
              <h2 className="panel-title">
                <FileText size={20} className="header-icon" aria-hidden="true" /> Resume Input
              </h2>
              <span className="step-badge">Step 2</span>
            </div>

            {/* 1-Click Samples */}
            <div className="sample-bar">
              <span className="sample-label">⚡ 1-Click Samples:</span>
              <button
                type="button"
                className="sample-btn"
                onClick={() => loadSample("software_engineer")}
              >
                Software Engineer
              </button>
              <button
                type="button"
                className="sample-btn"
                onClick={() => loadSample("data_scientist")}
              >
                Data Scientist
              </button>
              <button
                type="button"
                className="sample-btn"
                onClick={() => loadSample("product_manager")}
              >
                Product Manager
              </button>
            </div>

            {/* Mode Tabs */}
            <div className="mode-tabs" role="tablist" aria-label="Resume input format">
              <button
                type="button"
                role="tab"
                id="tab-upload"
                aria-selected={activeTab === "upload"}
                aria-controls="panel-upload"
                className={`tab-btn ${activeTab === "upload" ? "active" : ""}`}
                onClick={() => setActiveTab("upload")}
              >
                <UploadCloud size={16} aria-hidden="true" /> Upload Resume (PDF, DOCX, TXT)
              </button>
              <button
                type="button"
                role="tab"
                id="tab-paste"
                aria-selected={activeTab === "paste"}
                aria-controls="panel-paste"
                className={`tab-btn ${activeTab === "paste" ? "active" : ""}`}
                onClick={() => setActiveTab("paste")}
              >
                <FileText size={16} aria-hidden="true" /> Paste Text
              </button>
            </div>

            {activeTab === "upload" ? (
              <div
                id="panel-upload"
                role="tabpanel"
                aria-labelledby="tab-upload"
                className="upload-dropzone"
              >
                <label htmlFor="file-input" className="dropzone-label">
                  <UploadCloud size={36} className="dropzone-icon" aria-hidden="true" />
                  <span className="dropzone-main-text">
                    {resumeFile ? `Selected: ${resumeFile.name}` : "Click or drag & drop your resume"}
                  </span>
                  <span className="dropzone-sub-text">
                    Supports PDF, DOCX, and TXT files (up to 5 MB)
                  </span>
                  <input
                    id="file-input"
                    type="file"
                    accept=".pdf,.docx,.doc,.txt"
                    onChange={handleFileChange}
                    className="hidden-file-input"
                  />
                </label>
                {resumeFile && (
                  <div className="file-preview-strip">
                    <span>📄 {resumeFile.name} ({(resumeFile.size / 1024).toFixed(1)} KB)</span>
                    <button
                      type="button"
                      className="remove-file-btn"
                      onClick={() => setResumeFile(null)}
                      aria-label="Remove uploaded resume"
                    >
                      <X size={14} aria-hidden="true" /> Remove
                    </button>
                  </div>
                )}
              </div>
            ) : (
              <div
                id="panel-paste"
                role="tabpanel"
                aria-labelledby="tab-paste"
                className="paste-container"
              >
                <textarea
                  id="paste-textarea-field"
                  className="paste-box"
                  rows={9}
                  aria-label="Paste resume content"
                  placeholder="Paste your full resume text here (experience, education, projects)..."
                  value={pastedText}
                  onChange={(e) => setPastedText(e.target.value)}
                />
                <div className="word-count-bar">
                  <span>{pastedText.trim() ? `${pastedText.trim().split(/\s+/).length} words` : "0 words"}</span>
                </div>
              </div>
            )}

            {errorMessage && (
              <div className="error-alert" role="alert">
                <AlertTriangle size={16} aria-hidden="true" />
                <span>{errorMessage}</span>
              </div>
            )}

            {/* Action Button */}
            <button
              type="button"
              className="submit-analyze-btn"
              onClick={runAnalysis}
              disabled={isAnalyzing || !hasInput}
              aria-busy={isAnalyzing}
            >
              {isAnalyzing ? (
                <>
                  <RefreshCw size={18} className="spin" aria-hidden="true" />
                  <span>Analyzing Resume with AI...</span>
                </>
              ) : (
                <>
                  <Sparkles size={18} aria-hidden="true" />
                  <span>Analyze Resume with {selectedPersona}</span>
                </>
              )}
            </button>
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
              {/* Hero Score Card */}
              <div className="report-card hero-score-card">
                <div className="score-summary-grid">
                  <div className="primary-score-box">
                    <div className={`score-circle ${getScoreColor(analysisResult.overall_score)}`}>
                      <span className="score-number">{analysisResult.overall_score}</span>
                      <span className="score-total">/100</span>
                    </div>
                    <div className="score-label-group">
                      <h3 className="score-title">Overall ATS Fit Score</h3>
                      <div className="meta-badges">
                        <span className="meta-badge engine-badge">
                          🧠 {analysisResult.engine || "Intelligent ATS Engine"}
                        </span>
                        <span className="meta-badge seniority-badge">
                          <UserCheck size={12} aria-hidden="true" /> {analysisResult.seniority_level || "Mid-Level"}
                        </span>
                        <span className="meta-badge prob-badge">
                          <Percent size={12} aria-hidden="true" /> Pass: {analysisResult.ats_pass_probability || "Moderate"}
                        </span>
                      </div>
                    </div>
                  </div>

                  <div className="category-scores-list">
                    {analysisResult.category_scores && (
                      <>
                        <div className="cat-item">
                          <div className="cat-header">
                            <span>Role Relevance & Keywords</span>
                            <span>{analysisResult.category_scores.role_relevance}%</span>
                          </div>
                          <div className="progress-track" role="progressbar" aria-valuenow={analysisResult.category_scores.role_relevance} aria-valuemin="0" aria-valuemax="100">
                            <div
                              className="progress-fill"
                              style={{ width: `${analysisResult.category_scores.role_relevance}%` }}
                            />
                          </div>
                        </div>

                        <div className="cat-item">
                          <div className="cat-header">
                            <span>Impact & Metrics (XYZ Formula)</span>
                            <span>{analysisResult.category_scores.impact_quantification}%</span>
                          </div>
                          <div className="progress-track" role="progressbar" aria-valuenow={analysisResult.category_scores.impact_quantification} aria-valuemin="0" aria-valuemax="100">
                            <div
                              className="progress-fill"
                              style={{ width: `${analysisResult.category_scores.impact_quantification}%` }}
                            />
                          </div>
                        </div>

                        <div className="cat-item">
                          <div className="cat-header">
                            <span>ATS Readability & Sections</span>
                            <span>{analysisResult.category_scores.ats_readability}%</span>
                          </div>
                          <div className="progress-track" role="progressbar" aria-valuenow={analysisResult.category_scores.ats_readability} aria-valuemin="0" aria-valuemax="100">
                            <div
                              className="progress-fill"
                              style={{ width: `${analysisResult.category_scores.ats_readability}%` }}
                            />
                          </div>
                        </div>

                        <div className="cat-item">
                          <div className="cat-header">
                            <span>Skills & Competencies Match</span>
                            <span>{analysisResult.category_scores.skills_alignment}%</span>
                          </div>
                          <div className="progress-track" role="progressbar" aria-valuenow={analysisResult.category_scores.skills_alignment} aria-valuemin="0" aria-valuemax="100">
                            <div
                              className="progress-fill"
                              style={{ width: `${analysisResult.category_scores.skills_alignment}%` }}
                            />
                          </div>
                        </div>
                      </>
                    )}
                  </div>
                </div>

                <div className="report-actions-bar">
                  <button type="button" className="action-btn-pdf" onClick={downloadReportPdf}>
                    <Download size={16} aria-hidden="true" /> Download Multi-Page PDF Report
                  </button>
                  <button type="button" className="action-btn-copy" onClick={copyToClipboard}>
                    {copied ? <Check size={16} aria-hidden="true" /> : <Copy size={16} aria-hidden="true" />}
                    {copied ? "Copied!" : "Copy Markdown"}
                  </button>
                </div>
              </div>

              {/* Executive Assessment */}
              <div className="report-card">
                <h3 className="section-title">
                  <Target size={18} className="section-icon" aria-hidden="true" /> Executive Assessment
                </h3>
                <p className="summary-text">{analysisResult.summary}</p>
              </div>

              {/* Strengths & Weaknesses */}
              <div className="dual-grid">
                <div className="report-card strengths-card">
                  <h3 className="section-title text-green">
                    <CheckCircle2 size={18} className="section-icon" aria-hidden="true" /> Key Strengths
                  </h3>
                  <ul className="bullet-list">
                    {analysisResult.strengths?.map((s, idx) => (
                      <li key={idx} className="strength-item">
                        <Check size={14} className="bullet-check" aria-hidden="true" />
                        <span>{s}</span>
                      </li>
                    ))}
                  </ul>
                </div>

                <div className="report-card weaknesses-card">
                  <h3 className="section-title text-amber">
                    <AlertTriangle size={18} className="section-icon" aria-hidden="true" /> Critical Improvement Areas
                  </h3>
                  <div className="weakness-list">
                    {analysisResult.weaknesses?.map((w, idx) => (
                      <div key={idx} className="weakness-item">
                        <div className="weakness-header">
                          <span className={`severity-tag sev-${w.severity}`}>
                            {w.severity.toUpperCase()}
                          </span>
                          <span className="weakness-title">{w.issue}</span>
                        </div>
                        <p className="weakness-desc">{w.description}</p>
                      </div>
                    ))}
                  </div>
                </div>
              </div>

              {/* Keyword Gap Analysis */}
              {(analysisResult.matched_keywords?.length > 0 || analysisResult.missing_keywords?.length > 0) && (
                <div className="report-card">
                  <h3 className="section-title">
                    <Award size={18} className="section-icon" aria-hidden="true" /> Keyword Gap Analysis
                  </h3>
                  <div className="keywords-wrapper">
                    {analysisResult.matched_keywords?.length > 0 && (
                      <div className="keyword-group">
                        <span className="group-heading text-green">✓ Matched in Resume:</span>
                        <div className="tag-cloud">
                          {analysisResult.matched_keywords.map((kw, i) => (
                            <span key={i} className="tag tag-matched">{kw}</span>
                          ))}
                        </div>
                      </div>
                    )}
                    {analysisResult.missing_keywords?.length > 0 && (
                      <div className="keyword-group">
                        <span className="group-heading text-red">+ Recommended to Add:</span>
                        <div className="tag-cloud">
                          {analysisResult.missing_keywords.map((kw, i) => (
                            <span key={i} className="tag tag-missing">{kw}</span>
                          ))}
                        </div>
                      </div>
                    )}
                  </div>
                </div>
              )}

              {/* Google XYZ Formula Bullet Rewrites */}
              {analysisResult.bullet_improvements?.length > 0 && (
                <div className="report-card">
                  <h3 className="section-title">
                    <Sparkles size={18} className="section-icon" aria-hidden="true" /> Actionable Bullet Rewrites (Google XYZ Formula)
                  </h3>
                  <div className="rewrite-list">
                    {analysisResult.bullet_improvements.map((b, idx) => (
                      <div key={idx} className="rewrite-card">
                        <div className="rewrite-row before-row">
                          <span className="rewrite-tag tag-before">BEFORE</span>
                          <span className="rewrite-text">{b.original}</span>
                        </div>
                        <div className="rewrite-row after-row">
                          <span className="rewrite-tag tag-after">OPTIMIZED</span>
                          <span className="rewrite-text bold">{b.improved}</span>
                        </div>
                        <div className="rewrite-why">
                          <strong>Why this converts:</strong> {b.reason}
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* Strategic Action Plan */}
              {analysisResult.action_plan?.length > 0 && (
                <div className="report-card">
                  <h3 className="section-title">
                    <BookOpen size={18} className="section-icon" aria-hidden="true" /> Strategic Action Plan
                  </h3>
                  <div className="action-steps">
                    {analysisResult.action_plan.map((step, idx) => (
                      <div key={idx} className="step-card">
                        <span className="step-number" aria-hidden="true">{idx + 1}</span>
                        <span className="step-content">{step}</span>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* Targeted Interview Questions */}
              {analysisResult.interview_questions?.length > 0 && (
                <div className="report-card">
                  <h3 className="section-title">
                    <HelpCircle size={18} className="section-icon" aria-hidden="true" /> Targeted Interview Questions
                  </h3>
                  <div className="interview-list">
                    {analysisResult.interview_questions.map((q, idx) => (
                      <div key={idx} className="interview-card">
                        <p className="question-text">
                          <strong>Q{idx + 1}:</strong> {q.question}
                        </p>
                        <p className="question-context">
                          <em>Why interviewers ask this:</em> {q.context}
                        </p>
                      </div>
                    ))}
                  </div>
                </div>
              )}
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

      {/* Settings Modal */}
      {showSettings && (
        <div
          className="modal-overlay"
          onClick={() => setShowSettings(false)}
          role="dialog"
          aria-modal="true"
          aria-labelledby="modal-settings-title"
        >
          <div className="modal-card" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <h3 id="modal-settings-title" className="modal-title">⚙️ AI Platform & Engine Settings</h3>
              <button
                type="button"
                className="modal-close-btn"
                onClick={() => setShowSettings(false)}
                aria-label="Close settings modal"
              >
                <X size={18} aria-hidden="true" />
              </button>
            </div>
            <div className="modal-body">
              <p className="modal-desc">
                By default, this application utilizes its high-precision <strong>Built-in ATS & NLP Intelligence Engine</strong>, which executes completely offline with zero latency and high consistency.
              </p>
              <div className="form-group">
                <label htmlFor="api-key-input" className="form-label">
                  Google Gemini API Key <span className="label-optional">(Optional)</span>
                </label>
                <input
                  type="password"
                  className="custom-input"
                  placeholder="AIzaSy..."
                  defaultValue={userApiKey}
                  id="api-key-input"
                  autoComplete="off"
                />
                <span className="input-hint">
                  Saved only in your browser session for direct API calls.
                </span>
              </div>
            </div>
            <div className="modal-footer">
              <button
                type="button"
                className="modal-cancel-btn"
                onClick={() => setShowSettings(false)}
              >
                Cancel
              </button>
              <button
                type="button"
                className="modal-save-btn"
                onClick={() => {
                  const val = document.getElementById("api-key-input")?.value || "";
                  handleSaveApiKey(val);
                }}
              >
                Save Preferences
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
