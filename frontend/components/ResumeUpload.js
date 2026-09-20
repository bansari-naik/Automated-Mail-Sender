"use client";
import { useRef, useState } from "react";

export default function ResumeUpload({ file, setFile, error }) {
  const inputRef = useRef(null);
  const [over, setOver] = useState(false);

  function pick(f) {
    if (!f) return;
    if (!f.name.toLowerCase().endsWith(".pdf")) {
      setFile(null, "Resume must be a PDF file.");
      return;
    }
    setFile(f, null);
  }

  return (
    <section className="section">
      <div className="section-head">
        <span className="label">Resume</span>
      </div>
      <div
        className={`drop${over ? " over" : ""}`}
        onClick={() => inputRef.current?.click()}
        onDragOver={(e) => {
          e.preventDefault();
          setOver(true);
        }}
        onDragLeave={() => setOver(false)}
        onDrop={(e) => {
          e.preventDefault();
          setOver(false);
          pick(e.dataTransfer.files?.[0]);
        }}
      >
        {file ? (
          <span className="file-ok">✓ {file.name}</span>
        ) : (
          <>
            Drop your resume here
            <br />
            or choose a PDF
          </>
        )}
      </div>
      <input
        ref={inputRef}
        type="file"
        accept=".pdf,application/pdf"
        hidden
        onChange={(e) => pick(e.target.files?.[0])}
      />
      {error && <div className="error">{error}</div>}
    </section>
  );
}
