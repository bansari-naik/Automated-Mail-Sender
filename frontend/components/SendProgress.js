export default function SendProgress({ total, results }) {
  const done = results.length;
  const pct = total ? Math.round((done / total) * 100) : 0;
  return (
    <section className="section">
      <div className="label">Sending applications…</div>
      <div className="progress-track">
        <div className="progress-fill" style={{ width: `${pct}%` }} />
      </div>
      <div className="count">
        {done} / {total}
      </div>
      <ul className="result-list">
        {results.map((r) => (
          <li key={r.email} className={r.ok ? "ok" : "fail"}>
            {r.ok ? "✓" : "×"} {r.email}
          </li>
        ))}
      </ul>
    </section>
  );
}
