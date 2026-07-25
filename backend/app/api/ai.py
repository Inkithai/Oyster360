from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database.database import get_db
from app.services.ai_service import AIService
from pydantic import BaseModel
from typing import Optional

router = APIRouter()

class YieldPredictionRequest(BaseModel):
    batch_id: int

class ImageAnalysisRequest(BaseModel):
    batch_id: int
    image_url: str

class ChatRequest(BaseModel):
    question: str
    batch_id: Optional[int] = None

@router.post("/predict-yield")
def predict_yield(request: YieldPredictionRequest, db: Session = Depends(get_db)):
    service = AIService(db)
    return service.predict_yield(request.batch_id)

@router.post("/analyze-image")
def analyze_image(request: ImageAnalysisRequest, db: Session = Depends(get_db)):
    service = AIService(db)
    return service.analyze_image(request.batch_id, request.image_url)

@router.post("/chat")
def cultivation_chat(request: ChatRequest, db: Session = Depends(get_db)):
    service = AIService(db)
    answer = service.ask_cultivation_question(request.question, request.batch_id)
    return {"answer": answer}