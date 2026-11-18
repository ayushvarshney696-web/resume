import React from "react";
import { Award } from "lucide-react";

export function KeywordGapSection({ matchedKeywords, missingKeywords }) {
  if (!matchedKeywords?.length && !missingKeywords?.length) return null;

  return (
    <div className="report-card">
      <h3 className="section-title">
        <Award size={18} className="section-icon" aria-hidden="true" /> Keyword Gap Analysis
      </h3>
      <div className="keywords-wrapper">
        {matchedKeywords?.length > 0 && (
          <div className="keyword-group">
            <span className="group-heading text-green">✓ Matched in Resume:</span>
            <div className="tag-cloud">
              {matchedKeywords.map((kw, i) => (
                <span key={i} className="tag tag-matched">{kw}</span>
              ))}
            </div>
          </div>
        )}
        {missingKeywords?.length > 0 && (
          <div className="keyword-group">
            <span className="group-heading text-red">+ Recommended to Add:</span>
            <div className="tag-cloud">
              {missingKeywords.map((kw, i) => (
                <span key={i} className="tag tag-missing">{kw}</span>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

export default React.memo(KeywordGapSection);
