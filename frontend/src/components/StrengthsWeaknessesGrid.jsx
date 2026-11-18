import React from "react";
import { CheckCircle2, AlertTriangle, Check } from "lucide-react";

export function StrengthsWeaknessesGrid({ strengths, weaknesses }) {
  return (
    <div className="dual-grid">
      <div className="report-card strengths-card">
        <h3 className="section-title text-green">
          <CheckCircle2 size={18} className="section-icon" aria-hidden="true" /> Key Strengths
        </h3>
        <ul className="bullet-list">
          {strengths?.map((s, idx) => (
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
          {weaknesses?.map((w, idx) => (
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
  );
}

export default React.memo(StrengthsWeaknessesGrid);
