export default function EmailContent({ subject, setSubject, body, setBody }) {
  return (
    <section className="section">
      <div className="section-head">
        <span className="label">Email content</span>
      </div>
      <div className="label" style={{ marginBottom: 8 }}>
        Subject
      </div>
      <input
        type="text"
        value={subject}
        onChange={(e) => setSubject(e.target.value)}
        placeholder="AI Internship Application – Your Name"
        style={{ marginBottom: 16 }}
      />
      <div className="label" style={{ marginBottom: 8 }}>
        Body
      </div>
      <textarea
        value={body}
        onChange={(e) => setBody(e.target.value)}
        style={{ minHeight: 280 }}
      />
    </section>
  );
}
