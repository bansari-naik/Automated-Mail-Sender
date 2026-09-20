export default function Header({ connected, email, onConnect, onLogout }) {
  return (
    <header className="header">
      <div className="brand">Mail Hunt</div>
      {connected ? (
        <button className="connected-pill" onClick={onLogout} title={email || ""}>
          ✓ Gmail Connected
        </button>
      ) : (
        <button className="btn-connect" onClick={onConnect}>
          Connect Gmail
        </button>
      )}
    </header>
  );
}
