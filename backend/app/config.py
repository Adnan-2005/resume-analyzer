import os
from pathlib import Path

from dotenv import load_dotenv

# backend/.env
BACKEND_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BACKEND_DIR / ".env")

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
MODEL = os.getenv("MODEL", "openai/gpt-oss-120b")

MAX_UPLOAD_BYTES = 5 * 1024 * 1024  # 5 MB
HISTORY_LIMIT = 10                  # past messages sent to the LLM
RAW_TEXT_LIMIT = 12000              # resume characters sent to the LLM

# resume-analyzer/frontend
FRONTEND_DIR = BACKEND_DIR.parent / "frontend"


def get_groq_api_key() -> str | None:
    load_dotenv(BACKEND_DIR / ".env")
    return os.getenv("GROQ_API_KEY")
