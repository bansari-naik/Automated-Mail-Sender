"""Mail Hunt backend — tiny FastAPI app. No database."""
import json
import os

from dotenv import load_dotenv
from fastapi import FastAPI, File, Form, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, RedirectResponse

import auth
import email_sender
import gmail

load_dotenv()
load_dotenv(os.path.join(os.path.dirname(__file__), ".env"))

FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:3000")

app = FastAPI(title="Mail Hunt")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[FRONTEND_URL, "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def root():
    return {"ok": True, "app": "Mail Hunt", "auth_configured": auth.configured()}


@app.get("/auth/google")
def auth_google():
    """Return the Google OAuth URL. Frontend redirects the user there."""
    if not auth.configured():
        return JSONResponse(
            {"error": "Google OAuth is not configured. See README for setup."},
            status_code=500,
        )
    return {"auth_url": auth.get_auth_url()}


@app.get("/auth/google/callback")
def auth_callback(code: str = "", error: str = ""):
    if error:
        return RedirectResponse(f"{FRONTEND_URL}?gmail=error")
    if not code:
        return RedirectResponse(f"{FRONTEND_URL}?gmail=error")
    try:
        flow = auth.build_flow()
        flow.fetch_token(code=code)
        auth.save_credentials(flow.credentials)
        return RedirectResponse(f"{FRONTEND_URL}?gmail=connected")
    except Exception:
        return RedirectResponse(f"{FRONTEND_URL}?gmail=error")


@app.get("/auth/status")
def auth_status():
    creds = auth.load_credentials()
    if not creds:
        return {"connected": False, "email": None}
    return {"connected": True, "email": gmail.get_profile_email()}


@app.post("/auth/logout")
def logout():
    auth.clear_credentials()
    return {"connected": False}


@app.post("/send")
async def send(
    recipients: str = Form("[]"),
    subject: str = Form(""),
    body: str = Form(""),
    resume: UploadFile | None = File(None),
):
    """Send one individual email per recipient with the resume attached."""
    try:
        emails = json.loads(recipients or "[]")
    except json.JSONDecodeError:
        return JSONResponse({"error": "Invalid recipients list."}, status_code=400)

    # Deduplicate + drop blanks (frontend already does this; re-check here).
    seen, clean = set(), []
    for e in emails:
        e = str(e).strip().lower()
        if e and e not in seen:
            seen.add(e)
            clean.append(e)

    if not clean:
        return JSONResponse({"error": "Paste at least one recruiter email."}, status_code=400)
    if not subject.strip() or not body.strip():
        return JSONResponse({"error": "Subject and email body are required."}, status_code=400)
    if auth.load_credentials() is None:
        return JSONResponse({"error": "Connect your Gmail account before sending."}, status_code=401)

    resume_bytes, resume_filename = None, None
    if resume is not None and resume.filename:
        if not resume.filename.lower().endswith(".pdf"):
            return JSONResponse({"error": "Resume must be a PDF file."}, status_code=400)
        resume_bytes = await resume.read()
        if len(resume_bytes) > 10 * 1024 * 1024:
            return JSONResponse({"error": "Resume must be under 10 MB."}, status_code=400)
        resume_filename = resume.filename
    if resume_bytes is None:
        return JSONResponse({"error": "Please upload your resume."}, status_code=400)

    # Resume lives only in memory for this request, then is discarded.
    results = email_sender.send_all(clean, subject, body, resume_bytes, resume_filename)
    sent = sum(1 for r in results if r["ok"])
    failed = [r for r in results if not r["ok"]]
    return {"sent": sent, "failed_count": len(failed), "results": results}
