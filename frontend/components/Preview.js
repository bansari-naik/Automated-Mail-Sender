export default function Preview({ stats, subject, body, file, onSend, sending, error }) {
  if (stats.valid.length === 0) return null;
  return (
    <section className="section">
      <div className="label">Ready to send</div>
      <div className="preview">
        <div className="preview-meta">
          <span>
            <b>{stats.valid.length}</b> recipients
          </span>
          <span>
            <b>1</b> resume
          </span>
          <span>
            <b>1</b> email template
          </span>
        </div>
        <div className="label">To</div>
        <div style={{ margin: "6px 0 12px" }}>{stats.valid[0]}</div>
        <div className="label">Subject</div>
        <div style={{ margin: "6px 0 12px" }}>{subject || "—"}</div>
        <hr />
        <div className="preview-body">{body}</div>
        <hr />
        <div className="label">Attachment</div>
        <div style={{ marginTop: 6 }}>{file ? `✓ ${file.name}` : "No resume attached"}</div>
      </div>
      <button className="btn-send" onClick={onSend} disabled={sending}>
        {sending ? "Sending…" : "Send All"}
      </button>
      {error && <div className="error" style={{ textAlign: "center" }}>{error}</div>}
    </section>
  );
}
