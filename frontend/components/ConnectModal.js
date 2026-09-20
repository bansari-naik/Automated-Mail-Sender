"use client";

export default function ConnectModal({ open, onClose, onContinue, loading, error }) {
  if (!open) return null;
  return (
    <div className="modal-bg" onClick={onClose}>
      <div className="modal" onClick={(e) => e.stopPropagation()}>
        <h2>Connect your Gmail</h2>
        <p>
          Mail Hunt needs permission to send emails
          <br />
          from your Gmail account.
        </p>
        <button className="btn-google" onClick={onContinue} disabled={loading}>
          {loading ? "Opening Google…" : "Continue with Google"}
        </button>
        {error && <div className="error">{error}</div>}
        <button className="btn-ghost" onClick={onClose}>
          Cancel
        </button>
      </div>
    </div>
  );
}
