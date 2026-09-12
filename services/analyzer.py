"""
Simple, viva-friendly answer analysis.

Scoring formula (0-100), documented for the project viva:

    overall = (
        0.25 * relevance_score +
        0.20 * completeness_score +
        0.15 * pace_score +
        0.15 * filler_score +
        0.25 * ai_blend
    )

- relevance_score: keyword overlap between the answer and expected keywords
- completeness_score: how close the answer length is to an expected word range
- pace_score: speaking speed vs a healthy interview range (120-160 WPM)
- filler_score: fewer filler words => higher score
- ai_blend: average of Gemini scores when available, otherwise the average of the four basic scores

No machine-learning model is trained here. Everything is rule-based plus an optional Gemini call.
"""

import re
from collections import Counter

FILLER_WORDS = ["um", "umm", "uh", "like", "basically", "actually", "you know"]

# Expected keywords by interview type. Kept small and readable on purpose.
CATEGORY_KEYWORDS = {
    "HR": [
        "team", "learn", "strength", "weakness", "goal", "communication",
        "responsibility", "experience", "motivation", "company", "growth",
    ],
    "Technical": [
        "problem", "algorithm", "database", "code", "complexity", "debug",
        "api", "test", "data", "system", "function", "python", "javascript",
    ],
    "Behavioral": [
        "situation", "task", "action", "result", "team", "conflict",
        "deadline", "lead", "challenge", "improve", "feedback", "star",
    ],
    "General": [
        "prepare", "skill", "example", "goal", "learn", "project",
        "communication", "time", "plan", "improve",
    ],
}

EXPECTED_WORDS = {
    "Beginner": (40, 90),
    "Intermediate": (70, 140),
    "Advanced": (100, 200),
}

IDEAL_WPM_MIN = 120
IDEAL_WPM_MAX = 160


def tokenize(text):
    return re.findall(r"[a-zA-Z']+", (text or "").lower())


def word_count(text):
    return len(tokenize(text))


def count_filler_words(text):
    """
    Count filler words/phrases.
    Multi-word fillers such as "you know" are counted first so they
    are not split into unrelated single words.
    """
    lowered = " " + re.sub(r"[^a-zA-Z\s']", " ", (text or "").lower()) + " "
    counts = {}
    total = 0
    remaining = lowered
    for phrase in sorted(FILLER_WORDS, key=len, reverse=True):
        pattern = " " + phrase + " "
        found = remaining.count(pattern)
        counts[phrase] = found
        total += found
        remaining = remaining.replace(pattern, " ")
    return {"total": total, "details": counts}


def speaking_speed(words, duration_seconds, typed=False):
    """
    WPM = word_count / duration_in_minutes
    Typed answers (or very short durations) receive a neutral pace score.
    """
    duration_seconds = max(float(duration_seconds or 0), 0)
    if typed or duration_seconds < 3:
        wpm = round(words / (duration_seconds / 60.0), 1) if duration_seconds >= 3 else None
        return {"wpm": wpm, "score": 75, "note": "Pace scored neutrally because this answer was typed or too short to measure speech."}

    minutes = duration_seconds / 60.0
    wpm = words / minutes if minutes > 0 else 0
    if IDEAL_WPM_MIN <= wpm <= IDEAL_WPM_MAX:
        score = 100
        note = "Speaking pace is in a clear interview range."
    elif wpm < IDEAL_WPM_MIN:
        # Too slow: lose points as WPM drops
        score = max(40, 100 - (IDEAL_WPM_MIN - wpm) * 0.8)
        note = "Speaking pace is slower than a typical interview answer."
    else:
        score = max(40, 100 - (wpm - IDEAL_WPM_MAX) * 0.5)
        note = "Speaking pace is faster than a typical interview answer."
    return {"wpm": round(wpm, 1), "score": round(score), "note": note}


