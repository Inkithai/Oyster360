from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.core.dependencies import worker_access
from app.core.tenant import get_current_organization
from app.database.database import get_db
from app.models.user import User
from app.services.ai_service import AIService

router = APIRouter()


class YieldPredictionRequest(BaseModel):
    batch_id: int


class ImageAnalysisRequest(BaseModel):
    batch_id: int
    image_url: str


class ChatRequest(BaseModel):
    question: str
    batch_id: Optional[int] = None


def _service(db: Session, organization_id: int) -> AIService:
    return AIService(db, organization_id)


@router.post("/predict-yield")
def predict_yield(
    request: YieldPredictionRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(worker_access),
    organization_id: int = Depends(get_current_organization),
):
    result = _service(db, organization_id).predict_yield(request.batch_id)
    if "error" in result:
        raise HTTPException(status_code=404, detail=result["error"])
    return result


@router.post("/analyze-image")
def analyze_image(
    request: ImageAnalysisRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(worker_access),
    organization_id: int = Depends(get_current_organization),
):
    result = _service(db, organization_id).analyze_image(
        request.batch_id,
        request.image_url,
    )
    if "error" in result:
        raise HTTPException(status_code=404, detail=result["error"])
    return result


@router.post("/chat")
def cultivation_chat(
    request: ChatRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(worker_access),
    organization_id: int = Depends(get_current_organization),
):
    answer = _service(db, organization_id).ask_cultivation_question(
        request.question,
        request.batch_id,
    )
    if answer is None:
        raise HTTPException(status_code=404, detail="Batch not found")
    return {"answer": answer}
