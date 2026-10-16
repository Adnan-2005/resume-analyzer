from fastapi import APIRouter, File, HTTPException, UploadFile

from app.config import MAX_UPLOAD_BYTES
from app.schemas import UploadResponse
from app.services import llm_service, pdf_service, session_store

router = APIRouter(prefix="/api", tags=["resume"])


@router.post("/upload", response_model=UploadResponse)
async def upload_resume(file: UploadFile = File(...)):
    filename = file.filename or "resume.pdf"
    if not filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Please upload a PDF file.")

    data = await file.read()
    if len(data) > MAX_UPLOAD_BYTES:
        raise HTTPException(status_code=413, detail="File too large (max 5 MB).")

    try:
        text = pdf_service.extract_text(data)
    except Exception:
        raise HTTPException(status_code=400, detail="Could not read this PDF.")

    if not text.strip():
        raise HTTPException(
            status_code=422,
            detail="No text found in the PDF. Scanned/image resumes are not supported.",
        )

    try:
        resume = llm_service.parse_resume(text)
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Resume parsing failed: {e}")

    session_id = session_store.create_session(resume, text, filename)
    return UploadResponse(session_id=session_id, filename=filename, resume=resume)
