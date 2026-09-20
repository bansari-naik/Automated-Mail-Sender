export default function EmailInput({ raw, setRaw, stats }) {
  return (
    <section className="section">
      <div className="section-head">
        <span className="label">Recruiter emails</span>
        <span className="count">
          {stats.valid.length > 0 ? `${stats.valid.length} valid` : ""}
        </span>
      </div>
      <textarea
        value={raw}
        onChange={(e) => setRaw(e.target.value)}
        placeholder={"Paste email addresses — one per line\n\nhr@company.com\nrecruiter@startup.com\ncareers@company.com"}
      />
      {(stats.valid.length > 0 || stats.duplicates > 0 || stats.invalid > 0) && (
        <div className="stats">
          <span>
            <b>{stats.valid.length}</b> valid emails
          </span>
          {stats.duplicates > 0 && (
            <span>
              <b>{stats.duplicates}</b> duplicates removed
            </span>
          )}
          {stats.invalid > 0 && (
            <span>
              <b>{stats.invalid}</b> invalid
            </span>
          )}
        </div>
      )}
    </section>
  );
}
