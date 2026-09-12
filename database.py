"""
MongoDB access with a clear demo fallback.

If MONGO_URI is missing or Atlas cannot be reached, the app stores
users and interviews in memory so the presentation still works.
"""

import os
import uuid
from datetime import datetime
from copy import deepcopy

from dotenv import load_dotenv

load_dotenv()

MONGO_URI = os.getenv("MONGO_URI", "").strip()

# --- Demo / in-memory fallback store (NOT used when MongoDB is healthy) ---
_demo_users = {}
_demo_interviews = {}

mongo_client = None
mongo_db = None
USE_DEMO_DB = True
DB_STATUS = "Demo mode: MongoDB is not connected. Data is stored in memory and will reset when the server restarts."


def _connect_mongo():
    global mongo_client, mongo_db, USE_DEMO_DB, DB_STATUS
    if not MONGO_URI:
        USE_DEMO_DB = True
        DB_STATUS = "Demo mode: MONGO_URI is empty. Using in-memory storage."
        return

    try:
        from pymongo import MongoClient
        from pymongo.errors import PyMongoError

        mongo_client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=4000)
        mongo_client.admin.command("ping")
        mongo_db = mongo_client.get_default_database()
        if mongo_db is None or mongo_db.name in ("", "admin", "local"):
            mongo_db = mongo_client["interviewiq"]
        mongo_db.users.create_index("email", unique=True)
        USE_DEMO_DB = False
        DB_STATUS = "MongoDB Atlas connected."
    except Exception as exc:
        USE_DEMO_DB = True
        DB_STATUS = f"Demo mode: could not connect to MongoDB ({exc}). Using in-memory storage."


_connect_mongo()


def is_demo_mode():
    return USE_DEMO_DB


def db_status_message():
    return DB_STATUS


def _now():
    return datetime.utcnow()


# -------------------- Users --------------------

def find_user_by_email(email):
    email = (email or "").strip().lower()
    if USE_DEMO_DB:
        return deepcopy(_demo_users.get(email))
    user = mongo_db.users.find_one({"email": email})
    return _serialize_user(user)


def find_user_by_id(user_id):
    if not user_id:
        return None
    if USE_DEMO_DB:
        for user in _demo_users.values():
            if user["id"] == user_id:
                return deepcopy(user)
        return None
    from bson import ObjectId
    from bson.errors import InvalidId

    try:
        user = mongo_db.users.find_one({"_id": ObjectId(user_id)})
    except (InvalidId, TypeError):
        user = mongo_db.users.find_one({"_id": user_id})
    return _serialize_user(user)


def create_user(name, email, password_hash):
    email = email.strip().lower()
    if find_user_by_email(email):
        return None, "An account with this email already exists."

    if USE_DEMO_DB:
        user = {
            "id": str(uuid.uuid4()),
            "name": name.strip(),
            "email": email,
            "password_hash": password_hash,
            "created_at": _now().isoformat(),
        }
        _demo_users[email] = user
        return deepcopy(user), None

    doc = {
        "name": name.strip(),
        "email": email,
        "password_hash": password_hash,
        "created_at": _now(),
    }
    try:
        result = mongo_db.users.insert_one(doc)
    except Exception as exc:
        if "duplicate" in str(exc).lower():
            return None, "An account with this email already exists."
        return None, "Could not create the account. Please try again."
    doc["id"] = str(result.inserted_id)
    return _serialize_user(doc), None


def update_user_name(user_id, name):
    name = name.strip()
    if USE_DEMO_DB:
        for user in _demo_users.values():
            if user["id"] == user_id:
                user["name"] = name
                return deepcopy(user)
        return None

    from bson import ObjectId
    from bson.errors import InvalidId

    try:
        oid = ObjectId(user_id)
        mongo_db.users.update_one({"_id": oid}, {"$set": {"name": name}})
        return find_user_by_id(user_id)
    except InvalidId:
        return None


