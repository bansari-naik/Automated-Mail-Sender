"""Google OAuth helpers. Keeps the Gmail send-only OAuth flow in one place."""
import json
import os

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import Flow

SCOPES = ["https://www.googleapis.com/auth/gmail.send"]
TOKEN_FILE = os.path.join(os.path.dirname(__file__), "token.json")

# In-memory cache so we don't hit disk on every request.
_cached_creds = None


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


def build_flow():
    return Flow.from_client_config(
        client_config(),
        scopes=SCOPES,
        redirect_uri=_env("GOOGLE_REDIRECT_URI", "http://localhost:8000/auth/google/callback"),
    )


def get_auth_url():
    flow = build_flow()
    auth_url, _ = flow.authorization_url(
        access_type="offline",
        include_granted_scopes="true",
        prompt="consent",
    )
    return auth_url


def save_credentials(creds: Credentials):
    global _cached_creds
    _cached_creds = creds
    try:
        with open(TOKEN_FILE, "w") as f:
            f.write(creds.to_json())
    except OSError:
        pass  # memory cache still works for the current session


def load_credentials():
    global _cached_creds
    if _cached_creds and _cached_creds.valid:
        return _cached_creds
    if _cached_creds and _cached_creds.expired and _cached_creds.refresh_token:
        try:
            _cached_creds.refresh(Request())
            save_credentials(_cached_creds)
            return _cached_creds
        except Exception:
            return None
    if not os.path.exists(TOKEN_FILE):
        return None
    try:
        with open(TOKEN_FILE) as f:
            data = json.load(f)
        creds = Credentials.from_authorized_user_info(data, SCOPES)
        if creds and creds.valid:
            _cached_creds = creds
            return creds
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
            save_credentials(creds)
            return creds
    except Exception:
        return None
    return None


def clear_credentials():
    global _cached_creds
    _cached_creds = None
    try:
        if os.path.exists(TOKEN_FILE):
            os.remove(TOKEN_FILE)
    except OSError:
        pass