def relevance_score(answer, question, interview_type, extra_keywords=None):
    """
    Basic keyword matching:
    1. Collect keywords from the question, category list, and optional extras.
    2. Count how many of those keywords appear in the answer.
    3. relevance = matched / total_keywords * 100, with a small floor if the
       answer is reasonably long so empty keyword lists do not zero the score.
    """
    answer_tokens = set(tokenize(answer))
    question_tokens = [t for t in tokenize(question) if len(t) > 3]
    category_tokens = CATEGORY_KEYWORDS.get(interview_type, CATEGORY_KEYWORDS["General"])
    extra = extra_keywords or []

    keywords = []
    for token in question_tokens + category_tokens + extra:
        if token not in keywords and token not in {"what", "when", "where", "which", "your", "this", "that", "with", "from", "have", "would", "could", "should", "about"}:
            keywords.append(token)

    if not keywords:
        return {"score": 50, "matched": [], "keywords": []}

    matched = [k for k in keywords if k in answer_tokens]
    ratio = len(matched) / max(len(keywords), 1)
    score = round(min(100, ratio * 140))  # slight boost so 70% overlap is excellent
    if word_count(answer) >= 25 and score < 35:
        score = 35
    return {"score": score, "matched": matched[:12], "keywords": keywords[:16]}


