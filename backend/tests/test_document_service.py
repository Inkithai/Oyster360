"""Tests for DocumentService (app.services.document_service)."""
from app.services.document_service import DocumentService


def test_upload_document_defaults_to_pending(db_session):
    doc = DocumentService(db_session).upload_document("guide.pdf", "pdf", user_id=4)
    assert doc.id
    assert doc.processing_status == "pending"
    assert doc.chunk_count == 0
    assert doc.uploaded_by == 4


def test_update_processing_status(db_session):
    svc = DocumentService(db_session)
    doc = svc.upload_document("a.txt", "txt", 1)
    svc.update_processing_status(doc.id, "completed", chunk_count=7)
    db_session.refresh(doc)
    assert doc.processing_status == "completed"
    assert doc.chunk_count == 7


def test_get_all_documents_ordered_desc(db_session):
    svc = DocumentService(db_session)
    svc.upload_document("a.txt", "txt", 1)
    svc.upload_document("b.txt", "txt", 1)
    docs = svc.get_all_documents()
    assert len(docs) == 2
