from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database.database import get_db
from app.services.ai.assistant_service import AssistantService
from app.core.dependencies import worker_access
from app.models.user import User
from pydantic import BaseModel
from typing import Optional

router = APIRouter()

class ChatRequest(BaseModel):
    question: str
    batch_id: Optional[int] = None

@router.post("/chat")
def chat_with_assistant(
    request: ChatRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(worker_access)
):
    assistant = AssistantService(db)
    result = assistant.chat(
        question=request.question,
        batch_id=request.batch_id,
        user_id=current_user.id
    )
    return result