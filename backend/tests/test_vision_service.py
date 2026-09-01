"""Tests for the vision inspection pipeline.

``VisionService`` wraps whichever vision provider is configured; today it uses
a deterministic simulation, and these tests pin the persistence contract that
the real provider will have to honour.
"""
from datetime import datetime

import pytest

from app.models.image_inspection import ImageInspection, InspectionFinding
from app.services.vision_service import VisionService


@pytest.fixture
def inspection(db_session):
    record = ImageInspection(
        image_url="https://cdn.test/inspection.jpg",
        ai_status="pending",
        uploaded_at=datetime.utcnow(),
    )
    db_session.add(record)
    db_session.commit()
    db_session.refresh(record)
    return record


def test_analyze_image_marks_inspection_completed(db_session, inspection):
    result = VisionService(db_session).analyze_image(inspection.id, inspection.image_url)

    db_session.refresh(inspection)
    assert inspection.ai_status == "completed"
    assert inspection.detected_stage == result["detected_stage"]
    assert inspection.overall_health_score == result["health_score"]
    assert inspection.contamination_probability == result["contamination_probability"]


def test_analyze_image_returns_scores_in_expected_ranges(db_session, inspection):
    result = VisionService(db_session).analyze_image(inspection.id, inspection.image_url)

    assert 0 <= result["health_score"] <= 100
    assert 0 <= result["contamination_probability"] <= 100
    assert result["detected_stage"] in {
        "Colonization",
        "Early Fruiting",
        "Fruiting",
        "Harvest Ready",
    }


def test_analyze_image_persists_findings(db_session, inspection):
    result = VisionService(db_session).analyze_image(inspection.id, inspection.image_url)

    stored = (
        db_session.query(InspectionFinding)
        .filter(InspectionFinding.inspection_id == inspection.id)
        .all()
    )
    assert len(stored) == len(result["findings"])
    for finding in stored:
        assert finding.category in {"contamination", "substrate", "growth_stage"}
        assert finding.severity in {"low", "medium", "high"}
        assert finding.recommendation


def test_analyze_image_recommendations_match_findings(db_session, inspection):
    result = VisionService(db_session).analyze_image(inspection.id, inspection.image_url)

    assert result["recommendations"] == [f["recommendation"] for f in result["findings"]]


def test_analyze_image_for_missing_inspection(db_session):
    result = VisionService(db_session).analyze_image(999_999, "https://cdn.test/missing.jpg")

    assert result == {"error": "Inspection not found"}
    assert db_session.query(InspectionFinding).count() == 0


def test_repeated_analysis_appends_new_findings(db_session, inspection):
    service = VisionService(db_session)
    first = service.analyze_image(inspection.id, inspection.image_url)
    second = service.analyze_image(inspection.id, inspection.image_url)

    total = db_session.query(InspectionFinding).count()
    assert total == len(first["findings"]) + len(second["findings"])
