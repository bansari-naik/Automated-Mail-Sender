"""Mail Hunt backend — stateless multi-user FastAPI app.

No database: each user's Gmail tokens live sealed in their own HttpOnly
cookie. The server stores nothing about who uses the app. User A's login
never touches User B's browser.
"""
import hmac
import json
import logging
import os
import secrets

from dotenv import load_dotenv
from fastapi import FastAPI, File, Form, Request, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, RedirectResponse

import auth
import crypto
import email_sender
import gmail

load_dotenv()
load_dotenv(os.path.join(os.path.dirname(__file__), ".env"))

FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:3000").rstrip("/")
COOKIE_SECURE = os.getenv("COOKIE_SECURE", "false").lower() in ("1", "true", "yes")
MAX_RECIPIENTS = 100

AUTH_COOKIE = "mailhunt_auth"  # sealed session: tokens + email, 30 days
STATE_COOKIE = "mailhunt_oauth_state"  # one-time CSRF state, 10 min
AUTH_DAYS = 30
STATE_SECONDS = 600

log = logging.getLogger("mailhunt")

app = FastAPI(title="Mail Hunt")

origins = []
for o in (FRONTEND_URL, "http://localhost:3000"):
    if o and o not in origins:
        origins.append(o)

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def _cookie_kwargs(max_age: int):
    return {
        "httponly": True,
        "secure": COOKIE_SECURE,
        "samesite": "lax",
        "max_age": max_age,
        "path": "/",
    }


def _session_to_cookie_data(token_data: dict, email: str, sub: str):
    expiry = token_data.get("expiry")
    return {
        "access_token": token_data.get("access_token"),
        "refresh_token": token_data.get("refresh_token"),  # may be None
        "expiry": expiry.isoformat() if expiry is not None else None,
        "scopes": token_data.get("scopes", ""),
        "email": email,
        "sub": sub,
    }


def _load_session(request: Request):
    """Return (session_dict, email, creds, refreshed_token_data|None).

    creds is None when not connected or re-auth is needed.
    """
    data = crypto.unseal_session(request.cookies.get(AUTH_COOKIE))
    if not data or not data.get("access_token"):
        return None, None, None, None
    try:
        creds, updated = auth.db_dict_to_creds(data)
    except auth.NeedsReauth:
        return data, data.get("email"), None, None
    return data, data.get("email"), creds, updated


def _apply_refresh(data: dict, updated: dict):
    data["access_token"] = updated.get("access_token", data["access_token"])
    if updated.get("refresh_token"):
        data["refresh_token"] = updated["refresh_token"]
    expiry = updated.get("expiry")
    data["expiry"] = expiry.isoformat() if expiry is not None else data.get("expiry")
    if updated.get("scopes"):
        data["scopes"] = updated["scopes"]
    return data


@app.get("/")
def root():
    return {"ok": True, "app": "Mail Hunt", "auth_configured": auth.configured(), "stateless": True}


@app.get("/auth/google")
def auth_google():
    """Return the Google OAuth URL and set a one-time CSRF state cookie."""
    if not auth.configured():
        return JSONResponse(
            {"error": "Google OAuth is not configured. See README for setup."},
            status_code=500,
        )
    state = secrets.token_urlsafe(32)
    resp = JSONResponse({"auth_url": auth.get_auth_url(state)})
    resp.set_cookie(STATE_COOKIE, state, **_cookie_kwargs(STATE_SECONDS))
    return resp


@app.get("/auth/google/callback")
def auth_callback(request: Request, code: str = "", state: str = "", error: str = ""):
    expected = request.cookies.get(STATE_COOKIE, "")
    bad_state = (
        not code
        or not state
        or not expected
        or not hmac.compare_digest(state, expected)
    )
    if error or bad_state:
        if error:
            log.warning("OAuth callback error from Google: %s", error)
        else:
            log.warning("OAuth callback with missing/invalid state")
        resp = RedirectResponse(f"{FRONTEND_URL}?gmail=error")
        resp.delete_cookie(STATE_COOKIE, path="/")
        return resp
    try:
        creds = auth.exchange_code(code, state)
        sub, email = auth.get_userinfo(creds)
    except Exception as e:
        log.warning("OAuth exchange/userinfo failed: %s", e)
        resp = RedirectResponse(f"{FRONTEND_URL}?gmail=error")
        resp.delete_cookie(STATE_COOKIE, path="/")
        return resp

    data = _session_to_cookie_data(auth.creds_to_db_dict(creds), email, sub)
    resp = RedirectResponse(f"{FRONTEND_URL}?gmail=connected")
    resp.delete_cookie(STATE_COOKIE, path="/")
    resp.set_cookie(AUTH_COOKIE, crypto.seal_session(data), **_cookie_kwargs(AUTH_DAYS * 86400))
    return resp


@app.get("/auth/status")
def auth_status(request: Request):
    data, email, creds, updated = _load_session(request)
    if not creds:
        return {"connected": False, "email": None}
    if updated:
        data = _apply_refresh(data, updated)
        resp = JSONResponse({"connected": True, "email": gmail.get_profile_email(creds) or email})
        resp.set_cookie(AUTH_COOKIE, crypto.seal_session(data), **_cookie_kwargs(AUTH_DAYS * 86400))
        return resp
    return {"connected": True, "email": gmail.get_profile_email(creds) or email}


@app.post("/auth/logout")
def logout():
    # Only this browser's cookie is cleared — other users are untouched.
    resp = JSONResponse({"connected": False})
    resp.delete_cookie(AUTH_COOKIE, path="/")
    return resp


@app.post("/send")
async def send(
    request: Request,
    recipients: str = Form("[]"),
    subject: str = Form(""),
    body: str = Form(""),
    resume: UploadFile | None = File(None),
):
    """Send one individual email per recipient with the resume attached."""
    resume_file: UploadFile | None = resume
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
    if len(clean) > MAX_RECIPIENTS:
        return JSONResponse(
            {"error": f"Max {MAX_RECIPIENTS} recipients per request. Split into batches."},
            status_code=400,
        )
    if not subject.strip() or not body.strip():
        return JSONResponse({"error": "Subject and email body are required."}, status_code=400)

    data, _, creds, updated = _load_session(request)
    if creds is None:
        return JSONResponse({"error": "Connect your Gmail account before sending."}, status_code=401)

    resume_bytes, resume_filename = None, None
    if resume_file is not None and resume_file.filename:
        if not resume_file.filename.lower().endswith(".pdf"):
            return JSONResponse({"error": "Resume must be a PDF file."}, status_code=400)
        resume_bytes = await resume_file.read()
        if len(resume_bytes) > 10 * 1024 * 1024:
            return JSONResponse({"error": "Resume must be under 10 MB."}, status_code=400)
        resume_filename = resume_file.filename
    if resume_bytes is None:
        return JSONResponse({"error": "Please upload your resume."}, status_code=400)

    # Resume lives only in memory for this request, then is discarded.
    service = gmail.get_service(creds)
    results = email_sender.send_all(service, clean, subject, body, resume_bytes, resume_filename)
    sent = sum(1 for r in results if r["ok"])
    failed = [r for r in results if not r["ok"]]
    resp = JSONResponse({"sent": sent, "failed_count": len(failed), "results": results})
    if updated and data is not None:
        resp.set_cookie(
            AUTH_COOKIE,
            crypto.seal_session(_apply_refresh(data, updated)),
            **_cookie_kwargs(AUTH_DAYS * 86400),
        )
    return resp
