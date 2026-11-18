import React, { useRef } from "react";
import { X } from "lucide-react";

export function SettingsModal({ show, onClose, currentKey, onSaveKey }) {
  const inputRef = useRef(null);

  if (!show) return null;

  return (
    <div
      className="modal-overlay"
      onClick={onClose}
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
            onClick={onClose}
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
              ref={inputRef}
              type="password"
              className="custom-input"
              placeholder="AIzaSy..."
              defaultValue={currentKey}
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
            onClick={onClose}
          >
            Cancel
          </button>
          <button
            type="button"
            className="modal-save-btn"
            onClick={() => {
              const val = inputRef.current ? inputRef.current.value : "";
              onSaveKey(val);
            }}
          >
            Save Preferences
          </button>
        </div>
      </div>
    </div>
  );
}

export default React.memo(SettingsModal);
