"""
Gemini AI feedback through the Flask backend only.

The API key stays on the server (.env). If Gemini is missing or fails,
the rest of the app continues with basic analysis.
"""

import json
import os
import re

import requests
from dotenv import load_dotenv

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "").strip()
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.0-flash").strip() or "gemini-2.0-flash"
FALLBACK_MODELS = [GEMINI_MODEL, "gemini-2.0-flash", "gemini-1.5-flash", "gemini-flash-latest"]


def gemini_configured():
    return bool(GEMINI_API_KEY)


def _extract_json(text):
    if not text:
        return None
    text = text.strip()
    if text.startswith("```"):
        text = re.sub(r"^```(?:json)?", "", text).strip()
        text = re.sub(r"```$", "", text).strip()
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        match = re.search(r"\{.*\}", text, re.DOTALL)
        if match:
            try:
                return json.loads(match.group(0))
            except json.JSONDecodeError:
                return None
    return None


def get_ai_feedback(question, answer, interview_type, difficulty):
    """
    Returns a dict. On success: {"ok": True, ...scores and comments...}
    On failure: {"ok": False, "message": "..."}
    """
    if not GEMINI_API_KEY:
        return {
            "ok": False,
            "message": "AI feedback is offline because GEMINI_API_KEY is not set. Basic analysis is shown instead.",
        }

    prompt = f"""You are an interview coach for students.
Evaluate this mock-interview answer. Return ONLY valid JSON with this exact shape:
{{
  "relevance_score": <integer 0-100>,
  "clarity_score": <integer 0-100>,
  "completeness_score": <integer 0-100>,
  "communication_score": <integer 0-100>,
  "communication_feedback": "<actionable 1-2 sentence feedback on delivery, pace, clarity, and tone>",
  "content_feedback": "<actionable 1-2 sentence feedback on technical/subject accuracy, relevance, and depth>",
  "strengths": ["...", "..."],
  "weaknesses": ["...", "..."],
  "suggestions": ["...", "..."],
  "improved_answer": "<a stronger version of the student's answer, 80-160 words>"
}}

Interview type: {interview_type}
Difficulty: {difficulty}
Question: {question}
Student answer: {answer}
"""

    models_tried = []
    last_error = "Unknown Gemini error"
    for model in FALLBACK_MODELS:
        if model in models_tried:
            continue
        models_tried.append(model)
        url = (
            f"https://generativelanguage.googleapis.com/v1beta/models/"
            f"{model}:generateContent?key={GEMINI_API_KEY}"
        )
        try:
            response = requests.post(
                url,
                json={
                    "contents": [{"parts": [{"text": prompt}]}],
                    "generationConfig": {"temperature": 0.4, "maxOutputTokens": 800},
                },
                timeout=18,
            )
            if response.status_code >= 400:
                last_error = f"Gemini HTTP {response.status_code}"
                continue
            data = response.json()
            text = (
                data.get("candidates", [{}])[0]
                .get("content", {})
                .get("parts", [{}])[0]
                .get("text", "")
            )
            parsed = _extract_json(text)
            if not parsed:
                last_error = "Gemini returned an unreadable response."
                continue
            return {
                "ok": True,
                "relevance_score": _clamp(parsed.get("relevance_score")),
                "clarity_score": _clamp(parsed.get("clarity_score")),
                "completeness_score": _clamp(parsed.get("completeness_score")),
                "communication_score": _clamp(parsed.get("communication_score")),
                "communication_feedback": str(parsed.get("communication_feedback") or "").strip(),
                "content_feedback": str(parsed.get("content_feedback") or "").strip(),
                "strengths": _as_list(parsed.get("strengths")),
                "weaknesses": _as_list(parsed.get("weaknesses")),
                "suggestions": _as_list(parsed.get("suggestions")),
                "improved_answer": str(parsed.get("improved_answer") or "").strip(),
            }
        except requests.Timeout:
            last_error = "Gemini timed out."
        except Exception as exc:
            last_error = str(exc)

    return {
        "ok": False,
        "message": f"AI feedback is temporarily unavailable ({last_error}). Basic analysis is shown instead.",
    }


def _clamp(value):
    try:
        number = int(round(float(value)))
    except (TypeError, ValueError):
        number = 60
    return max(0, min(100, number))


def _as_list(value):
    if isinstance(value, list):
        return [str(v).strip() for v in value if str(v).strip()][:4]
    if value:
        return [str(value).strip()]
    return []
