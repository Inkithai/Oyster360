from sqlalchemy import Column, Integer, String, JSON, Float, ForeignKey, DateTime, Boolean
from sqlalchemy.orm import relationship
from .base import Base

class KnowledgeDocument(Base):
    __tablename__ = "knowledge_documents"

    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String, nullable=False)
    document_type = Column(String)  # pdf, txt, md, docx
    uploaded_by = Column(Integer, ForeignKey("users.id"))
    uploaded_at = Column(DateTime)
    processing_status = Column(String, default="pending")  # pending, processing, completed, failed
    chunk_count = Column(Integer, default=0)
    meta_data = Column(JSON)

    chunks = relationship("DocumentChunk", back_populates="document")


class DocumentChunk(Base):
    __tablename__ = "document_chunks"

    id = Column(Integer, primary_key=True, index=True)
    document_id = Column(Integer, ForeignKey("knowledge_documents.id"))
    content = Column(String)
    chunk_index = Column(Integer)
    embedding = Column(JSON)  # Will use pgvector later
    meta_data = Column(JSON)

    document = relationship("KnowledgeDocument", back_populates="chunks")