# Mail Hunt

A simple personal web app for sending AI internship outreach emails to multiple
recruiters — without composing and sending the same email over and over.

Paste recruiter emails → check the email → upload resume → connect Gmail → Send All.
Each recruiter gets an **individual** email through the Gmail API with your resume attached.

---

## Project structure

```text
Mail Sender/
├── frontend/          # Next.js single-page UI
│   ├── app/           # layout.js, page.js, globals.css
│   ├── components/    # Header, Hero, EmailInput, EmailContent, ResumeUpload,
│   │                  # Preview, SendProgress, Result, ConnectModal
│   └── lib/           # api.js, emails.js
├── backend/           # FastAPI — OAuth + Gmail sending only
│   ├── main.py        # routes: /auth/*, /send
│   ├── auth.py        # Google OAuth helpers
│   ├── gmail.py       # message creation + Gmail API calls
│   ├── email_sender.py# per-recipient send loop
│   └── requirements.txt
├── README.md
└── .gitignore
```
