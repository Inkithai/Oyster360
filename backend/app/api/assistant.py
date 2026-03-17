from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from sqlalchemy.orm import Session
from app.database.database import get_db
from app.services.assistant_service import AssistantService
from app.services.document_service import DocumentService
from app.core.dependencies import worker_access
from app.core.tenant import get_current_organization
from app.core.tenant_enforcer import TenantEnforcer
from app.models.batch import Batch
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
    current_user: User = Depends(worker_access),
    organization_id: int = Depends(get_current_organization),
):
    if request.batch_id is not None:
        TenantEnforcer(db, organization_id).safe_get(Batch, request.batch_id)
    assistant = AssistantService(db, organization_id)
    result = assistant.answer_question(
        question=request.question,
        batch_id=request.batch_id,
        user_id=current_user.id
    )
    return result

@router.post("/documents/upload")
async def upload_knowledge_document(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(worker_access)
):
    if not file.filename:
        raise HTTPException(status_code=400, detail="No file provided")

    doc_service = DocumentService(db)
    doc = doc_service.upload_document(
        filename=file.filename,
        doc_type=file.content_type or "txt",
        user_id=current_user.id
    )
    return {"document_id": doc.id, "status": "uploaded"}