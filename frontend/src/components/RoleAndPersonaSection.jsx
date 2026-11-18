import React from "react";
import { Briefcase } from "lucide-react";

export function RoleAndPersonaSection({
  jobRoles,
  selectedJobRole,
  setSelectedJobRole,
  customJobRole,
  setCustomJobRole,
  personas,
  selectedPersona,
  setSelectedPersona,
  jobDescription,
  setJobDescription
}) {
  return (
    <div className="panel-card-section">
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
          {jobRoles.map((role) => (
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
          {personas.map((p) => (
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
          {personas.find((p) => p.id === selectedPersona)?.tagline}
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
    </div>
  );
}

export default React.memo(RoleAndPersonaSection);
