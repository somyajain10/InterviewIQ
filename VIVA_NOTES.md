# InterviewIQ — Viva Notes

These answers describe **this project’s actual code**, not generic theory. Read `app.py`, `database.py`, `services/analyzer.py`, and `services/ai_service.py` once before the viva.

---

### 1. What is InterviewIQ?
A Flask web app where students practise mock interviews, get scores, and save reports. Frontend is HTML, CSS, and JavaScript. Backend is Python. Database is MongoDB Atlas with an in-memory fallback.

### 2. Why Flask?
Flask is a lightweight Python web framework. One file (`app.py`) maps URLs to functions. That is easy to explain in a viva compared with Django or Node.js.

### 3. What is a route?
A route connects a URL to a Python function. Example: `@app.route("/login")` runs `login()` when the browser opens `/login`.

### 4. Difference between GET and POST?
GET loads a page. POST submits form data (signup, login, answers). Sensitive data like passwords is sent with POST, not in the URL.

### 5. What is Jinja2?
Jinja is Flask’s template engine. Files in `templates/` mix HTML with `{{ variable }}` and `{% if %}`. `base.html` is reused by every page.

### 6. How does the frontend talk to the backend?
The browser requests Flask URLs. Forms POST to routes such as `/interview/submit`. Flask returns a new HTML page. Chart.js only draws numbers that Flask already computed.

### 7. What is HTML5 used for?
Page structure: forms, textarea, buttons, semantic sections on the landing page, and canvas tags for Chart.js.

### 8. What is CSS3 used for?
`static/css/style.css` defines colors, cards, dark mode via `html[data-theme="dark"]`, layout grids, and simple animations.

### 9. How does dark/light mode work?
`main.js` reads `localStorage` key `interviewiq-theme` and sets `data-theme` on `<html>`. CSS variables change with that attribute. Preference stays in the browser, not in MongoDB.

### 10. Why Bootstrap 5?
It gives a responsive grid, navbar collapse, forms, and accordion FAQ through a CDN. Custom CSS still provides the InterviewIQ look.

### 11. What does JavaScript do here?
Theme toggle, Web Speech API, interview timer, submit overlay (“Analyzing your response...”), and Chart.js helpers in `charts.js`. No React.

### 12. What is the Web Speech API?
A browser API (`SpeechRecognition` / `webkitSpeechRecognition`) that turns microphone audio into text. Implemented in `static/js/interview.js`. If the API is missing, the textarea still works.

### 13. Why is speech handled in the browser, not Python?
Speech-to-text runs in Chrome using the Web Speech API. That avoids extra Python audio libraries. Flask only receives the final text.

### 14. How are passwords stored?
`werkzeug.security.generate_password_hash` on signup. Login uses `check_password_hash`. Plain-text passwords are never saved. See `app.py` signup/login.

### 15. What is a Flask session?
After login, Flask stores `user_id` (and name) in a signed cookie using `SECRET_KEY`. `@login_required` blocks pages if `session["user_id"]` is missing.

### 16. Why not store the whole interview in the session cookie?
Cookies are small (~4 KB). Answers plus analysis would overflow. Live interviews are kept in the server dict `LIVE_INTERVIEWS` in `app.py`.

### 17. What is MongoDB?
A NoSQL document database. InterviewIQ uses two collections conceptually: `users` and `interviews`. Documents are JSON-like, which fits nested answers.

### 18. What is PyMongo?
The official Python driver. `database.py` uses `MongoClient`, `insert_one`, `find_one`, and `find`.

### 19. What is MongoDB Atlas?
MongoDB’s cloud service. `MONGO_URI` in `.env` is the connection string. The app pings Atlas on startup.

### 20. What is demo / fallback database mode?
If `MONGO_URI` is empty or ping fails, `USE_DEMO_DB = True` and data is stored in Python dictionaries `_demo_users` and `_demo_interviews`. The UI does not look broken; a chip on the dashboard says demo mode. Data resets when the server stops.

### 21. User schema?
`name`, `email`, `password_hash`, `created_at`. Email is unique (index on Atlas; dictionary key in demo mode).

### 22. Interview schema?
`user_id`, `type`, `difficulty`, `job_role`, `questions`, `answers`, `scores`, `overall_score`, `created_at`, plus `summary` and `ai_available`.