def _serialize_user(user):
    if not user:
        return None
    created = user.get("created_at")
    if hasattr(created, "isoformat"):
        created = created.isoformat()
    return {
        "id": str(user.get("id") or user.get("_id")),
        "name": user.get("name"),
        "email": user.get("email"),
        "password_hash": user.get("password_hash"),
        "created_at": created,
    }


# -------------------- Interviews --------------------

def save_interview(interview):
    """Save a completed interview. Returns the interview id."""
    payload = deepcopy(interview)
    payload["created_at"] = payload.get("created_at") or _now().isoformat()

    if USE_DEMO_DB:
        interview_id = payload.get("id") or str(uuid.uuid4())
        payload["id"] = interview_id
        _demo_interviews[interview_id] = payload
        return interview_id

    from bson import ObjectId

    doc = deepcopy(payload)
    doc.pop("id", None)
    if "created_at" in doc and isinstance(doc["created_at"], str):
        try:
            doc["created_at"] = datetime.fromisoformat(doc["created_at"])
        except ValueError:
            doc["created_at"] = _now()
    if doc.get("user_id"):
        try:
            doc["user_id"] = ObjectId(doc["user_id"])
        except Exception:
            pass
    result = mongo_db.interviews.insert_one(doc)
    return str(result.inserted_id)


def get_interview(interview_id, user_id):
    if not interview_id:
        return None
    if USE_DEMO_DB:
        item = _demo_interviews.get(interview_id)
        if item and item.get("user_id") == user_id:
            return deepcopy(item)
        return None

    from bson import ObjectId
    from bson.errors import InvalidId

    query = {"_id": interview_id}
    try:
        query = {"_id": ObjectId(interview_id)}
    except (InvalidId, TypeError):
        pass

    item = mongo_db.interviews.find_one(query)
    serialized = _serialize_interview(item)
    if not serialized:
        return None
    if str(serialized.get("user_id")) != str(user_id):
        return None
    return serialized


def list_interviews(user_id, interview_type=None, difficulty=None, sort="newest"):
    if USE_DEMO_DB:
        items = [deepcopy(i) for i in _demo_interviews.values() if i.get("user_id") == user_id]
    else:
        from bson import ObjectId
        from bson.errors import InvalidId

        query = {"user_id": user_id}
        try:
            query = {"$or": [{"user_id": ObjectId(user_id)}, {"user_id": user_id}]}
        except (InvalidId, TypeError):
            query = {"user_id": user_id}
        items = [_serialize_interview(i) for i in mongo_db.interviews.find(query)]

    if interview_type:
        items = [i for i in items if i.get("type") == interview_type]
    if difficulty:
        items = [i for i in items if i.get("difficulty") == difficulty]

    reverse = True
    key = lambda i: i.get("created_at") or ""
    if sort == "oldest":
        reverse = False
    elif sort == "highest":
        key = lambda i: i.get("overall_score") or 0
        reverse = True
    elif sort == "lowest":
        key = lambda i: i.get("overall_score") or 0
        reverse = False

    items.sort(key=key, reverse=reverse)
    return items


def _serialize_interview(item):
    if not item:
        return None
    created = item.get("created_at")
    if hasattr(created, "isoformat"):
        created = created.isoformat()
    user_id = item.get("user_id")
    return {
        "id": str(item.get("id") or item.get("_id")),
        "user_id": str(user_id) if user_id is not None else None,
        "type": item.get("type"),
        "difficulty": item.get("difficulty"),
        "job_role": item.get("job_role"),
        "questions": item.get("questions") or [],
        "answers": item.get("answers") or [],
        "scores": item.get("scores") or {},
        "overall_score": item.get("overall_score") or 0,
        "performance_category": item.get("performance_category") or (item.get("summary") or {}).get("performance_category") or "Completed",
        "created_at": created,
        "ai_available": item.get("ai_available", False),
        "summary": item.get("summary") or {},
    }
