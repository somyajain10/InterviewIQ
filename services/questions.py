"""Question bank for InterviewIQ mock interviews."""

import random

QUESTION_BANK = {
    "HR": {
        "Beginner": [
            {"q": "Tell me about yourself.", "keywords": ["student", "skills", "project", "goal"]},
            {"q": "Why do you want this internship?", "keywords": ["learn", "company", "skill", "growth"]},
            {"q": "What are your strengths?", "keywords": ["strength", "example", "skill", "team"]},
            {"q": "What is one weakness you are working on?", "keywords": ["weakness", "improve", "learn"]},
            {"q": "How do you handle deadlines?", "keywords": ["plan", "time", "priority", "deadline"]},
            {"q": "What motivates you as a student?", "keywords": ["goal", "learn", "project", "growth"]},
            {"q": "How do you work in a team?", "keywords": ["team", "listen", "responsibility", "communicate"]},
            {"q": "Where do you see yourself in two years?", "keywords": ["goal", "learn", "career", "skill"]},
        ],
        "Intermediate": [
            {"q": "Describe a time you received feedback and how you used it.", "keywords": ["feedback", "improve", "example"]},
            {"q": "Why should we select you over other intern candidates?", "keywords": ["skill", "project", "learn", "value"]},
            {"q": "Tell me about a project you are proud of.", "keywords": ["project", "problem", "result", "team"]},
            {"q": "How do you prioritize multiple college assignments?", "keywords": ["priority", "plan", "deadline", "focus"]},
            {"q": "What do you know about working in a professional environment?", "keywords": ["communication", "responsibility", "team"]},
            {"q": "How do you stay updated with technology?", "keywords": ["learn", "course", "project", "practice"]},
            {"q": "Describe your ideal internship mentor.", "keywords": ["learn", "feedback", "guidance", "growth"]},
            {"q": "What is your approach when you do not know an answer?", "keywords": ["honest", "learn", "research", "ask"]},
        ],
        "Advanced": [
            {"q": "How would you add value in your first month as an intern?", "keywords": ["learn", "contribute", "project", "team"]},
            {"q": "Tell me about a disagreement and how you resolved it.", "keywords": ["conflict", "listen", "solution", "team"]},
            {"q": "What does ownership mean to you in a project?", "keywords": ["responsibility", "deadline", "quality", "result"]},
            {"q": "How do you measure your own growth?", "keywords": ["goal", "skill", "feedback", "improve"]},
            {"q": "Describe a failure and what you changed afterwards.", "keywords": ["failure", "learn", "improve", "result"]},
            {"q": "How would you communicate a delayed task to your manager?", "keywords": ["honest", "plan", "deadline", "communication"]},
            {"q": "What kind of company culture helps you do your best work?", "keywords": ["team", "learn", "feedback", "respect"]},
            {"q": "Why this role rather than a different internship?", "keywords": ["role", "skill", "interest", "growth"]},
        ],
    },
    "Technical": {
        "Beginner": [
            {"q": "What is the difference between a compiler and an interpreter?", "keywords": ["compiler", "interpreter", "code", "language"]},
            {"q": "Explain what a variable is in programming.", "keywords": ["variable", "data", "memory", "value"]},
            {"q": "What is an array?", "keywords": ["array", "index", "data", "element"]},
            {"q": "What is the difference between frontend and backend?", "keywords": ["frontend", "backend", "ui", "server"]},
            {"q": "What is a database used for?", "keywords": ["database", "data", "store", "query"]},
            {"q": "What is Git and why do developers use it?", "keywords": ["git", "version", "commit", "collaborate"]},
            {"q": "Explain what an API is in simple words.", "keywords": ["api", "request", "data", "service"]},
            {"q": "What is the difference between HTML, CSS, and JavaScript?", "keywords": ["html", "css", "javascript", "webpage"]},
        ],
        "Intermediate": [
            {"q": "What is time complexity and why does it matter?", "keywords": ["complexity", "algorithm", "time", "performance"]},
            {"q": "Explain the difference between SQL and NoSQL databases.", "keywords": ["sql", "nosql", "schema", "document"]},
            {"q": "How does a REST API work?", "keywords": ["rest", "http", "endpoint", "json"]},
            {"q": "What happens when you enter a URL in a browser?", "keywords": ["dns", "http", "server", "browser"]},
            {"q": "Explain stack vs queue with one example each.", "keywords": ["stack", "queue", "lifo", "fifo"]},
            {"q": "What is the difference between authentication and authorization?", "keywords": ["authentication", "authorization", "login", "permission"]},
            {"q": "How would you debug a program that crashes sometimes?", "keywords": ["debug", "log", "reproduce", "test"]},
            {"q": "What is Object-Oriented Programming?", "keywords": ["class", "object", "inheritance", "encapsulation"]},
        ],
        "Advanced": [
            {"q": "How would you design a URL shortener at a high level?", "keywords": ["hash", "database", "api", "scale"]},
            {"q": "Explain indexing in databases and when it helps.", "keywords": ["index", "query", "database", "performance"]},
            {"q": "How would you find a duplicate in a large list efficiently?", "keywords": ["hash", "set", "complexity", "algorithm"]},
            {"q": "What is the difference between process and thread?", "keywords": ["process", "thread", "memory", "parallel"]},
            {"q": "How does HTTPS protect data compared with HTTP?", "keywords": ["https", "encryption", "tls", "certificate"]},
            {"q": "Explain CAP theorem in simple terms.", "keywords": ["consistency", "availability", "partition", "database"]},
            {"q": "How would you test an API before releasing it?", "keywords": ["test", "status", "edge", "validation"]},
            {"q": "What is caching and where would you use it?", "keywords": ["cache", "speed", "memory", "database"]},
        ],
    },
    "Behavioral": {
        "Beginner": [
            {"q": "Tell me about a time you helped a classmate.", "keywords": ["help", "team", "result", "learn"]},
            {"q": "Describe a challenging assignment and how you finished it.", "keywords": ["challenge", "plan", "effort", "result"]},
            {"q": "How do you react when you make a mistake?", "keywords": ["mistake", "honest", "fix", "learn"]},
            {"q": "Tell me about a time you learned something quickly.", "keywords": ["learn", "practice", "example", "result"]},
            {"q": "Describe a situation where you had to ask for help.", "keywords": ["ask", "team", "learn", "progress"]},
            {"q": "How do you stay focused during exams or deadlines?", "keywords": ["focus", "plan", "time", "habit"]},
            {"q": "Tell me about a team project in college.", "keywords": ["team", "role", "communication", "result"]},
            {"q": "What do you do when a topic feels confusing?", "keywords": ["learn", "practice", "question", "notes"]},
        ],
        "Intermediate": [
            {"q": "Describe a conflict in a group project and what you did.", "keywords": ["conflict", "listen", "solution", "team"]},
            {"q": "Tell me about a time you took extra responsibility.", "keywords": ["ownership", "initiative", "result", "team"]},
            {"q": "Share an example of meeting a tight deadline.", "keywords": ["deadline", "priority", "plan", "result"]},
            {"q": "Describe a time you had to explain a technical idea simply.", "keywords": ["communication", "example", "clarity"]},
            {"q": "Tell me about a time you failed to meet your own standard.", "keywords": ["failure", "improve", "effort", "learn"]},
            {"q": "How have you handled unclear instructions?", "keywords": ["clarify", "ask", "plan", "communication"]},
            {"q": "Give an example of receiving critical feedback.", "keywords": ["feedback", "listen", "improve", "result"]},
            {"q": "Describe a time you adapted when a plan changed.", "keywords": ["adapt", "change", "plan", "result"]},
        ],
        "Advanced": [
            {"q": "Tell me about leading a task even if you were not the official leader.", "keywords": ["lead", "initiative", "team", "result"]},
            {"q": "Describe a high-pressure situation and your decision process.", "keywords": ["pressure", "decision", "priority", "result"]},
            {"q": "Share a time you improved a process, not just a task.", "keywords": ["improve", "process", "efficiency", "result"]},
            {"q": "Tell me about persuading teammates to try your approach.", "keywords": ["persuade", "listen", "data", "team"]},
            {"q": "Describe balancing quality and speed on a project.", "keywords": ["quality", "deadline", "tradeoff", "result"]},
            {"q": "Give an example of owning a mistake in public.", "keywords": ["honest", "responsibility", "fix", "trust"]},
            {"q": "Tell me about working with someone whose style differed from yours.", "keywords": ["difference", "respect", "adapt", "team"]},
            {"q": "Describe a goal you set and how you tracked it.", "keywords": ["goal", "track", "habit", "result"]},
        ],
    },
    "General": {
        "Beginner": [
            {"q": "Why do companies conduct interviews?", "keywords": ["skill", "fit", "communication", "role"]},
            {"q": "How do you prepare for an interview?", "keywords": ["research", "practice", "resume", "questions"]},
            {"q": "What is a resume and what should it highlight?", "keywords": ["resume", "skills", "project", "education"]},
            {"q": "How can body language affect an interview?", "keywords": ["eye", "posture", "confidence", "listen"]},
            {"q": "What is the STAR method?", "keywords": ["situation", "task", "action", "result"]},
            {"q": "Why is communication important for engineers?", "keywords": ["team", "clarity", "requirement", "client"]},
            {"q": "How would you introduce your best project in 60 seconds?", "keywords": ["project", "problem", "solution", "result"]},
            {"q": "What questions would you ask the interviewer?", "keywords": ["role", "team", "learn", "project"]},
        ],
        "Intermediate": [
            {"q": "How do you explain a gap in knowledge without sounding unprepared?", "keywords": ["honest", "learn", "example", "plan"]},
            {"q": "What makes a good intern in the first 30 days?", "keywords": ["learn", "ask", "reliable", "team"]},
            {"q": "How should you structure answers to technical questions?", "keywords": ["definition", "example", "tradeoff", "summary"]},
            {"q": "How do you show problem-solving in an interview?", "keywords": ["clarify", "approach", "tradeoff", "test"]},
            {"q": "What is the difference between confidence and arrogance?", "keywords": ["listen", "humble", "evidence", "respect"]},
            {"q": "How would you handle a question you cannot answer fully?", "keywords": ["honest", "reason", "next", "learn"]},
            {"q": "Why do interviewers ask puzzle or scenario questions?", "keywords": ["thinking", "approach", "communication", "logic"]},
            {"q": "How can you improve after a weak interview?", "keywords": ["notes", "practice", "feedback", "improve"]},
        ],
        "Advanced": [
            {"q": "How would you demonstrate business awareness as a second-year student?", "keywords": ["user", "value", "product", "impact"]},
            {"q": "Design a 2-week plan to prepare for a product-company interview.", "keywords": ["dsa", "projects", "hr", "mock"]},
            {"q": "How do you talk about teamwork without sounding generic?", "keywords": ["role", "conflict", "result", "example"]},
            {"q": "What signals show an intern is ready for real project work?", "keywords": ["ownership", "communication", "quality", "deadline"]},
            {"q": "How would you compare two internship offers?", "keywords": ["learn", "mentor", "role", "growth"]},
            {"q": "Explain a technical project to a non-technical interviewer.", "keywords": ["problem", "impact", "simple", "result"]},
            {"q": "How should you follow up after an interview?", "keywords": ["thank", "interest", "clarity", "professional"]},
            {"q": "What is one habit that most improves interview performance?", "keywords": ["practice", "feedback", "structure", "examples"]},
        ],
    },
}


