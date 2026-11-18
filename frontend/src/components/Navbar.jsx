import React from "react";
import { Key } from "lucide-react";

export function Navbar({ onOpenSettings, isApiKeyConfigured }) {
  return (
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
            type="button"
            className="settings-trigger-btn"
            onClick={onOpenSettings}
            aria-label="Configure AI settings and Gemini API key"
          >
            <Key size={16} aria-hidden="true" />
            <span>{isApiKeyConfigured ? "API Key Configured" : "AI Settings"}</span>
          </button>
        </div>
      </div>
    </header>
  );
}

export default React.memo(Navbar);
