import React from "react";
import { BookOpen } from "lucide-react";

export function ActionPlanSection({ actionPlan }) {
  if (!actionPlan?.length) return null;

  return (
    <div className="report-card">
      <h3 className="section-title">
        <BookOpen size={18} className="section-icon" aria-hidden="true" /> Strategic Action Plan
      </h3>
      <div className="action-steps">
        {actionPlan.map((step, idx) => (
          <div key={idx} className="step-card">
            <span className="step-number" aria-hidden="true">{idx + 1}</span>
            <span className="step-content">{step}</span>
          </div>
        ))}
      </div>
    </div>
  );
}

export default React.memo(ActionPlanSection);
