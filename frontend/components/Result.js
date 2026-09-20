"use client";
import { useState } from "react";

export default function Result({ report, onRetry, onReset }) {
  const [showFailed, setShowFailed] = useState(false);
  const failed = report.results.filter((r) => !r.ok);
  return (
    <section className="section" style={{ textAlign: "center" }}>
      <div className="label">All done</div>
      <h2 className="serif" style={{ fontWeight: 400, fontSize: 36 }}>
        {report.sent} emails sent
        <br />
        {failed.length} emails failed
      </h2>
      <div className="stats" style={{ justifyContent: "center" }}>
        <span className="ok">✓ {report.sent} Sent</span>
        <span className="fail">× {failed.length} Failed</span>
      </div>
      {failed.length > 0 && (
        <>
          <button className="btn-ghost" onClick={() => setShowFailed((s) => !s)}>
            {showFailed ? "Hide failed" : "View Failed"}
          </button>
          {showFailed && (
            <ul className="result-list" style={{ textAlign: "left" }}>
              {failed.map((r) => (
                <li key={r.email} className="fail">
                  × {r.email}
                  <br />
                  <span className="wait">{r.error}</span>
                </li>
              ))}
            </ul>
          )}
          <button className="btn-send" onClick={() => onRetry(failed.map((r) => r.email))}>
            Send Again
          </button>
        </>
      )}
      <button className="btn-ghost" onClick={onReset}>
        Start over
      </button>
    </section>
  );
}
