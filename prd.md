# PRD — Mail Hunt

## 1. Product Overview

**Mail Hunt** is a simple personal web app for sending AI internship outreach emails to multiple recruiters without manually composing and sending the same email repeatedly.

The user will:

1. Paste multiple recruiter email addresses.
2. Enter/keep their internship email content.
3. Upload their resume.
4. Connect their Gmail account using Google OAuth.
5. Preview the emails.
6. Click **Send All**.
7. The app sends the email individually to each recruiter through the Gmail API.

### Core principle

> **Keep it simple. This is a personal productivity tool, not a SaaS product.**

No database, no user accounts, no admin dashboard, no complex analytics.

---

# 2. Goals

### Primary goal

Reduce the repetitive work involved in sending the same AI internship application email to many recruiters.

### The user should only need to:

```text
Paste emails
      ↓
Check email
      ↓
Upload resume
      ↓
Connect Gmail
      ↓
Send
```

### Not a goal

The application is **not** intended to:

* scrape recruiter emails
* scrape LinkedIn
* find recruiters automatically
* maintain a CRM
* manage multiple users
* track email opens
* provide complex analytics
* automatically generate fake personalization
* store recruiter data permanently

---

# 3. Tech Stack

## Frontend

**Next.js**

* Simple React-based UI
* Responsive
* No database
* No authentication system of its own
* Client-side state where possible

## Backend

**Python + FastAPI**

Responsible for:

* receiving email addresses
* handling Gmail OAuth flow
* communicating with Gmail API
* creating emails
* attaching resume
* sending emails
* returning send status

## Email

**Gmail API**

Use Google's OAuth 2.0 flow.

The application should request the minimum required Gmail permission, ideally:

```text
https://www.googleapis.com/auth/gmail.send
```

The app should **never ask for or store the user's Gmail password**.

## Storage

**No database.**

No PostgreSQL, MongoDB, Supabase, Firebase, etc.

Temporary information can exist only during the current session/request.

User's basic profile information can optionally be stored in **browser localStorage** for convenience.

---

# 4. UI / Design Direction

The attached reference should be used as the **design inspiration**.

