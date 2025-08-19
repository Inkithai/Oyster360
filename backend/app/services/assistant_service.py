"""
Oyster360 AI Cultivation Assistant Service
Handles RAG + Tool calling for farm-specific questions
"""
from sqlalchemy.orm import Session
from app.services.rag_service import RAGService
from app.services.analytics_service import AnalyticsService
from typing import Dict, Any

class AssistantService:
    def __init__(self, db: Session, organization_id: int):
        self.db = db
        self.organization_id = organization_id
        self.rag = RAGService(db)
        self.analytics = AnalyticsService(db)

    def answer_question(self, question: str, batch_id: int = None, user_id: int = None) -> Dict[str, Any]:
        """
        Main entry point for the AI Assistant.
        Combines RAG retrieval + farm data + tool execution.
        """
        farm_context = ""

        # Tool: Get batch-specific data
        if batch_id:
            batch_data = self.analytics.get_dashboard_stats(self.organization_id)  # Can be expanded
            farm_context += f"\nCurrent Batch #{batch_id} context: {batch_data}"

        # Tool: Get analytics if relevant
        if any(word in question.lower() for word in ["yield", "production", "success"]):
            stats = self.analytics.get_dashboard_stats(self.organization_id)
            farm_context += f"\nFarm Statistics: {stats}"

        # Build RAG context
        prompt = self.rag.build_context(question, user_id or 0, farm_context)

        # Simulated LLM response (replace with real LLM call later)
        if "slow" in question.lower() and batch_id:
            answer = (
                f"Batch #{batch_id} is growing slower than average. "
                "Possible causes: Temperature below 22°C or humidity under 85%. "
                "Recommendation: Check environmental logs and increase humidity to 88-92%."
            )
        elif "recipe" in question.lower() and "best" in question.lower():
            answer = "Rice Straw Recipe V2 currently shows the highest average yield (820g/bag) with 93% success rate."
        else:
            answer = "Thank you for your question. I'm analyzing your farm data and documents to provide the best recommendation."

        return {
            "answer": answer,
            "sources": ["Farm Data", "Knowledge Base"],
            "confidence": 0.87
        }