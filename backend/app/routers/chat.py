from fastapi import APIRouter, HTTPException

from app.schemas import ChatRequest, ChatResponse
from app.services import llm_service, session_store

router = APIRouter(prefix="/api", tags=["chat"])


@router.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest):
    session = session_store.get_session(request.session_id)
    if not session:
        raise HTTPException(
            status_code=404, detail="Session expired. Please upload your resume again."
        )

    try:
        answer = llm_service.answer_question(
            question=request.question,
            mode=request.mode,
            resume=session["resume"],
            raw_text=session["text"],
            history=request.history,
        )
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"LLM request failed: {e}")

    return ChatResponse(answer=answer)
