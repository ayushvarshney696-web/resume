import React from "react";
import { FileText, UploadCloud, X, RefreshCw, Sparkles, AlertTriangle } from "lucide-react";

export function ResumeInputSection({
  onLoadSample,
  activeTab,
  setActiveTab,
  resumeFile,
  setResumeFile,
  onFileChange,
  pastedText,
  setPastedText,
  isAnalyzing,
  onRunAnalysis,
  hasInput,
  errorMessage,
  selectedPersona
}) {
  return (
    <div className="panel-card-section">
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
          onClick={() => onLoadSample("software_engineer")}
        >
          Software Engineer
        </button>
        <button
          type="button"
          className="sample-btn"
          onClick={() => onLoadSample("data_scientist")}
        >
          Data Scientist
        </button>
        <button
          type="button"
          className="sample-btn"
          onClick={() => onLoadSample("product_manager")}
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
              onChange={onFileChange}
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
        onClick={onRunAnalysis}
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
  );
}

export default React.memo(ResumeInputSection);
