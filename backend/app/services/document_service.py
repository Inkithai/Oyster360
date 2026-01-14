from sqlalchemy.orm import Session
from app.models.document import KnowledgeDocument, DocumentChunk
from datetime import datetime
from typing import List

class DocumentService:
    def __init__(self, db: Session):
        self.db = db

    def upload_document(self, filename: str, doc_type: str, user_id: int) -> KnowledgeDocument:
        doc = KnowledgeDocument(
            filename=filename,
            document_type=doc_type,
            uploaded_by=user_id,
            uploaded_at=datetime.utcnow(),
            processing_status="pending"
        )
        self.db.add(doc)
        self.db.commit()
        self.db.refresh(doc)
        return doc

    def get_all_documents(self) -> List[KnowledgeDocument]:
        return self.db.query(KnowledgeDocument).order_by(KnowledgeDocument.uploaded_at.desc()).all()

    def update_processing_status(self, doc_id: int, status: str, chunk_count: int = 0):
        doc = self.db.query(KnowledgeDocument).filter(KnowledgeDocument.id == doc_id).first()
        if doc:
            doc.processing_status = status
            doc.chunk_count = chunk_count
            self.db.commit()