import React from "react";
import { Download, Copy, Check, UserCheck, Percent } from "lucide-react";

export function ScoreHeroCard({ analysisResult, onDownloadPdf, onCopyMarkdown, copied }) {
  const getScoreColor = (score) => {
    if (score >= 80) return "score-green";
    if (score >= 65) return "score-amber";
    return "score-red";
  };

  return (
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
                <div
                  className="progress-track"
                  role="progressbar"
                  aria-valuenow={analysisResult.category_scores.role_relevance}
                  aria-valuemin="0"
                  aria-valuemax="100"
                >
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
                <div
                  className="progress-track"
                  role="progressbar"
                  aria-valuenow={analysisResult.category_scores.impact_quantification}
                  aria-valuemin="0"
                  aria-valuemax="100"
                >
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
                <div
                  className="progress-track"
                  role="progressbar"
                  aria-valuenow={analysisResult.category_scores.ats_readability}
                  aria-valuemin="0"
                  aria-valuemax="100"
                >
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
                <div
                  className="progress-track"
                  role="progressbar"
                  aria-valuenow={analysisResult.category_scores.skills_alignment}
                  aria-valuemin="0"
                  aria-valuemax="100"
                >
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
        <button type="button" className="action-btn-pdf" onClick={onDownloadPdf}>
          <Download size={16} aria-hidden="true" /> Download Multi-Page PDF Report
        </button>
        <button type="button" className="action-btn-copy" onClick={onCopyMarkdown}>
          {copied ? <Check size={16} aria-hidden="true" /> : <Copy size={16} aria-hidden="true" />}
          {copied ? "Copied!" : "Copy Markdown"}
        </button>
      </div>
    </div>
  );
}

export default React.memo(ScoreHeroCard);
