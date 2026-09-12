# InterviewIQ

AI-Powered Smart Interview Analyzer — a full-stack internship project for practising mock interviews, analysing answers, and tracking progress.

**Practice. Analyze. Improve. Get Interview Ready.**

## Project overview

InterviewIQ is a Flask website where students:

1. Create an account and log in
2. Choose interview type, difficulty, job role, and question count
3. Answer by microphone (Web Speech API) or by typing
4. Get a score from Python analysis (and optional Gemini feedback)
5. Finish a round, save a report, and review history and charts

The code is intentionally simple so it can be explained in a college viva. There is no React, no custom ML model, and no Docker.

## Features

- Signup / login with hashed passwords and Flask sessions
- Student dashboard with readiness, averages, and a Chart.js line graph
- Interview setup: HR, Technical, Behavioral, General
- Live interview room with timer, voice, and text
- Filler-word detection, WPM, keyword relevance, completeness
- Gemini JSON feedback through the Flask backend only
- Graceful fallbacks if MongoDB, Gemini, or speech are unavailable
- Final report, history filters, progress analytics, profile, dark/light mode

## Technologies

| Layer | Technology |
| --- | --- |
| Frontend | HTML5, CSS3, Vanilla JavaScript, Bootstrap 5, Bootstrap Icons, Chart.js |
| Backend | Python 3, Flask |
| Database | MongoDB Atlas via PyMongo (in-memory demo mode if Atlas is down) |
| Auth | Flask sessions, Werkzeug password hashing |
| AI | Gemini API (server-side `requests`) |
| Speech | Browser Web Speech API |
| Config | python-dotenv |

## Folder structure

```
InterviewIQ/
├── app.py                 # Flask routes and interview flow
├── database.py            # MongoDB + in-memory demo store
├── requirements.txt
├── .env.example
├── README.md
├── VIVA_NOTES.md
├── services/
│   ├── analyzer.py        # WPM, fillers, keywords, scoring
│   ├── ai_service.py      # Gemini call + fallback
│   └── questions.py       # Question bank
├── templates/             # Jinja HTML pages
└── static/
    ├── css/style.css
    └── js/main.js, interview.js, charts.js
```

`templates/base.html` is a shared layout (navbar, footer, theme). `templates/error.html` shows friendly 404/500 pages.

## Installation

### 1. Python 3

Use Python 3.9 or newer.

### 2. Virtual environment

macOS / Linux:

```bash
cd InterviewIQ
python3 -m venv .venv
source .venv/bin/activate
```

Windows:

```bash
cd InterviewIQ
python -m venv .venv
.venv\Scripts\activate
```

### 3. Dependencies

```bash
pip install -r requirements.txt
```

Packages installed: Flask, PyMongo, python-dotenv, requests, Werkzeug (with Flask), gunicorn (optional production server).

## MongoDB Atlas setup (optional but recommended)

1. Create a free cluster at [MongoDB Atlas](https://www.mongodb.com/cloud/atlas)
2. Add a database user
3. Allow your IP (or `0.0.0.0/0` for a short demo)
4. Copy the connection string
5. Put it in `.env` as `MONGO_URI`

If `MONGO_URI` is empty or Atlas cannot be reached, InterviewIQ **automatically uses demo mode**: users and interviews stay in memory until the server restarts. The UI still works for a presentation.

## Gemini API setup (optional)

1. Open [Google AI Studio](https://aistudio.google.com/apikey)
2. Create an API key
3. Put it in `.env` as `GEMINI_API_KEY`

The key is read only in `services/ai_service.py`. It is never sent to the browser.

If the key is missing or Gemini fails, the app uses basic Python analysis and shows a clear message. Interviews do not crash.

## .env setup

```bash
cp .env.example .env
```

Edit `.env`:

```
SECRET_KEY=any-long-random-string
MONGO_URI=
GEMINI_API_KEY=
GEMINI_MODEL=gemini-2.0-flash
```

Leave `MONGO_URI` and `GEMINI_API_KEY` blank for a local demo.

## How to run

```bash
source .venv/bin/activate   # if not already active
python app.py
```

Open: **http://127.0.0.1:5000**

Demo path:

1. Sign up
2. Dashboard
3. Start New Interview
4. Answer (type or speak)
5. Read analysis
6. Finish the round
7. Open History and Progress

## Troubleshooting

| Problem | What to do |
| --- | --- |
| Page will not load | Confirm `python app.py` is running and visit http://127.0.0.1:5000 |
| Duplicate email | Use another email; the app blocks duplicates |
| Invalid login | Check email/password; passwords are hashed, so they cannot be recovered from the database |
| Microphone does nothing | Use Chrome if possible, allow mic permission, or type the answer |
| No AI comments | Set `GEMINI_API_KEY` or present the basic-analysis fallback |
| Data disappeared after restart | You were in demo mode. Add a working `MONGO_URI` |
| Charts empty | Complete at least one interview; empty states are intentional |

## Architecture

```
Browser (HTML/CSS/JS)
    → Flask routes in app.py
        → database.py  (MongoDB or memory)
        → services/questions.py
        → services/analyzer.py
        → services/ai_service.py  (Gemini HTTPS)
```

- **Cookie session** stores only `user_id` and name (small).
- **Live interview state** is a server dictionary `LIVE_INTERVIEWS` so long answers do not overflow the cookie.
- **Completed interviews** are saved to MongoDB or the in-memory demo store.

### Scoring (from `services/analyzer.py`)

```
overall =
    0.25 * relevance +
    0.20 * completeness +
    0.15 * pace +
    0.15 * filler_score +
    0.25 * AI blend (or basic average if Gemini is off)
```

WPM = word count / duration in minutes.

## Viva concepts

See `VIVA_NOTES.md` for 30+ likely questions that match this codebase (Flask, sessions, hashing, MongoDB, WPM, fillers, Gemini, Chart.js, security).
