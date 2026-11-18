import React from "react";
import { HelpCircle } from "lucide-react";

export function InterviewQuestionsSection({ interviewQuestions }) {
  if (!interviewQuestions?.length) return null;

  return (
    <div className="report-card">
      <h3 className="section-title">
        <HelpCircle size={18} className="section-icon" aria-hidden="true" /> Targeted Interview Questions
      </h3>
      <div className="interview-list">
        {interviewQuestions.map((q, idx) => (
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
  );
}

export default React.memo(InterviewQuestionsSection);
