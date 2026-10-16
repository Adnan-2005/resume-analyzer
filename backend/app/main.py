from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.config import FRONTEND_DIR
from app.routers import chat, resume

app = FastAPI(title="Resume Analyzer")

# CORS is only needed if the frontend runs on another origin (e.g. Live Server :5500).
# When FastAPI serves the frontend itself (default), everything is same-origin.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(resume.router)
app.include_router(chat.router)


@app.get("/api/health")
def health():
    return {"status": "ok"}


# Serve the frontend at "/" — mounted LAST so /api/* routes take priority.
app.mount("/", StaticFiles(directory=FRONTEND_DIR, html=True), name="frontend")
