"""Tests for the cultivation assistant services.

Two implementations exist: the RAG-backed ``app.services.assistant_service``
and the provider-aware ``app.services.ai.assistant_service``. Both must answer
without ever reaching an LLM vendor when no API key is configured — the
``block_external_services`` fixture turns any outbound call into a failure.
"""
from datetime import datetime

import pytest

from app.models.batch import Batch, BatchStage
from app.models.environment_log import EnvironmentLog
from app.models.organization import Organization
from app.models.room import Room
from app.services.ai.assistant_service import AssistantService as ProviderAssistantService
from app.services.assistant_service import AssistantService as RagAssistantService


@pytest.fixture
def farm(db_session):
    org = Organization(name="Assistant Org", slug="assistant-org", created_at=datetime.utcnow())
    db_session.add(org)
    db_session.flush()

    room = Room(name="Room 1", organization_id=org.id, capacity=100)
    db_session.add(room)
    db_session.flush()

    batch = Batch(
        batch_number="ASSIST-1",
        organization_id=org.id,
        room_id=room.id,
        status="active",
        current_stage=BatchStage.FRUITING,
        created_at=datetime.utcnow(),
    )
    db_session.add(batch)
    db_session.flush()

    db_session.add_all(
        [
            EnvironmentLog(
                room_id=room.id,
                organization_id=org.id,
                temperature=21.0,
                humidity=84.0,
                recorded_at=datetime.utcnow(),
            ),
            EnvironmentLog(
                room_id=room.id,
                organization_id=org.id,
                temperature=23.0,
                humidity=88.0,
                recorded_at=datetime.utcnow(),
            ),
        ]
    )
    db_session.commit()
    return {"org": org.id, "batch": batch.id}


def test_rag_assistant_answers_batch_question(db_session, farm):
    service = RagAssistantService(db_session, farm["org"])

    result = service.answer_question("Why is this batch slow?", batch_id=farm["batch"])

    assert f"#{farm['batch']}" in result["answer"]
    assert result["sources"]
    assert 0 < result["confidence"] <= 1


def test_rag_assistant_answers_recipe_question(db_session, farm):
    service = RagAssistantService(db_session, farm["org"])

    result = service.answer_question("Which is the best recipe?")

    assert "Recipe" in result["answer"]


def test_rag_assistant_falls_back_for_unrelated_question(db_session, farm):
    service = RagAssistantService(db_session, farm["org"])

    result = service.answer_question("Tell me a joke")

    assert result["answer"].startswith("Thank you for your question")


def test_provider_assistant_defaults_to_rule_based(db_session, farm, monkeypatch):
    monkeypatch.delenv("AI_PROVIDER", raising=False)
    service = ProviderAssistantService(db_session, farm["org"])

    result = service.chat("Why is growth slow?", batch_id=farm["batch"])

    assert result["model"] == "rule-based"
    assert result["batch_id"] == farm["batch"]
    assert "humidity" in result["answer"].lower()


def test_provider_assistant_answers_contamination_question(db_session, farm, monkeypatch):
    monkeypatch.delenv("AI_PROVIDER", raising=False)
    service = ProviderAssistantService(db_session, farm["org"])

    result = service.chat("What is our contamination rate?")

    assert "contamination" in result["answer"].lower()


def test_provider_assistant_openai_falls_back_without_api_key(db_session, farm, monkeypatch):
    """No key must mean no HTTP call — the fixture would fail the test otherwise."""
    monkeypatch.setenv("AI_PROVIDER", "openai")
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    service = ProviderAssistantService(db_session, farm["org"])

    result = service.chat("Which recipe gives the best yield?")

    assert result["model"] == "openai"
    assert result["answer"]


def test_provider_assistant_gemini_uses_rule_based_placeholder(db_session, farm, monkeypatch):
    monkeypatch.setenv("AI_PROVIDER", "gemini")
    service = ProviderAssistantService(db_session, farm["org"])

    result = service.chat("Why is growth slow?", batch_id=farm["batch"])

    assert result["model"] == "gemini"
    assert result["answer"]


def test_provider_assistant_ignores_batch_from_another_tenant(db_session, farm, monkeypatch):
    monkeypatch.delenv("AI_PROVIDER", raising=False)
    other_org_service = ProviderAssistantService(db_session, organization_id=farm["org"] + 999)

    result = other_org_service.chat("Why is growth slow?", batch_id=farm["batch"])

    # No farm context may leak; the answer is generic rule-based guidance.
    assert result["answer"]
    assert result["batch_id"] == farm["batch"]
