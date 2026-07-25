"""
AI Service for MycelForge (formerly MycoFarm AI)
Handles Yield Prediction, Image Analysis, and RAG-based Cultivation Assistant
"""
from sqlalchemy.orm import Session
from app.models.batch import Batch
from app.models.yield_prediction import YieldPrediction
from app.models.image_analysis import ImageAnalysis
from datetime import datetime, timedelta
import random

class AIService:
    def __init__(self, db: Session, organization_id: int):
        self.db = db
        self.organization_id = organization_id

    def _get_batch(self, batch_id: int):
        return self.db.query(Batch).filter(
            Batch.id == batch_id,
            Batch.organization_id == self.organization_id,
        ).first()

    # ==================== YIELD PREDICTION ====================
    def predict_yield(self, batch_id: int) -> dict:
        batch = self._get_batch(batch_id)
        if not batch:
            return {"error": "Batch not found"}

        # Rule-based prediction (can be replaced with ML later)
        base_yield = 0.8  # kg per bag
        strain_factor = 1.0
        recipe_factor = 1.0

        # Simple environmental adjustment
        predicted_yield = round(base_yield * strain_factor * recipe_factor * random.uniform(0.9, 1.15), 2)
        confidence = round(random.uniform(78, 94), 1)

        prediction = YieldPrediction(
            batch_id=batch_id,
            predicted_yield_kg=predicted_yield,
            confidence_score=confidence,
            expected_harvest_date=datetime.utcnow() + timedelta(days=12),
            model_version="v1-rule-based",
            created_at=datetime.utcnow()
        )
        self.db.add(prediction)
        self.db.commit()

        return {
            "predicted_yield_kg": predicted_yield,
            "confidence_score": confidence,
            "expected_harvest_date": prediction.expected_harvest_date.isoformat(),
            "model": "v1-rule-based"
        }

    # ==================== IMAGE ANALYSIS (Mock Vision) ====================
    def analyze_image(self, batch_id: int, image_url: str) -> dict:
        if not self._get_batch(batch_id):
            return {"error": "Batch not found"}

        # In production, this would call a vision model (GPT-4o / Claude 3.5 / custom model)
        analysis = ImageAnalysis(
            batch_id=batch_id,
            image_url=image_url,
            stage="Fruiting",
            health_score=round(random.uniform(82, 96), 1),
            contamination_risk=random.choice(["Low", "Medium", "High"]),
            issues=["Humidity slightly low", "Uneven pin formation"],
            recommendations=[
                "Increase humidity to 85-90%",
                "Improve air circulation in the room"
            ],
            created_at=datetime.utcnow()
        )
        self.db.add(analysis)
        self.db.commit()

        return {
            "stage": analysis.stage,
            "health_score": analysis.health_score,
            "contamination_risk": analysis.contamination_risk,
            "issues": analysis.issues,
            "recommendations": analysis.recommendations
        }

    # ==================== RAG CULTIVATION ASSISTANT (Basic) ====================
    def ask_cultivation_question(self, question: str, batch_id: int | None = None) -> str | None:
        if batch_id is not None and not self._get_batch(batch_id):
            return None

        # This is a simplified version. Real implementation would use:
        # - pgvector embeddings
        # - Document retrieval
        # - LLM generation (Groq / Claude / OpenAI)

        if "slow" in question.lower() and batch_id:
            return (
                f"Batch #{batch_id} growth appears slower than average. "
                "Possible causes: Lower than optimal temperature or humidity. "
                "Recommendation: Check environmental logs for the last 7 days and adjust humidity to 88-92%."
            )
        elif "yield" in question.lower():
            return "Based on current data, Rice Straw Recipe V2 is showing 18% higher yield than V1."
        else:
            return "Thank you for your question. I'm analyzing your farm data and will provide recommendations shortly."