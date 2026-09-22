"use client";
import { useEffect, useMemo, useState } from "react";
import Header from "../components/Header";
import Hero from "../components/Hero";
import EmailInput from "../components/EmailInput";
import EmailContent from "../components/EmailContent";
import ResumeUpload from "../components/ResumeUpload";
import Preview from "../components/Preview";
import SendProgress from "../components/SendProgress";
import Result from "../components/Result";
import ConnectModal from "../components/ConnectModal";
import { parseEmails } from "../lib/emails";
import { getAuthUrl, getStatus, logout, sendAll } from "../lib/api";

const DEFAULT_SUBJECT = "AI Internship Application – Bansari Naik";
const DEFAULT_BODY = `Dear Hiring Team,

I am Bansari Naik, a final-year B.Tech student specializing in Artificial Intelligence and Data Science at DJSCE, Mumbai.

I am currently looking for an AI internship opportunity where I can work on practical AI systems and contribute to an engineering team.

I have hands-on experience working with agentic AI workflows, RAG-based systems, backend APIs and full-stack applications.

I have attached my resume for your consideration.

GitHub: https://github.com/
LinkedIn: https://linkedin.com/in/

Thank you for your time.

Best regards,
Bansari Naik`;

export default function Page() {
  const [raw, setRaw] = useState("");
  const [subject, setSubject] = useState(DEFAULT_SUBJECT);
  const [body, setBody] = useState(DEFAULT_BODY);
  const [file, setFile] = useState(null);
  const [resumeError, setResumeError] = useState(null);

  const [connected, setConnected] = useState(false);
  const [gmailEmail, setGmailEmail] = useState(null);
  const [modalOpen, setModalOpen] = useState(false);
  const [modalLoading, setModalLoading] = useState(false);
  const [modalError, setModalError] = useState(null);

  const [sending, setSending] = useState(false);
  const [liveResults, setLiveResults] = useState([]); // per-email progress
  const [report, setReport] = useState(null); // final {sent, results}
  const [sendError, setSendError] = useState(null);

  const stats = useMemo(() => parseEmails(raw), [raw]);

  // Restore conveniences from localStorage (subject/body only — not recruiter emails).
  useEffect(() => {
    try {
      const s = localStorage.getItem("mailhunt.subject");
      const b = localStorage.getItem("mailhunt.body");
      if (s) setSubject(s);
      if (b) setBody(b);
    } catch {}
    getStatus().then((s) => {
      setConnected(!!s.connected);
      setGmailEmail(s.email || null);
    });
    const params = new URLSearchParams(window.location.search);
    if (params.get("gmail") === "connected") {
      setConnected(true);
      getStatus().then((s) => {
        setConnected(!!s.connected);
        setGmailEmail(s.email || null);
      });
      window.history.replaceState({}, "", window.location.pathname);
    } else if (params.get("gmail") === "error") {
      setSendError("Google blocked the connection. Check Test users / redirect URI, then try again.");
      window.history.replaceState({}, "", window.location.pathname);
    }
  }, []);

  // Persist conveniences.
  useEffect(() => {
    try {
      localStorage.setItem("mailhunt.subject", subject);
      localStorage.setItem("mailhunt.body", body);
    } catch {}
  }, [subject, body]);

  function handleResume(f, err) {
    setFile(f);
    setResumeError(err);
  }

  async function handleContinueWithGoogle() {
    setModalLoading(true);
    setModalError(null);
    try {
      const url = await getAuthUrl();
      window.location.href = url;
    } catch (e) {
      setModalError(e.message);
      setModalLoading(false);
    }
  }

  async function handleLogout() {
    await logout();
    setConnected(false);
    setGmailEmail(null);
  }

  async function handleSend(recipientList) {
    const list = recipientList || stats.valid;
    setSendError(null);
    if (list.length === 0) {
      setSendError("Paste at least one recruiter email.");
      return;
    }
    if (!subject.trim() || !body.trim()) {
      setSendError("Subject and email body are required.");
      return;
    }
    if (!file) {
      setResumeError("Please upload your resume.");
      setSendError("Please upload your resume.");
      return;
    }
    if (!connected) {
      setModalOpen(true);
      setSendError("Connect your Gmail account before sending.");
      return;
    }
    setSending(true);
    setReport(null);
    setLiveResults([]);
    try {
      // Fake progressive UI: backend sends in one request; we reveal
      // progress optimistically, then reconcile with real results.
      const promise = sendAll({ recipients: list, subject, body, resumeFile: file });
      const tick = setInterval(() => {
        setLiveResults((prev) => {
          if (prev.length >= list.length) {
            clearInterval(tick);
            return prev;
          }
          return [...prev, { email: list[prev.length], ok: true, pending: true }];
        });
      }, 250);
      const data = await promise;
      clearInterval(tick);
      setLiveResults(data.results);
      setReport(data);
    } catch (e) {
      setSendError(e.message);
    } finally {
      setSending(false);
    }
  }

  const showProgress = sending || (liveResults.length > 0 && !report);

  return (
    <>
      <Header
        connected={connected}
        email={gmailEmail}
        onConnect={() => setModalOpen(true)}
        onLogout={handleLogout}
      />
      <main className="wrap">
        <Hero />

        {!report && (
          <>
            <EmailInput raw={raw} setRaw={setRaw} stats={stats} />
            <EmailContent
              subject={subject}
              setSubject={setSubject}
              body={body}
              setBody={setBody}
            />
            <ResumeUpload file={file} setFile={handleResume} error={resumeError} />
          </>
        )}

        {!report && !showProgress && (
          <Preview
            stats={stats}
            subject={subject}
            body={body}
            file={file}
            onSend={() => handleSend()}
            sending={sending}
            error={sendError}
          />
        )}

        {showProgress && <SendProgress total={stats.valid.length} results={liveResults} />}

        {report && !sending && (
          <Result
            report={report}
            onRetry={(failedEmails) => {
              setReport(null);
              handleSend(failedEmails);
            }}
            onReset={() => {
              setReport(null);
              setLiveResults([]);
              setRaw("");
            }}
          />
        )}

        <div className="footer">Mail Hunt — one page, one workflow, no database.</div>
      </main>

      <ConnectModal
        open={modalOpen}
        onClose={() => setModalOpen(false)}
        onContinue={handleContinueWithGoogle}
        loading={modalLoading}
        error={modalError}
      />
    </>
  );
}
