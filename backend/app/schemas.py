from pydantic import BaseModel


class Experience(BaseModel):
    company: str | None = None
    role: str | None = None
    duration: str | None = None
    description: str | None = None
    skills_used: list[str] = []


class Resume(BaseModel):
    name: str | None = None
    email: str | None = None
    phone: str | None = None
    total_experience_years: float | None = None
    skills: list[str] = []
    experiences: list[Experience] = []
    education: list[str] = []
    projects: list[str] = []
    certifications: list[str] = []


class ChatRequest(BaseModel):
    session_id: str
    question: str
    mode: str = "analyze"  # "analyze" (resume coach) or "interview" (HR Q&A)
    history: list[dict] = []  # [{"role": "user"|"assistant", "content": "..."}]


class UploadResponse(BaseModel):
    session_id: str
    filename: str
    resume: Resume


class ChatResponse(BaseModel):
    answer: str
