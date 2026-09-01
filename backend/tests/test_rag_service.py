"""Tests for the retrieval layer of the cultivation assistant.

The RAG pipeline is deliberately dependency-free (no embeddings provider, no
network) so these tests run in a fully offline environment.
"""
from datetime import datetime

import pytest

from app.models.document import DocumentChunk, KnowledgeDocument
from app.models.user import User
from app.core.security import get_password_hash
from app.services.rag_service import RAGService


@pytest.fixture
def users(db_session):
    owner = User(
        name="Owner",
        email="rag-owner@test.com",
        password_hash=get_password_hash("pass123"),
        role="ADMIN",
    )
    other = User(
        name="Other",
        email="rag-other@test.com",
        password_hash=get_password_hash("pass123"),
        role="ADMIN",
    )
    db_session.add_all([owner, other])
    db_session.commit()
    return owner, other


def _add_document(db, user_id: int, filename: str, chunks: list[str]) -> KnowledgeDocument:
    document = KnowledgeDocument(
        filename=filename,
        document_type="txt",
        uploaded_by=user_id,
        uploaded_at=datetime.utcnow(),
        processing_status="completed",
        chunk_count=len(chunks),
    )
    db.add(document)
    db.flush()
    for index, content in enumerate(chunks):
        db.add(DocumentChunk(document_id=document.id, content=content, chunk_index=index))
    db.commit()
    return document


def test_chunk_text_splits_with_overlap(db_session):
    service = RAGService(db_session)
    words = [f"w{i}" for i in range(25)]

    chunks = service.chunk_text(" ".join(words), chunk_size=10, overlap=2)

    assert len(chunks) == 4
    assert chunks[0].split()[0] == "w0"
    # The overlap means chunk N+1 restarts before chunk N ended.
    assert chunks[1].split()[0] == "w8"
    assert chunks[-1].split()[-1] == "w24"


def test_chunk_text_returns_empty_list_for_blank_input(db_session):
    assert RAGService(db_session).chunk_text("   ") == []


def test_chunk_text_rejects_overlap_greater_or_equal_to_chunk_size(db_session):
    """An overlap >= chunk size would loop forever or raise a bare ValueError."""
    service = RAGService(db_session)

    with pytest.raises(ValueError):
        service.chunk_text("some text here", chunk_size=5, overlap=5)


def test_store_document_chunks_persists_indexes(db_session, users):
    owner, _ = users
    document = _add_document(db_session, owner.id, "guide.txt", [])
    service = RAGService(db_session)

    service.store_document_chunks(document.id, ["first chunk", "second chunk"])

    stored = (
        db_session.query(DocumentChunk)
        .filter(DocumentChunk.document_id == document.id)
        .order_by(DocumentChunk.chunk_index)
        .all()
    )
    assert [c.chunk_index for c in stored] == [0, 1]
    assert [c.content for c in stored] == ["first chunk", "second chunk"]


def test_retrieve_relevant_chunks_ranks_by_term_overlap(db_session, users):
    owner, _ = users
    _add_document(
        db_session,
        owner.id,
        "cultivation.txt",
        [
            "humidity control keeps oyster mushroom pins healthy",
            "sterilise the substrate before inoculation",
            "humidity and temperature logs should be reviewed weekly",
        ],
    )
    service = RAGService(db_session)

    chunks = service.retrieve_relevant_chunks("humidity temperature", owner.id)

    assert chunks
    assert "humidity and temperature" in chunks[0]


def test_retrieve_relevant_chunks_skips_unrelated_documents(db_session, users):
    owner, _ = users
    _add_document(db_session, owner.id, "cultivation.txt", ["substrate sterilisation notes"])
    service = RAGService(db_session)

    assert service.retrieve_relevant_chunks("payroll invoices", owner.id) == []


def test_retrieve_relevant_chunks_does_not_leak_other_users_documents(db_session, users):
    owner, other = users
    _add_document(db_session, other.id, "private.txt", ["humidity secrets from another farm"])
    service = RAGService(db_session)

    assert service.retrieve_relevant_chunks("humidity", owner.id) == []


def test_retrieve_relevant_chunks_respects_top_k(db_session, users):
    owner, _ = users
    _add_document(
        db_session,
        owner.id,
        "many.txt",
        [f"humidity note number {i}" for i in range(10)],
    )
    service = RAGService(db_session)

    assert len(service.retrieve_relevant_chunks("humidity", owner.id, top_k=3)) == 3


def test_build_context_includes_knowledge_and_farm_data(db_session, users):
    owner, _ = users
    _add_document(db_session, owner.id, "cultivation.txt", ["humidity should stay near 90%"])
    service = RAGService(db_session)

    prompt = service.build_context("what humidity?", owner.id, farm_data="Batch A: 82% humidity")

    assert "humidity should stay near 90%" in prompt
    assert "Batch A: 82% humidity" in prompt
    assert "what humidity?" in prompt


def test_build_context_without_documents_still_produces_a_prompt(db_session, users):
    owner, _ = users
    prompt = RAGService(db_session).build_context("any question", owner.id)

    assert "KNOWLEDGE BASE" in prompt
    assert "any question" in prompt
