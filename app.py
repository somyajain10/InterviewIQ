"""
InterviewIQ — AI-Powered Smart Interview Analyzer
Flask application entry point.

Run:
    python app.py
Then open http://127.0.0.1:5000
"""

import os
import uuid
from datetime import datetime
from functools import wraps

from flask import (
    Flask,
    flash,
    redirect,
    render_template,
    request,
    session,
    url_for,
)
from werkzeug.security import check_password_hash, generate_password_hash
from dotenv import load_dotenv

import database
from services.analyzer import analyze_answer, readiness_score, summarize_interview
from services.ai_service import get_ai_feedback, gemini_configured
from services.questions import select_questions

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "interviewiq-dev-secret-change-me")

# Live interviews are stored on the server (not in the cookie session)
# because answers and analysis would exceed cookie size.
LIVE_INTERVIEWS = {}

VALID_TYPES = {"HR", "Technical", "Behavioral", "General"}
VALID_DIFFICULTIES = {"Easy", "Medium", "Hard", "Beginner", "Intermediate", "Advanced"}
VALID_COUNTS = {3, 5, 10, 15}
VALID_ROLES = {"Software Developer", "Web Developer", "Data Analyst", "General"}


def login_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        if not session.get("user_id"):
            flash("Please log in to continue.", "warning")
            return redirect(url_for("login"))

        user = current_user()

        if not user:
            session.clear()
            flash("Your session has expired. Please log in again.", "warning")
            return redirect(url_for("login"))

        return view(*args, **kwargs)

    return wrapped


def current_user():
    return database.find_user_by_id(session.get("user_id"))


def status_flags():
    return {
        "demo_db": database.is_demo_mode(),
        "db_message": database.db_status_message(),
        "gemini_ready": gemini_configured(),
    }


def format_date(value):
    if not value:
        return "—"
    text = str(value)
    try:
        if "T" in text:
            dt = datetime.fromisoformat(text.replace("Z", ""))
            return dt.strftime("%d %b %Y, %I:%M %p")
        return text[:16]
    except ValueError:
        return text[:16]


app.jinja_env.filters["when"] = format_date


@app.context_processor
def inject_globals():
    user = current_user() if session.get("user_id") else None
    flags = status_flags()
    return {
        "current_user": user,
        "demo_db": flags["demo_db"],
        "gemini_ready": flags["gemini_ready"],
    }


# -------------------- Public pages --------------------

@app.route("/")
def index():
    if session.get("user_id"):
        return redirect(url_for("dashboard"))
    return render_template("index.html")


