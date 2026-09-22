"""Loop over recipients and send one individual email to each."""
import re

import gmail

EMAIL_RE = re.compile(r"^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$")


def is_valid(email):
    return bool(EMAIL_RE.match(email.strip()))


def send_all(service, recipients, subject, body, resume_bytes=None, resume_filename="resume.pdf"):
    """Send individually. Returns list of {email, ok, error} dicts.

    `service` must be a per-user Gmail API service (see gmail.get_service).
    """
    if service is None:
        return [
            {"email": r, "ok": False, "error": "Gmail not connected."}
            for r in recipients
        ]

    results = []
    for email in recipients:
        email = email.strip()
        if not is_valid(email):
            results.append({"email": email, "ok": False, "error": "Invalid email address."})
            continue
        try:
            gmail.send_to_recipient(service, email, subject, body, resume_bytes, resume_filename)
            results.append({"email": email, "ok": True, "error": None})
        except Exception:
            results.append({
                "email": email,
                "ok": False,
                "error": "We couldn't send this email. Please check your Gmail connection and try again.",
            })
    return results
