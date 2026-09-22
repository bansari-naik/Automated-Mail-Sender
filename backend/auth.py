"""Google OAuth helpers — per-user credentials. No global token.json."""
import json
import os
import urllib.request
from datetime import datetime, timezone

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import Flow

SCOPES = ["https://www.googleapis.com/auth/gmail.send"]


class NeedsReauth(Exception):
    """Refresh token missing/expired — user must connect Gmail again."""


def _env(name, default=""):
    return os.getenv(name, default)


def client_config():
    return {
        "web": {
            "client_id": _env("GOOGLE_CLIENT_ID"),
            "client_secret": _env("GOOGLE_CLIENT_SECRET"),
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token",
            "redirect_uris": [_env("GOOGLE_REDIRECT_URI", "http://localhost:8000/auth/google/callback")],
        }
    }


def configured():
    return bool(_env("GOOGLE_CLIENT_ID") and _env("GOOGLE_CLIENT_SECRET"))


def redirect_uri():
    return _env("GOOGLE_REDIRECT_URI", "http://localhost:8000/auth/google/callback")


def build_flow(state=None):
    flow = Flow.from_client_config(
        client_config(),
        scopes=SCOPES,
        redirect_uri=redirect_uri(),
    )
    return flow


def get_auth_url(state=None):
    flow = build_flow()
    auth_url, _ = flow.authorization_url(
        access_type="offline",
        include_granted_scopes="true",
        prompt="consent",
        state=state,
    )
    return auth_url


def exchange_code(code: str, state: str | None = None) -> Credentials:
    flow = build_flow()
    # google-auth-oauthlib validates `state` only if the same flow created the
    # URL; we validate state ourselves in DB, so just exchange the code.
    flow.fetch_token(code=code)
    return flow.credentials


def get_userinfo(creds: Credentials):
    """Return (google_sub, email). Uses userinfo endpoint; falls back to Gmail profile."""
    try:
        req = urllib.request.Request(
            "https://www.googleapis.com/oauth2/v3/userinfo",
            headers={"Authorization": f"Bearer {creds.token}"},
        )
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = json.loads(resp.read().decode())
        sub = data.get("sub")
        email = data.get("email")
        if sub and email:
            return sub, email
    except Exception:
        pass
    # Fallback: Gmail profile gives email but no stable sub.
    try:
        import gmail as gmail_mod

        email = gmail_mod.get_profile_email(creds)
        if email:
            return email, email
    except Exception:
        pass
    raise NeedsReauth("Could not identify Google account.")


def creds_to_db_dict(creds: Credentials):
    expiry = creds.expiry
    if expiry is not None and expiry.tzinfo is None:
        expiry = expiry.replace(tzinfo=timezone.utc)
    return {
        "access_token": creds.token,
        "refresh_token": creds.refresh_token,  # may be None on re-consent
        "expiry": expiry,
        "scopes": " ".join(creds.scopes or SCOPES),
    }


def db_dict_to_creds(data) -> Credentials:
    """Rebuild Credentials from DB row dict. Refreshes if expired.

    Raises NeedsReauth if refresh is impossible.
    Returns (creds, updated_dict_or_None) — updated dict must be persisted
    when the access token was refreshed.
    """
    expiry = data.get("expiry")
    if expiry is not None and isinstance(expiry, str):
        try:
            expiry = datetime.fromisoformat(expiry)
        except ValueError:
            expiry = None
    creds = Credentials(
        token=data.get("access_token"),
        refresh_token=data.get("refresh_token"),
        token_uri="https://oauth2.googleapis.com/token",
        client_id=_env("GOOGLE_CLIENT_ID"),
        client_secret=_env("GOOGLE_CLIENT_SECRET"),
        scopes=(data.get("scopes") or " ".join(SCOPES)).split(),
        expiry=expiry,
    )
    if creds.valid:
        return creds, None
    if creds.expired and creds.refresh_token:
        try:
            creds.refresh(Request())
        except Exception as e:
            raise NeedsReauth("Gmail session expired. Please reconnect.") from e
        return creds, creds_to_db_dict(creds)
    raise NeedsReauth("Gmail not connected. Please reconnect.")
