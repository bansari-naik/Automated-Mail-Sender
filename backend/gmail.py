"""Gmail message creation + sending. One recipient per API call."""
import base64
import mimetypes
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from googleapiclient.discovery import build

import auth


def get_service():
    creds = auth.load_credentials()
    if not creds:
        return None
    return build("gmail", "v1", credentials=creds)


def get_profile_email():
    """Return the connected Gmail address (for the header UI)."""
    service = get_service()
    if not service:
        return None
    try:
        profile = service.users().getProfile(userId="me").execute()
        return profile.get("emailAddress")
    except Exception:
        return None


def create_message(to_email, subject, body, resume_bytes=None, resume_filename="resume.pdf"):
    msg = MIMEMultipart()
    msg["To"] = to_email
    msg["Subject"] = subject
    msg.attach(MIMEText(body, "plain", "utf-8"))

    if resume_bytes:
        mime_type, _ = mimetypes.guess_type(resume_filename)
        maintype, subtype = (mime_type or "application/pdf").split("/", 1)
        if maintype == "text":
            part = MIMEText(resume_bytes.decode("utf-8", errors="ignore"), _subtype=subtype)
        else:
            part = MIMEApplication(resume_bytes, _subtype=subtype)
        part.add_header("Content-Disposition", "attachment", filename=resume_filename)
        msg.attach(part)

    raw = base64.urlsafe_b64encode(msg.as_bytes()).decode("utf-8")
    return {"raw": raw}


def send_to_recipient(service, to_email, subject, body, resume_bytes=None, resume_filename="resume.pdf"):
    message = create_message(to_email, subject, body, resume_bytes, resume_filename)
    return service.users().messages().send(userId="me", body=message).execute()
