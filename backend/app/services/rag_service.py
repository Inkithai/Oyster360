"""
RAG Service for Oyster360 AI Cultivation Assistant
Production-ready Retrieval-Augmented Generation pipeline
"""
from sqlalchemy.orm import Session
from app.models.document import KnowledgeDocument, DocumentChunk
from typing import List, Dict, Any
import re

class RAGService:
    def __init__(self, db: Session):
        self.db = db

    def chunk_text(self, text: str, chunk_size: int = 800, overlap: int = 100) -> List[str]:
        """Simple text chunking strategy"""
        words = text.split()
        chunks = []
        for i in range(0, len(words), chunk_size - overlap):
            chunk = " ".join(words[i:i + chunk_size])
            chunks.append(chunk)
        return chunks

    def store_document_chunks(self, document_id: int, chunks: List[str]):
        """Store chunks in database (embedding placeholder for now)"""
        for idx, chunk in enumerate(chunks):
            chunk_obj = DocumentChunk(
                document_id=document_id,
                content=chunk,
                chunk_index=idx,
                embedding=None  # TODO: Generate real embeddings with pgvector
            )
            self.db.add(chunk_obj)
        self.db.commit()

    def retrieve_relevant_chunks(self, query: str, top_k: int = 5) -> List[str]:
        """Simple keyword-based retrieval (replace with vector search later)"""
        documents = self.db.query(DocumentChunk).all()
        scored_chunks = []

        query_words = set(query.lower().split())

        for chunk in documents:
            chunk_words = set(chunk.content.lower().split())
            score = len(query_words & chunk_words)
            if score > 0:
                scored_chunks.append((score, chunk.content))

        scored_chunks.sort(reverse=True)
        return [chunk for _, chunk in scored_chunks[:top_k]]

    def build_context(self, query: str, farm_data: str = "") -> str:
        """Build prompt context from documents + farm data"""
        chunks = self.retrieve_relevant_chunks(query)
        context = "\n\n".join(chunks)
        
        prompt = f"""You are Oyster360, an expert AI Farm Copilot for commercial oyster mushroom cultivation.

Use the following context to answer the question. Be specific and actionable.

=== KNOWLEDGE BASE ===
{context}

=== FARM DATA ===
{farm_data}

=== QUESTION ===
{query}

Answer clearly with recommendations. If data is insufficient, say so.
"""
        return prompt