![Image](https://images.openai.com/static-rsc-4/6lcj0KQ3OIRLlkrr5_oh_Ek0EY0KER0b5bXXftrBqn4AhrCKrKeZEGmJmoZaQo4qISq4XiQxBwdX8meAb-jEmYcnfz3GFTQTfcOzpqfB9BuWVtYhBUrnAceqpFE1-_9r_OLyHTKsnvTRfjJGBeWgsJt5NzA6G7lBz-vO4jGn32EL0k9RxlCMLUi86hgLVCan?purpose=fullsize)

![Image](https://images.openai.com/static-rsc-4/ZHlB9LVuXXlZY4b7cCFMW0RBE33Yx4w4jY35_XKWlSHNgwNAXlgdbECCPfqRO9BZGkt8lU9WXpsq0ypj3AnCOQsfrdNGPK0CZg6IBEg94Wpf3bixqbrBswlhwPTTm9E5ORnHunvpbWAEeGittMqXtj_rVaXAiD_58X6oXYyBzlsFdSx9SY4vcJg81G1uNkP5?purpose=fullsize)

![Image](https://images.openai.com/static-rsc-4/nVFbVYXEL1AFqNxvezc5Oq0sI_PbsLmEMMvxyGHBIlYA84N3W_gf7Efstv6F4f6ZNGMcExQz9acQZL2Pl0kemafeYiylExpYXxnL6oZPs_5rAlwO8Qn-OiJKMa2Ghcntz6FbX27iYBnJUTNsIGG5UFHAkXzfv19HTc7FNIzVVlOEMThe3DQSJXbonld_NgjA?purpose=fullsize)

![Image](https://images.openai.com/static-rsc-4/TpN9OIvHcIk6SH1WcVRoTRlxmNt6rQ09-IrwJYsTDb39Fb4pOGzyEloyy6AEENsScIkBJFyzkPhMz1sbljHwh4M6FpaXAg6V__ytG8_8rV7VR9XUVNn26BQRtdD6-o-5urNejsnqdmiZ93K1TR7mULlndCA35q7gXHEfafRr5dlbHOS8WU4DshE8mPgDJ-qX?purpose=fullsize)

The UI should feel:

* minimal
* elegant
* editorial
* spacious
* calm
* simple

### Visual style

**Background**

* Warm cream / off-white

**Primary text**

* Black / very dark brown

**Accent**

* Small orange accent

**Typography**

* Large serif heading
* Clean sans-serif body text
* Monospace/small uppercase labels where appropriate

### Avoid

* dashboards with many cards
* gradients
* excessive animations
* complicated navigation
* unnecessary icons
* excessive colors
* complex sidebar
* unnecessary charts

---

# 5. Main Page

The main page should be a single simple workflow.

### Header

```text
Mail Hunt                                      Connect Gmail
```

Left:

**Mail Hunt**

Right:

**Connect Gmail**

If Gmail is connected:

```text
✓ Gmail Connected
```

---

# 6. Hero Section

Similar to the attached UI:

### Small label

```text
AI INTERNSHIP OUTREACH
```

### Main heading

```text
Send your internship
emails in one go.
```

### Supporting text

```text
Paste recruiter emails below.
Your application email and resume will be sent individually through Gmail.
```

---

# 7. Recruiter Email Input

Large textarea.

### Label

```text
RECRUITER EMAILS
```

### Placeholder

```text
Paste email addresses — one per line

hr@company.com
recruiter@startup.com
careers@company.com
```

The user can paste:

```text
email1@gmail.com
email2@gmail.com
hr@company.com
recruiter@startup.com
```

### Automatically handle

* blank lines
* duplicate emails
* invalid email formats

Example:

```text
47 valid emails
2 duplicates removed
1 invalid email
```

No need for Excel or CSV.

---

# 8. Email Content Section

The user should be able to edit the email.

### Subject

```text
Subject

AI Internship Application – Bansari Naik
```

### Body

Large editable text area.

Example:

```text
Dear Hiring Team,

I am Bansari Naik, a final-year B.Tech student specializing in
Artificial Intelligence and Data Science at DJSCE, Mumbai.

I am currently looking for an AI internship opportunity where I can
work on practical AI systems and contribute to an engineering team.

I have hands-on experience working with agentic AI workflows,
RAG-based systems, backend APIs and full-stack applications.

I have attached my resume for your consideration.

GitHub: https://github.com/...
LinkedIn: https://linkedin.com/in/...

Thank you for your time.

Best regards,
Bansari Naik
```

The email content should be **editable**.

The application should not force AI-generated personalization.

---

# 9. Resume Upload

Simple upload component:

```text
RESUME

┌─────────────────────────────────────┐
│  Drop your resume here              │
│  or choose a PDF                    │
└─────────────────────────────────────┘

✓ Bansari_Naik_Resume.pdf
```

Requirements:

* PDF only
* One resume
* Resume attached to every email
* Do not permanently store the resume on a server

The backend can temporarily receive the file while sending emails and then discard it.

---

# 10. Gmail Connection

The header should contain:

```text
[ Connect Gmail ]
```

When clicked:

```text
Connect your Gmail

Mail Hunt needs permission to send emails
from your Gmail account.

[ Continue with Google ]
```

Google OAuth flow:

```text
Next.js
   ↓
FastAPI
   ↓
Google OAuth
   ↓
User signs into Google
   ↓
User grants Gmail send permission
   ↓
OAuth token
   ↓
Gmail API
```

The application should not collect the Gmail password.

---

# 11. Preview

Before sending, show a simple preview.

Example:

```text
READY TO SEND

47 recipients
1 resume
1 email template


To:
hr@company.com

Subject:
AI Internship Application – Bansari Naik

--------------------------------

Dear Hiring Team,

I am Bansari Naik...

...

GitHub: ...
LinkedIn: ...

--------------------------------

Attachment:
✓ Bansari_Naik_Resume.pdf


              [ Send All ]
```

---

# 12. Sending

When the user clicks:

**Send All**

the backend sends each email **individually**.

It should NOT send:

```text
To: recruiter1
CC: recruiter2
CC: recruiter3
```

Instead:

```text
Email 1 → recruiter1
Email 2 → recruiter2
Email 3 → recruiter3
```

This keeps each recruiter separate.

---

# 13. Sending Progress

While sending, show simple progress.

Example:

```text
Sending applications...

████████████████░░░░░░░░  32 / 47


✓ hr@company1.com
✓ recruiter@company2.com
✓ careers@company3.com
⟳ hr@company4.com
○ recruiter@company5.com
```

Don't make the user wait on a blank screen.

---

# 14. Final Result

After completion:

```text
ALL DONE

43 emails sent
4 emails failed

✓ 43 Sent
× 4 Failed


[ View Failed ]
[ Send Again ]
```

For failed emails, show:

```text
hr@company.com
Reason: Gmail API error
```

Do not automatically retry indefinitely.

---

# 15. Duplicate Handling

If the user pastes:

```text
hr@abc.com
hr@abc.com
recruiter@xyz.com
hr@abc.com
```

the app should automatically convert it to:

```text
hr@abc.com
recruiter@xyz.com
```

and show:

```text
2 duplicate entries removed
```

---

# 16. Session Behavior

Because there is **no database**, don't try to build permanent recruiter management.

The application only needs to maintain data during the current session.

For convenience, these can optionally be stored in browser `localStorage`:

```text
Name
Email
GitHub URL
LinkedIn URL
Default subject
Default email body
```

Recruiter emails don't need to be permanently stored.

---

# 17. Backend API

Keep the FastAPI backend small.

### `GET /auth/google`

Starts Google OAuth.

### `GET /auth/google/callback`

Handles OAuth callback.

### `POST /send`

Receives:

```text
recipients[]
subject
body
resume
```

and sends the emails using Gmail API.

### `GET /auth/status`

Returns:

```json
{
  "connected": true
}
```

### `POST /auth/logout`

Clears the current OAuth session/token.

That's enough for V1.

---

# 18. Suggested Project Structure

```text
mail-hunt/
│
├── frontend/
│   ├── app/
│   ├── components/
│   ├── lib/
│   └── ...
│
├── backend/
│   ├── main.py
│   ├── gmail.py
│   ├── auth.py
│   ├── email_sender.py
│   └── requirements.txt
│
├── README.md
└── .gitignore
```

Keep the backend modules simple. Don't over-engineer it.

---

# 19. Google OAuth README Requirement

The project **must include a detailed `README.md` explaining Google OAuth setup**.

The README should contain:

### Prerequisites

```text
Python
Node.js
Google account
Google Cloud account
```

### Google Cloud setup

Explain step-by-step:

1. Create a Google Cloud project.
2. Enable Gmail API.
3. Configure OAuth consent screen.
4. Create OAuth credentials.
5. Select the appropriate application type.
6. Add the required redirect URI.
7. Download the credentials JSON.
8. Place it in the backend as instructed.
9. Add required environment variables.

### Environment variables

Example:

```env
GOOGLE_CLIENT_ID=
GOOGLE_CLIENT_SECRET=
GOOGLE_REDIRECT_URI=
```

Do **not** put actual credentials in the repository.

### Running the project

Frontend:

```bash
npm install
npm run dev
```

Backend:

```bash
pip install -r requirements.txt
uvicorn main:app --reload
```

### Gmail authorization

Explain:

```text
Open application
        ↓
Click Connect Gmail
        ↓
Google login
        ↓
Grant Gmail permission
        ↓
Return to Mail Hunt
```

### Security

README should explicitly explain:

* Never commit OAuth credentials.
* Never commit access/refresh tokens.
* Never put Google client secrets in the frontend.
* Use `.env`.
* Add `.env` and credential files to `.gitignore`.

---

# 20. `.gitignore`

Include at minimum:

```text
.env
credentials.json
token.json
__pycache__/
node_modules/
.next/
```

---

# 21. Error Handling

Keep errors understandable.

### Gmail not connected

```text
Connect your Gmail account before sending.
```

### No emails

```text
Paste at least one recruiter email.
```

### Invalid emails

```text
3 invalid email addresses were removed.
```

### No resume

```text
Please upload your resume.
```

### Gmail error

```text
We couldn't send this email.
Please check your Gmail connection and try again.
```

Don't expose raw Python stack traces to the UI.

---

# 22. Important Scope Limitations

For V1, **do not build**:

* database
* user registration
* login system
* admin panel
* recruiter CRM
* email open tracking
* analytics dashboard
* LinkedIn integration
* recruiter scraping
* AI recruiter discovery
* AI-generated company research
* automatic follow-ups
* scheduling system
* multiple Gmail accounts
* subscription/payment system

The whole point is to keep this as a **small personal tool**.

---

# 23. V1 User Flow

```text
                    MAIL HUNT
                       │
                       ↓
              Paste recruiter emails
                       │
                       ↓
              Validate + deduplicate
                       │
                       ↓
              Enter/edit email
                       │
                       ↓
                 Upload resume
                       │
                       ↓
                 Connect Gmail
                       │
                       ↓
                    Preview
                       │
                       ↓
                   SEND ALL
                       │
             ┌─────────┴─────────┐
             ↓                   ↓
           Sent                Failed
             │                   │
             └─────────┬─────────┘
                       ↓
                   Done
```

---

# 24. Definition of Done

The project is complete when I can:

* Open the Next.js website.
* Paste 50+ recruiter emails at once.
* Have invalid/duplicate emails automatically handled.
* See the number of valid recipients.
* Enter/edit my email subject and body.
* Upload my resume PDF.
* Connect my Gmail through Google OAuth.
* Preview the email.
* Click **Send All**.
* Have each recruiter receive an individual email.
* Have the same resume attached to each email.
* See which emails succeeded/failed.
* Run the project locally using the README instructions.
* Understand exactly how to configure Google OAuth from the README.
* Have **no database** and no unnecessary backend infrastructure.

### Overall product philosophy

> **One page. One workflow. Minimal UI. No database. No unnecessary AI. No unnecessary features.**

The attached **Mail Hunt** design should be treated as the visual direction: large editorial typography, warm background, lots of whitespace, subtle orange accents, and a very focused interface rather than a traditional SaaS dashboard.
