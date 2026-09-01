"""Tenant-scoped tests for :class:`AIService`.

The service currently uses rule-based/simulated inference, so no AI vendor is
contacted. ``conftest.block_external_services`` additionally fails the test if
anything tries an outbound HTTP call.
"""
from datetime import datetime

import pytest

from app.models.batch import Batch
from app.models.image_analysis import ImageAnalysis
from app.models.organization import Organization
from app.models.yield_prediction import YieldPrediction
from app.services.ai_service import AIService


@pytest.fixture
def two_org_batches(db_session):
    org_a = Organization(name="AI Org A", slug="ai-org-a", created_at=datetime.utcnow())
    org_b = Organization(name="AI Org B", slug="ai-org-b", created_at=datetime.utcnow())
    db_session.add_all([org_a, org_b])
    db_session.flush()

    batch_a = Batch(
        batch_number="AI-A",
        organization_id=org_a.id,
        status="active",
        created_at=datetime.utcnow(),
    )
    batch_b = Batch(
        batch_number="AI-B",
        organization_id=org_b.id,
        status="active",
        created_at=datetime.utcnow(),
    )
    db_session.add_all([batch_a, batch_b])
    db_session.commit()
    return {"org_a": org_a.id, "org_b": org_b.id, "batch_a": batch_a.id, "batch_b": batch_b.id}


def test_predict_yield_persists_prediction(db_session, two_org_batches):
    service = AIService(db_session, two_org_batches["org_a"])

    result = service.predict_yield(two_org_batches["batch_a"])

    assert "error" not in result
    assert result["model"] == "v1-rule-based"
    assert 0 < result["predicted_yield_kg"] < 5
    assert 0 <= result["confidence_score"] <= 100
    stored = db_session.query(YieldPrediction).all()
    assert len(stored) == 1
    assert stored[0].batch_id == two_org_batches["batch_a"]


def test_predict_yield_rejects_batch_from_another_tenant(db_session, two_org_batches):
    service = AIService(db_session, two_org_batches["org_a"])

    result = service.predict_yield(two_org_batches["batch_b"])

    assert result == {"error": "Batch not found"}
    assert db_session.query(YieldPrediction).count() == 0


def test_predict_yield_for_missing_batch(db_session, two_org_batches):
    service = AIService(db_session, two_org_batches["org_a"])
    assert service.predict_yield(999_999) == {"error": "Batch not found"}


def test_analyze_image_persists_analysis(db_session, two_org_batches):
    service = AIService(db_session, two_org_batches["org_a"])

    result = service.analyze_image(two_org_batches["batch_a"], "https://cdn.test/img.jpg")

    assert result["stage"] == "Fruiting"
    assert result["contamination_risk"] in {"Low", "Medium", "High"}
    assert result["issues"] and result["recommendations"]
    stored = db_session.query(ImageAnalysis).one()
    assert stored.image_url == "https://cdn.test/img.jpg"


def test_analyze_image_rejects_batch_from_another_tenant(db_session, two_org_batches):
    service = AIService(db_session, two_org_batches["org_a"])

    result = service.analyze_image(two_org_batches["batch_b"], "https://cdn.test/img.jpg")

    assert result == {"error": "Batch not found"}
    assert db_session.query(ImageAnalysis).count() == 0


def test_ask_cultivation_question_uses_batch_context(db_session, two_org_batches):
    service = AIService(db_session, two_org_batches["org_a"])

    answer = service.ask_cultivation_question(
        "Why is growth slow?", batch_id=two_org_batches["batch_a"]
    )

    assert answer is not None
    assert f"#{two_org_batches['batch_a']}" in answer


def test_ask_cultivation_question_about_yield_without_batch(db_session, two_org_batches):
    service = AIService(db_session, two_org_batches["org_a"])

    answer = service.ask_cultivation_question("Which recipe gives the best yield?")

    assert "yield" in answer.lower()


def test_ask_cultivation_question_falls_back_for_unknown_topics(db_session, two_org_batches):
    service = AIService(db_session, two_org_batches["org_a"])

    answer = service.ask_cultivation_question("What is the weather tomorrow?")

    assert answer.startswith("Thank you for your question")


def test_ask_cultivation_question_denies_cross_tenant_batch(db_session, two_org_batches):
    service = AIService(db_session, two_org_batches["org_a"])

    assert service.ask_cultivation_question("slow?", batch_id=two_org_batches["batch_b"]) is None
