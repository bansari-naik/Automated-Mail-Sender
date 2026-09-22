const API = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export async function getAuthUrl() {
  const res = await fetch(`${API}/auth/google`, { credentials: "include" });
  const data = await res.json();
  if (!res.ok) throw new Error(data.error || "Could not start Gmail connection.");
  return data.auth_url;
}

export async function getStatus() {
  try {
    const res = await fetch(`${API}/auth/status`, { credentials: "include" });
    return await res.json();
  } catch {
    return { connected: false, email: null };
  }
}

export async function logout() {
  await fetch(`${API}/auth/logout`, { method: "POST", credentials: "include" });
}

export async function sendAll({ recipients, subject, body, resumeFile, onDone }) {
  const form = new FormData();
  form.append("recipients", JSON.stringify(recipients));
  form.append("subject", subject);
  form.append("body", body);
  form.append("resume", resumeFile);
  const res = await fetch(`${API}/send`, { method: "POST", body: form, credentials: "include" });
  const data = await res.json();
  if (!res.ok) throw new Error(data.error || "Sending failed.");
  return data;
}