def completeness_score(answer, difficulty):
    words = word_count(answer)
    low, high = EXPECTED_WORDS.get(difficulty, EXPECTED_WORDS["Beginner"])
    if words <= 8:
        return {"score": 20, "words": words, "note": "The answer is too short for this question."}
    if low <= words <= high:
        return {"score": 100, "words": words, "note": "Answer length looks complete for this difficulty."}
    if words < low:
        score = max(30, round(100 * (words / low)))
        return {"score": score, "words": words, "note": "The answer could include more detail."}
    # Longer than expected is still okay until it becomes rambling
    extra = words - high
    score = max(70, 100 - extra // 8)
    return {"score": score, "words": words, "note": "The answer is detailed; keep it focused."}


def filler_score(filler_total, words):
    if words == 0:
        return 0
    # Each filler word removes 6 points, capped.
    penalty = min(50, filler_total * 6)
    density = filler_total / words
    if density > 0.08:
        penalty = min(60, penalty + 10)
    return max(40, 100 - penalty) if filler_total else 100


def blend_ai_scores(basic_average, ai_result):
    if not ai_result or not ai_result.get("ok"):
        return basic_average
    parts = [
        ai_result.get("relevance_score"),
        ai_result.get("clarity_score"),
        ai_result.get("completeness_score"),
        ai_result.get("communication_score"),
    ]
    valid = [p for p in parts if isinstance(p, (int, float))]
    if not valid:
        return basic_average
    return round(sum(valid) / len(valid))


def get_performance_category(score):
    """Categorize overall interview performance for viva and student reports."""
    score = score or 0
    if score >= 85:
        return "Excellent"
    elif score >= 70:
        return "Good (Interview Ready)"
    elif score >= 50:
        return "Average (Needs Practice)"
    else:
        return "Foundational (Needs Improvement)"


def analyze_answer(question, answer, interview_type, difficulty, duration_seconds, typed=False, extra_keywords=None, ai_result=None):
    words = word_count(answer)
    fillers = count_filler_words(answer)
    pace = speaking_speed(words, duration_seconds, typed=typed)
    relevance = relevance_score(answer, question, interview_type, extra_keywords)
    completeness = completeness_score(answer, difficulty)
    f_score = filler_score(fillers["total"], words)

    basic_average = round((relevance["score"] + completeness["score"] + pace["score"] + f_score) / 4)
    ai_blend = blend_ai_scores(basic_average, ai_result)

    # Weighted overall score (see module docstring).
    overall = round(
        0.25 * relevance["score"]
        + 0.20 * completeness["score"]
        + 0.15 * pace["score"]
        + 0.15 * f_score
        + 0.25 * ai_blend
    )
    overall = max(0, min(100, overall))

    clarity = ai_result.get("clarity_score") if ai_result and ai_result.get("ok") else round((completeness["score"] + f_score) / 2)
    communication = ai_result.get("communication_score") if ai_result and ai_result.get("ok") else round((pace["score"] + f_score) / 2)
    ai_relevance = ai_result.get("relevance_score") if ai_result and ai_result.get("ok") else relevance["score"]
    ai_completeness = ai_result.get("completeness_score") if ai_result and ai_result.get("ok") else completeness["score"]

    strengths = []
    weaknesses = []
    suggestions = []
    improved = ""
    communication_feedback = ""
    content_feedback = ""
    ai_used = bool(ai_result and ai_result.get("ok"))

    if ai_used:
        strengths = ai_result.get("strengths") or []
        weaknesses = ai_result.get("weaknesses") or []
        suggestions = ai_result.get("suggestions") or []
        improved = ai_result.get("improved_answer") or ""
        communication_feedback = ai_result.get("communication_feedback") or ""
        content_feedback = ai_result.get("content_feedback") or ""
    else:
        if relevance["score"] >= 70:
            strengths.append("You used relevant terms that match the question.")
        if completeness["score"] >= 75:
            strengths.append("Your answer had enough detail for this difficulty level.")
        if f_score >= 85:
            strengths.append("You avoided heavy use of filler words.")
        if pace["score"] >= 80 and not typed:
            strengths.append("Your speaking pace was easy to follow.")
        if not strengths:
            strengths.append("You attempted the question and provided a starting answer.")

        if relevance["score"] < 65:
            weaknesses.append("The answer did not cover enough expected keywords for this topic.")
        if completeness["score"] < 65:
            weaknesses.append("The answer was shorter than expected for this difficulty.")
        if fillers["total"] >= 3:
            weaknesses.append("Filler words reduced how polished the answer sounded.")
        if pace["score"] < 65 and not typed:
            weaknesses.append("Speaking pace was outside a comfortable interview range.")
        if not weaknesses:
            weaknesses.append("Small improvements in structure and examples would make this stronger.")

        suggestions = [
            "Start with a direct one-sentence answer, then give one specific example.",
            "Use the STAR structure (Situation, Task, Action, Result) for clarity.",
            "Replace filler words with a deliberate 1-second pause.",
        ]
        improved = (
            "I would begin with a clear definition, support it with one specific example from a project or coursework, "
            "and close with the result or key takeaway. That structure keeps the answer relevant, concise, and complete."
        )

    # Rule-based fallback if communication/content feedback not provided by AI
    if not communication_feedback:
        if typed:
            comm_note = "Your response was submitted via text typing. Pace scored neutrally."
        elif pace["wpm"]:
            comm_note = f"Speaking speed was {pace['wpm']} WPM ({pace['note']})."
        else:
            comm_note = "Voice pacing could not be measured."

        if fillers["total"] > 0:
            active_fillers = [f"'{k}' ({v})" for k, v in fillers["details"].items() if v > 0]
            comm_note += f" Detected {fillers['total']} filler words: {', '.join(active_fillers)}. Practice substituting brief silent pauses for fillers."
        else:
            comm_note += " Excellent verbal discipline with zero filler words detected."
        communication_feedback = comm_note

    if not content_feedback:
        matched_str = ", ".join(relevance["matched"][:5]) if relevance["matched"] else "none"
        if relevance["score"] >= 70:
            content_feedback = f"Strong topical alignment! Successfully matched key concepts ({matched_str}). Word count ({words} words) fits the expected depth."
        elif relevance["score"] >= 45:
            content_feedback = f"Moderate relevance. Concepts matched: {matched_str}. Deepen your answer with specific technical terms and real-world project context."
        else:
            content_feedback = f"Limited keyword coverage for this {interview_type} topic. Focus on directly answering the core prompt using industry-standard terminology."

    return {
        "overall": overall,
        "relevance": round(ai_relevance),
        "clarity": round(clarity),
        "completeness": round(ai_completeness),
        "communication": round(communication),
        "word_count": words,
        "duration_seconds": round(float(duration_seconds or 0), 1),
        "wpm": pace["wpm"],
        "pace_note": pace["note"],
        "filler_total": fillers["total"],
        "filler_details": fillers["details"],
        "matched_keywords": relevance["matched"],
        "communication_feedback": communication_feedback,
        "content_feedback": content_feedback,
        "strengths": strengths if isinstance(strengths, list) else [str(strengths)],
        "weaknesses": weaknesses if isinstance(weaknesses, list) else [str(weaknesses)],
        "suggestions": suggestions if isinstance(suggestions, list) else [str(suggestions)],
        "improved_answer": improved,
        "ai_used": ai_used,
        "ai_message": None if ai_used else (ai_result or {}).get("message") or "AI feedback is unavailable. This result uses InterviewIQ explainable basic analysis.",
    }


def summarize_interview(answer_results):
    if not answer_results:
        return {
            "overall_score": 0,
            "performance_category": "Foundational (Needs Improvement)",
            "communication": 0,
            "clarity": 0,
            "relevance": 0,
            "completeness": 0,
            "avg_wpm": None,
            "total_fillers": 0,
            "avg_word_count": 0,
            "total_words": 0,
            "questions_answered": 0,
            "total_questions": 0,
            "strengths": [],
            "weaknesses": [],
            "recommendations": [],
            "communication_feedback": "Complete questions to receive communication feedback.",
            "content_feedback": "Complete questions to receive technical and content feedback.",
        }

    def avg(key):
        values = [a.get(key) or 0 for a in answer_results]
        return round(sum(values) / len(values)) if values else 0

    total_q = len(answer_results)
    answered_q = sum(1 for a in answer_results if not a.get("skipped", False) and (a.get("word_count") or 0) > 0)
    total_words = sum(a.get("word_count") or 0 for a in answer_results)
    overall_score = avg("overall")
    perf_category = get_performance_category(overall_score)

    wpms = [a["wpm"] for a in answer_results if a.get("wpm")]
    strengths = []
    weaknesses = []
    recs = []
    comm_notes = []
    content_notes = []

    for item in answer_results:
        strengths.extend(item.get("strengths") or [])
        weaknesses.extend(item.get("weaknesses") or [])
        recs.extend(item.get("suggestions") or [])
        if item.get("communication_feedback"):
            comm_notes.append(item.get("communication_feedback"))
        if item.get("content_feedback"):
            content_notes.append(item.get("content_feedback"))

    def unique_keep(items, limit):
        seen = []
        for item in items:
            if item and item not in seen:
                seen.append(item)
            if len(seen) >= limit:
                break
        return seen

    return {
        "overall_score": overall_score,
        "performance_category": perf_category,
        "communication": avg("communication"),
        "clarity": avg("clarity"),
        "relevance": avg("relevance"),
        "completeness": avg("completeness"),
        "avg_wpm": round(sum(wpms) / len(wpms), 1) if wpms else None,
        "total_fillers": sum(a.get("filler_total") or 0 for a in answer_results),
        "avg_word_count": round(total_words / max(answered_q, 1)),
        "total_words": total_words,
        "questions_answered": answered_q,
        "total_questions": total_q,
        "strengths": unique_keep(strengths, 4),
        "weaknesses": unique_keep(weaknesses, 4),
        "recommendations": unique_keep(recs, 3),
        "communication_feedback": comm_notes[0] if comm_notes else "Pacing and delivery tracked across questions.",
        "content_feedback": content_notes[0] if content_notes else "Topical and keyword coverage analyzed.",
    }


def readiness_score(interviews):
    """Simple readiness: average of last up to 5 overall scores, or 0 if none."""
    if not interviews:
        return 0
    recent = interviews[:5]
    return round(sum(i.get("overall_score") or 0 for i in recent) / len(recent))
