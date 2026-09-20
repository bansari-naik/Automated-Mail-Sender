# Mail Hunt

A simple personal web app for sending AI internship outreach emails to multiple
recruiters — without composing and sending the same email over and over.

Paste recruiter emails → check the email → upload resume → connect Gmail → Send All.
Each recruiter gets an **individual** email through the Gmail API with your resume attached.

> Keep it simple. Personal productivity tool, not SaaS.
> **No database. One page. One workflow.**

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

---

## Prerequisites

- **Python** 3.10+ (`python --version`)
- **Node.js** 18+ (`node --version`)
- A **Google account**
- A **Google Cloud account** (free — for OAuth credentials)

---

## Google Cloud setup (step by step)

### 1. Create a Google Cloud project

1. Go to [Google Cloud Console](https://console.cloud.google.com/).
2. Click the project dropdown (top left) → **New Project**.
3. Name it e.g. `mail-hunt` → **Create**.

### 2. Enable the Gmail API

1. In the console, go to **APIs & Services → Library**.
2. Search for **Gmail API** → click it → **Enable**.

### 3. Configure the OAuth consent screen

1. Go to **APIs & Services → OAuth consent screen**.
2. User type: **External** → **Create**.
3. Fill in app name (`Mail Hunt`), user support email, developer email.
4. On the **Scopes** step, add:
   - `https://www.googleapis.com/auth/gmail.send`
5. On the **Test users** step, add your own Gmail address (while the app is in
   testing mode, only test users can sign in).
6. Save.

### 4. Create OAuth credentials

1. Go to **APIs & Services → Credentials** → **Create Credentials → OAuth client ID**.
2. Application type: **Web application**.
3. Name it e.g. `mail-hunt-web`.
4. Under **Authorized redirect URIs**, add exactly:

```text
http://localhost:8000/auth/google/callback
```

5. Click **Create**. Copy the **Client ID** and **Client Secret**.

> If you deploy somewhere else later, add that domain's
> `https://<your-domain>/auth/google/callback` URI here too.

### 5. Add environment variables

```bash
cp backend/.env.example backend/.env
```

Edit `backend/.env`:

```env
GOOGLE_CLIENT_ID=your-client-id-here
GOOGLE_CLIENT_SECRET=your-client-secret-here
GOOGLE_REDIRECT_URI=http://localhost:8000/auth/google/callback
FRONTEND_URL=http://localhost:3000
```

Frontend (optional — defaults to `http://localhost:8000`):

```bash
# frontend/.env.local
NEXT_PUBLIC_API_URL=http://localhost:8000
```

> Do **not** put real credentials in the repo. `backend/.env`, `token.json` and
> `credentials.json` are all gitignored.

---

## Running the project

Backend:

```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --reload
```

Frontend:

```bash
cd frontend
npm install
npm run dev
```

Open [http://localhost:3000](http://localhost:3000).

---

## Gmail authorization (user flow)

```text
Open application
        ↓
Click Connect Gmail
        ↓
Google login
        ↓
Grant Gmail send permission
        ↓
Return to Mail Hunt (✓ Gmail Connected)
        ↓
Preview → Send All
```

The app requests only the minimum scope (`gmail.send`), sends each email
individually (no CC), and never asks for or stores your Gmail password.

---

## API (V1 — that's all there is)

| Method | Route                   | What it does                          |
| ------ | ----------------------- | ------------------------------------- |
| GET    | `/auth/google`          | Returns the Google OAuth URL          |
| GET    | `/auth/google/callback` | Handles OAuth callback, saves token   |
| GET    | `/auth/status`          | `{ "connected": true/false, email }`  |
| POST   | `/auth/logout`          | Clears the OAuth token                |
| POST   | `/send`                 | Sends one email per recipient + resume|

`POST /send` takes multipart form data: `recipients` (JSON array), `subject`,
`body`, `resume` (PDF). The resume lives only in memory for the request and is
then discarded.

---

## Security

- Never commit OAuth credentials (`backend/.env`, `credentials.json`).
- Never commit access/refresh tokens (`backend/token.json`).
- Never put the Google client secret in the frontend — it stays in `backend/.env`.
- Use `.env` files; they are covered by `.gitignore`.
- The app uses the least-privilege `gmail.send` scope only.
- No raw Python stack traces are exposed to the UI — errors are friendly strings.

---

## Scope (deliberately small)

No database, no user accounts, no admin dashboard, no CRM, no open tracking, no
analytics, no LinkedIn integration, no scraping, no scheduling, no follow-ups.
Just send the emails.