DIFFICULTY_MAP = {
    "Easy": "Beginner",
    "Medium": "Intermediate",
    "Hard": "Advanced",
    "Beginner": "Beginner",
    "Intermediate": "Intermediate",
    "Advanced": "Advanced",
}


def select_questions(interview_type, difficulty, count):
    """Randomly pick questions for the chosen type and difficulty."""
    bank = QUESTION_BANK.get(interview_type, QUESTION_BANK.get("General", {}))
    
    # Normalize difficulty (Easy -> Beginner, Medium -> Intermediate, Hard -> Advanced)
    normalized_difficulty = DIFFICULTY_MAP.get(difficulty, "Beginner")
    pool = list(bank.get(normalized_difficulty, bank.get("Beginner", [])))

    # If the student asked for more questions than we store, fill from nearby difficulties.
    if len(pool) < count:
        for extra_level in ("Beginner", "Intermediate", "Advanced"):
            for item in bank.get(extra_level, []):
                if item not in pool:
                    pool.append(item)
            if len(pool) >= count:
                break

    count = max(1, min(int(count), len(pool)))
    chosen = random.sample(pool, count)
    questions = []
    for index, item in enumerate(chosen, start=1):
        questions.append({
            "index": index,
            "text": item["q"],
            "keywords": item.get("keywords") or [],
        })
    return questions

