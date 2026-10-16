import uuid

from app.schemas import Resume

# In-memory store: session_id -> {"resume": Resume, "text": str, "filename": str}
# Lost on server restart. Swap for Redis/DB if you need persistence.
_SESSIONS: dict[str, dict] = {}


def create_session(resume: Resume, text: str, filename: str) -> str:
    session_id = uuid.uuid4().hex
    _SESSIONS[session_id] = {"resume": resume, "text": text, "filename": filename}
    return session_id


def get_session(session_id: str) -> dict | None:
    return _SESSIONS.get(session_id)
