"""Tests for the rule-based YieldPredictionService."""
from app.models.batch import Batch
from app.models.yield_prediction import YieldPrediction
from app.services.yield_prediction_service import YieldPredictionService


def test_predict_unknown_batch_returns_error(db_session):
    result = YieldPredictionService(db_session).predict(99999)
    assert result == {"error": "Batch not found"}


def test_predict_returns_metrics_and_persists(db_session):
    batch = Batch(batch_number="YP-1", organization_id=1)
    db_session.add(batch)
    db_session.commit()
    db_session.refresh(batch)

    result = YieldPredictionService(db_session).predict(batch.id)
    assert result["batch_id"] == batch.id
    assert result["predicted_yield_kg"] > 0
    assert 0 <= result["confidence_score"] <= 100
    assert result["model_version"] == "v1.2-rule-based"

    stored = db_session.query(YieldPrediction).filter(YieldPrediction.batch_id == batch.id).one()
    assert stored.predicted_yield_kg == result["predicted_yield_kg"]
