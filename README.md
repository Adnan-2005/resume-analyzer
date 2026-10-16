# Resume Analyzer

Upload a resume (PDF) and chat with an AI that analyzes it and suggests improvements.
Backend: FastAPI + Groq. Frontend: plain HTML/CSS/JS (ChatGPT-style UI).

## Project structure

```
resume-analyzer/
├── backend/
│   ├── app/
│   │   ├── main.py              # FastAPI app, CORS, serves the frontend
│   │   ├── config.py            # env vars and settings
│   │   ├── schemas.py           # Pydantic models (Resume, ChatRequest, ...)
│   │   ├── routers/
│   │   │   ├── resume.py        # POST /api/upload
│   │   │   └── chat.py          # POST /api/chat
│   │   └── services/
│   │       ├── pdf_service.py   # PDF -> text
│   │       ├── llm_service.py   # resume parsing + chat prompts (Groq)
│   │       └── session_store.py # in-memory sessions
│   ├── requirements.txt
│   └── .env.example
├── frontend/
│   ├── index.html
│   ├── css/style.css
│   └── js/app.js
├── .gitignore
└── README.md
```

## Run

```bash
cd backend
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt

cp .env.example .env             # then put your GROQ_API_KEY in .env
uvicorn app.main:app --reload
```

Open http://localhost:8000 — FastAPI serves the frontend, so no separate server is needed.
API docs: http://localhost:8000/docs

## How frontend and backend connect

| Step | Frontend (`js/app.js`) | Backend |
|------|------------------------|---------|
| 1 | Sends the PDF as `multipart/form-data` to `POST /api/upload` | Extracts text, parses it with the LLM, stores it, returns `session_id` + parsed resume |
| 2 | Sends `{session_id, question, mode, history}` to `POST /api/chat` | Looks up the resume by `session_id`, calls the LLM, returns `{answer}` |
| 3 | Renders the answer as Markdown | — |

## Notes

- Sessions are stored in memory and are lost on restart; swap `session_store.py` for Redis/DB to persist.
- Scanned/image-only PDFs are not supported (no OCR).
- If you serve `frontend/` separately (e.g. VS Code Live Server), the JS automatically calls `http://localhost:8000/api`.