@app.route("/signup", methods=["GET", "POST"])
def signup():
    if session.get("user_id"):
        return redirect(url_for("dashboard"))
    if request.method == "POST":
        name = (request.form.get("name") or "").strip()
        email = (request.form.get("email") or "").strip().lower()
        password = request.form.get("password") or ""
        confirm = request.form.get("confirm") or ""

        if len(name) < 2:
            flash("Please enter your full name.", "danger")
        elif "@" not in email or "." not in email.split("@")[-1]:
            flash("Please enter a valid email address.", "danger")
        elif len(password) < 6:
            flash("Password must be at least 6 characters.", "danger")
        elif password != confirm:
            flash("Password and confirm password do not match.", "danger")
        else:
            user, error = database.create_user(name, email, generate_password_hash(password))
            if error:
                flash(error, "danger")
            else:
                session["user_id"] = user["id"]
                session["user_name"] = user["name"]
                flash("Welcome to InterviewIQ. Your account is ready.", "success")
                return redirect(url_for("dashboard"))
    return render_template("signup.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if session.get("user_id"):
        return redirect(url_for("dashboard"))
    if request.method == "POST":
        email = (request.form.get("email") or "").strip().lower()
        password = request.form.get("password") or ""
        user = database.find_user_by_email(email)
        if not user or not check_password_hash(user.get("password_hash") or "", password):
            flash("Invalid email or password.", "danger")
        else:
            session["user_id"] = user["id"]
            session["user_name"] = user["name"]
            flash(f"Welcome back, {user['name'].split()[0]}.", "success")
            return redirect(url_for("dashboard"))
    return render_template("login.html")


@app.route("/logout")
def logout():
    user_id = session.get("user_id")
    if user_id:
        LIVE_INTERVIEWS.pop(user_id, None)
    session.clear()
    flash("You have been logged out.", "success")
    return redirect(url_for("index"))


# -------------------- Dashboard & profile --------------------

@app.route("/dashboard")
@login_required
def dashboard():
    user = current_user()
    interviews = database.list_interviews(user["id"], sort="newest")
    scores = [i.get("overall_score") or 0 for i in interviews]
    stats = {
        "count": len(interviews),
        "average": round(sum(scores) / len(scores)) if scores else 0,
        "best": max(scores) if scores else 0,
        "readiness": readiness_score(interviews),
        "chart_labels": [format_date(i.get("created_at")) for i in reversed(interviews[-8:])],
        "chart_scores": [i.get("overall_score") or 0 for i in reversed(interviews[-8:])],
        "recent": interviews[:5],
    }
    return render_template("dashboard.html", user=user, stats=stats, **status_flags())


@app.route("/profile", methods=["GET", "POST"])
@login_required
def profile():
    user = current_user()
    if request.method == "POST":
        name = (request.form.get("name") or "").strip()
        if len(name) < 2:
            flash("Please enter a valid name.", "danger")
        else:
            updated = database.update_user_name(user["id"], name)
            if updated:
                session["user_name"] = updated["name"]
                user = updated
                flash("Profile updated.", "success")
            else:
                flash("Could not update profile.", "danger")
    created = format_date(user.get("created_at"))
    return render_template("profile.html", user=user, created=created, **status_flags())


# -------------------- Interview flow --------------------

@app.route("/setup", methods=["GET", "POST"])
@login_required
def setup():
    if request.method == "POST":
        interview_type = request.form.get("interview_type")
        difficulty = request.form.get("difficulty")
        job_role = request.form.get("job_role")
        try:
            count = int(request.form.get("count") or 0)
        except ValueError:
            count = 0

        if interview_type not in VALID_TYPES:
            flash("Please choose a valid interview type.", "danger")
        elif difficulty not in VALID_DIFFICULTIES:
            flash("Please choose a valid difficulty.", "danger")
        elif count not in VALID_COUNTS:
            flash("Please choose 5, 10, or 15 questions.", "danger")
        elif job_role not in VALID_ROLES:
            flash("Please choose a valid job role.", "danger")
        else:
            questions = select_questions(interview_type, difficulty, count)
            live = {
                "id": str(uuid.uuid4()),
                "user_id": session["user_id"],
                "type": interview_type,
                "difficulty": difficulty,
                "job_role": job_role,
                "questions": questions,
                "answers": [],
                "current": 0,
                "started_at": datetime.utcnow().isoformat(),
            }
            LIVE_INTERVIEWS[session["user_id"]] = live
            return redirect(url_for("interview"))
    return render_template("setup.html")


def _get_live():
    return LIVE_INTERVIEWS.get(session.get("user_id"))


@app.route("/interview")
@login_required
def interview():
    live = _get_live()
    if not live:
        flash("Start an interview from setup first.", "warning")
        return redirect(url_for("setup"))
    index = live["current"]
    if index >= len(live["questions"]):
        return redirect(url_for("finalize_interview"))
    question = live["questions"][index]
    progress = round((index / len(live["questions"])) * 100)
    return render_template(
        "interview.html",
        live=live,
        question=question,
        number=index + 1,
        total=len(live["questions"]),
        progress=progress,
    )


@app.route("/interview/submit", methods=["POST"])
@login_required
def submit_answer():
    live = _get_live()
    if not live:
        flash("Your interview session expired. Please start again.", "warning")
        return redirect(url_for("setup"))

    answer = (request.form.get("answer") or "").strip()
    skipped = request.form.get("skipped") == "1"
    typed = request.form.get("typed") == "1"
    try:
        duration = float(request.form.get("duration") or 0)
    except ValueError:
        duration = 0

    if not skipped and len(answer) < 8:
        flash("Please speak or type a longer answer before submitting.", "danger")
        return redirect(url_for("interview"))

    index = live["current"]
    question = live["questions"][index]
    if skipped:
        analysis = {
            "overall": 0,
            "relevance": 0,
            "clarity": 0,
            "completeness": 0,
            "communication": 0,
            "word_count": 0,
            "duration_seconds": 0,
            "wpm": None,
            "pace_note": "Question skipped.",
            "filler_total": 0,
            "filler_details": {},
            "matched_keywords": [],
            "communication_feedback": "This question was skipped. Speech pacing and communication clarity could not be measured.",
            "content_feedback": "This question was skipped. Make sure to attempt all questions to demonstrate technical vocabulary and completeness.",
            "strengths": [],
            "weaknesses": ["This question was skipped, so it scored 0."],
            "suggestions": ["Attempt every question. Even a partial answer earns valuable practice points."],
            "improved_answer": "",
            "ai_used": False,
            "ai_message": "Question skipped.",
            "skipped": True,
        }
    else:
        ai_result = get_ai_feedback(question["text"], answer, live["type"], live["difficulty"])
        analysis = analyze_answer(
            question=question["text"],
            answer=answer,
            interview_type=live["type"],
            difficulty=live["difficulty"],
            duration_seconds=duration,
            typed=typed,
            extra_keywords=question.get("keywords"),
            ai_result=ai_result,
        )
        analysis["skipped"] = False

    live["answers"].append({
        "question": question["text"],
        "answer": answer if not skipped else "",
        "skipped": skipped,
        "analysis": analysis,
    })
    live["last_analysis"] = analysis
    live["last_question"] = question["text"]
    live["last_answer"] = answer if not skipped else ""
    return redirect(url_for("analysis"))


@app.route("/analysis")
@login_required
def analysis():
    live = _get_live()
    if not live or not live.get("last_analysis"):
        flash("No answer to analyze yet.", "warning")
        return redirect(url_for("interview"))
    index = live["current"]
    total = len(live["questions"])
    is_last = index + 1 >= total
    return render_template(
        "analysis.html",
        analysis=live["last_analysis"],
        question=live.get("last_question"),
        answer=live.get("last_answer"),
        number=index + 1,
        total=total,
        is_last=is_last,
        live=live,
    )


@app.route("/analysis/continue", methods=["POST"])
@login_required
def analysis_continue():
    live = _get_live()
    if not live:
        return redirect(url_for("setup"))
    live["current"] += 1
    live["last_analysis"] = None
    if live["current"] >= len(live["questions"]):
        return redirect(url_for("finalize_interview"))
    return redirect(url_for("interview"))


@app.route("/interview/complete")
@login_required
def finalize_interview():
    live = _get_live()
    if not live or not live.get("answers"):
        flash("Complete at least one question to see a report.", "warning")
        return redirect(url_for("setup"))

    answer_results = [a["analysis"] for a in live["answers"]]
    summary = summarize_interview(answer_results)
    record = {
        "user_id": live["user_id"],
        "type": live["type"],
        "difficulty": live["difficulty"],
        "job_role": live["job_role"],
        "questions": [q["text"] for q in live["questions"]],
        "answers": live["answers"],
        "scores": {
            "communication": summary["communication"],
            "clarity": summary["clarity"],
            "relevance": summary["relevance"],
            "completeness": summary["completeness"],
        },
        "overall_score": summary["overall_score"],
        "performance_category": summary.get("performance_category", "Good (Interview Ready)"),
        "summary": summary,
        "ai_available": any(a["analysis"].get("ai_used") for a in live["answers"]),
        "created_at": datetime.utcnow().isoformat(),
    }
    interview_id = database.save_interview(record)
    LIVE_INTERVIEWS.pop(session["user_id"], None)
    return redirect(url_for("report", interview_id=interview_id))


@app.route("/report/<interview_id>")
@login_required
def report(interview_id):
    user = current_user()
    item = database.get_interview(interview_id, user["id"])
    if not item:
        flash("That report was not found.", "danger")
        return redirect(url_for("history"))
    return render_template("report.html", item=item, detailed=request.args.get("detailed") == "1")


# -------------------- History & progress --------------------

@app.route("/history")
@login_required
def history():
    user = current_user()
    interview_type = request.args.get("type") or ""
    difficulty = request.args.get("difficulty") or ""
    sort = request.args.get("sort") or "newest"
    items = database.list_interviews(
        user["id"],
        interview_type=interview_type or None,
        difficulty=difficulty or None,
        sort=sort,
    )
    return render_template(
        "history.html",
        items=items,
        selected_type=interview_type,
        selected_difficulty=difficulty,
        selected_sort=sort,
    )


@app.route("/progress")
@login_required
def progress():
    user = current_user()
    interviews = database.list_interviews(user["id"], sort="oldest")
    scores = [i.get("overall_score") or 0 for i in interviews]
    by_type = {}
    for item in interviews:
        bucket = by_type.setdefault(item.get("type") or "General", [])
        bucket.append(item.get("overall_score") or 0)
    category_labels = list(by_type.keys())
    category_scores = [round(sum(v) / len(v)) for v in by_type.values()]

    strongest = weakest = None
    if category_scores:
        strongest = category_labels[category_scores.index(max(category_scores))]
        weakest = category_labels[category_scores.index(min(category_scores))]

    suggestions = []
    if not interviews:
        suggestions = [
            "Complete your first mock interview to unlock progress analytics.",
            "Start with a Beginner HR round if you are new to interviews.",
            "Practice speaking answers out loud, then review filler words.",
        ]
    else:
        if scores and sum(scores) / len(scores) < 70:
            suggestions.append("Your average is under 70%. Repeat the same type until the score rises.")
        if weakest:
            suggestions.append(f"Your weakest category is {weakest}. Schedule another {weakest} interview.")
        suggestions.append("Use the improved-answer examples after each question and retry similar topics.")
        suggestions.append("Track filler words. Pausing is better than saying 'um' or 'like'.")

    stats = {
        "count": len(interviews),
        "average": round(sum(scores) / len(scores)) if scores else 0,
        "best": max(scores) if scores else 0,
        "readiness": readiness_score(list(reversed(interviews))),
        "labels": [format_date(i.get("created_at")) for i in interviews],
        "scores": scores,
        "category_labels": category_labels,
        "category_scores": category_scores,
        "strongest": strongest,
        "weakest": weakest,
        "suggestions": suggestions[:4],
    }
    return render_template("progress.html", stats=stats)


@app.errorhandler(404)
def not_found(_error):
    return render_template("error.html", code=404, message="That page does not exist."), 404


@app.errorhandler(500)
def server_error(_error):
    return render_template("error.html", code=500, message="Something went wrong. Please try again."), 500


if __name__ == "__main__":
    print("InterviewIQ")
    print(database.db_status_message())
    print("Gemini:", "configured" if gemini_configured() else "not configured (basic analysis fallback)")
    print("Open http://127.0.0.1:5000")
    app.run(debug=True)
