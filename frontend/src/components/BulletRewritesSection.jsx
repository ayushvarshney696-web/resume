import React from "react";
import { Sparkles } from "lucide-react";

export function BulletRewritesSection({ bulletImprovements }) {
  if (!bulletImprovements?.length) return null;

  return (
    <div className="report-card">
      <h3 className="section-title">
        <Sparkles size={18} className="section-icon" aria-hidden="true" /> Actionable Bullet Rewrites (Google XYZ Formula)
      </h3>
      <div className="rewrite-list">
        {bulletImprovements.map((b, idx) => (
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
  );
}

export default React.memo(BulletRewritesSection);
