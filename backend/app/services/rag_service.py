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
        """Split text into overlapping word windows.

        Guard rails matter here: an ``overlap`` greater than or equal to
        ``chunk_size`` produces a non-positive stride, which would loop
        forever, and blank documents must yield no chunks rather than a
        single empty one.
        """
        if chunk_size <= 0:
            raise ValueError("chunk_size must be positive")
        if overlap < 0:
            raise ValueError("overlap must not be negative")
        if overlap >= chunk_size:
            raise ValueError("overlap must be smaller than chunk_size")

        words = text.split()
        if not words:
            return []
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

    def retrieve_relevant_chunks(
        self,
        query: str,
        user_id: int,
        top_k: int = 5,
    ) -> List[str]:
        """Retrieve chunks only from documents uploaded by the current user."""
        documents = self.db.query(DocumentChunk).join(
            KnowledgeDocument,
            KnowledgeDocument.id == DocumentChunk.document_id,
        ).filter(KnowledgeDocument.uploaded_by == user_id).all()
        scored_chunks = []

        query_words = self._tokenize(query)

        for chunk in documents:
            chunk_words = self._tokenize(chunk.content)
            score = len(query_words & chunk_words)
            if score > 0:
                scored_chunks.append((score, chunk.content))

        scored_chunks.sort(reverse=True)
        return [chunk for _, chunk in scored_chunks[:top_k]]

    @staticmethod
    def _tokenize(text: str) -> set:
        """Lowercase word tokens with punctuation stripped.

        Without this, a question such as "what humidity?" would never match a
        chunk containing the bare word "humidity".
        """
        return set(re.findall(r"[a-z0-9]+", text.lower()))

    def build_context(self, query: str, user_id: int, farm_data: str = "") -> str:
        """Build prompt context from documents + farm data"""
        chunks = self.retrieve_relevant_chunks(query, user_id)
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