### 23. How are questions chosen?
`services/questions.py` holds a bank by type and difficulty. `random.sample` picks 5, 10, or 15 questions. If more are needed than stored, nearby difficulties of the same type are added.

### 24. How is word count calculated?
`tokenize()` in `analyzer.py` uses a regex `[a-zA-Z']+` and counts tokens.

### 25. What is WPM?
Words per minute: `word_count / (duration_seconds / 60)`. Duration comes from the JavaScript timer posted as a hidden field. Typed or very short answers get a **neutral pace score of 75** so typing does not fake a huge WPM.

### 26. How are filler words detected?
The list is `um`, `umm`, `uh`, `like`, `basically`, `actually`, `you know`. Longer phrases are counted first. Score falls by about 6 points per filler, capped.

### 27. How does keyword relevance work?
Keywords come from the question (words longer than 3 letters), the category list in `CATEGORY_KEYWORDS`, and optional question-bank keywords. Relevance is matched keywords divided by total keywords, scaled to 0–100.

### 28. Completeness score?
Each difficulty has an expected word range (Beginner 40–90, Intermediate 70–140, Advanced 100–200). Too short lowers the score; slightly long is still acceptable.

### 29. Overall scoring formula?
```
0.25 * relevance + 0.20 * completeness + 0.15 * pace
+ 0.15 * filler_score + 0.25 * AI blend
```
If Gemini fails, AI blend is the average of the four basic scores. Formula is in the `analyzer.py` docstring.

### 30. How is Gemini used?
`services/ai_service.py` POSTs to Google’s generateContent URL with `requests`. The prompt asks for JSON: relevance, clarity, completeness, communication, strengths, weaknesses, suggestions, improved answer. The API key is only on the server.

### 31. Why not call Gemini from JavaScript?
That would expose `GEMINI_API_KEY` in the browser. The project rule is: AI only through Flask.

### 32. What if Gemini is down?
`get_ai_feedback` returns `{ok: False, message: ...}`. `analyze_answer` still returns scores and rule-based comments. The analysis page shows a warning alert.

### 33. What is an API?
A way for two programs to talk over HTTP. Flask is our app API (routes). Gemini is an external API. Chart.js is a frontend library, not an API.

### 34. What does Chart.js do?
It draws line, bar, and radar charts from arrays Flask puts into the page (`stats.chart_scores`, report scores, progress categories). Empty arrays show an empty state, not a broken canvas.

### 35. How is input validated?
Signup checks name length, email shape, password length ≥ 6, and matching confirm. Setup only accepts known types, difficulties, counts, and roles. Empty answers under 8 characters are rejected unless Skip is used.

### 36. Security features?
Password hashing, signed sessions, `.env` secrets, server-side Gemini key, no raw Python tracebacks on 500 pages, users can only open their own reports (`get_interview` checks `user_id`).

### 37. How are errors shown to users?
`flash()` messages for login/signup. Custom `error.html` for 404/500. Invalid report IDs redirect to history with a flash. Speech and Gemini failures are written in plain language.

### 38. What happens on Skip?
`skipped=1` is posted. The answer is stored empty with score 0 and a suggestion to attempt the question. The student still moves forward so the demo cannot get stuck.

### 39. How is readiness calculated?
Average overall score of the latest up to 5 interviews (`readiness_score` in `analyzer.py`). New users see 0% and empty charts.

### 40. Frontend vs backend?
Frontend: pages, CSS, microphone, charts. Backend: accounts, question selection, scoring, Gemini, saving interviews. Database: persistence.

### 41. Why Python on the server?
The analysis functions are easier to write and explain in Python. Flask keeps routing in the same language as scoring.

### 42. Can you explain MVC in this project?
Templates = view, `app.py` routes = controller, `database.py` + services = model/business logic. It is a simple MVC-style split, not a strict framework pattern.

### 43. What would you add next?
Persist live interviews in MongoDB so a refresh cannot lose a round; email verification; more questions. These were skipped to keep the internship build simple and reliable.

### 44. Is this machine learning?
No custom model is trained. “AI” means calling Gemini. Basic scoring is if/else and counts. That is an important honest answer for the viva.

### 45. How do you run it for the demo?
Activate `.venv`, run `python app.py`, open http://127.0.0.1:5000, sign up, start a 5-question beginner HR interview, type an answer, show analysis, finish, open history.
