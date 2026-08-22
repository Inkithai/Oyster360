"""
Analytics Service Tests

These tests pin the yield-prediction and performance metrics to values that
are *derived from seeded fixture data*: identical inputs must always produce
identical outputs, with no randomness anywhere in the pipeline.
"""
from datetime import datetime, timedelta
from types import SimpleNamespace

import pytest

from app.models.batch import Batch, BatchStage
from app.models.environment_log import EnvironmentLog
from app.models.harvest import Harvest
from app.models.organization import Organization
from app.models.strain import Strain
from app.services.analytics_service import AnalyticsService


def _hours_ago(hours: float) -> datetime:
    return datetime.utcnow() - timedelta(hours=hours)


@pytest.fixture
def analytics_farm(db_session):
    """One tenant with two strains, recorded harvests, and optimal room logs.

    Pearl batches harvested 500 kg (400 + 100 pickups) and 300 kg, so every
    Pearl average below is exactly 400.0 kg. Environment readings sit inside
    the optimal band, so the environmental factor is exactly 1.0.
    """
    org = Organization(name="Analytics Farm", slug="analytics-farm",
                       created_at=datetime.utcnow())
    db_session.add(org)
    db_session.flush()

    pearl = Strain(name="Pearl Analytic", species="Pleurotus ostreatus",
                   colonization_days=18, fruiting_days=7)
    blue = Strain(name="Blue Analytic", species="Pleurotus columbinus",
                  colonization_days=20, fruiting_days=8)
    db_session.add_all([pearl, blue])
    db_session.flush()

    started = datetime.utcnow() - timedelta(days=10)
    pearl_done = Batch(batch_number="AN-PEARL-DONE", organization_id=org.id,
                       strain_id=pearl.id, current_stage=BatchStage.COMPLETED,
                       status="completed", start_date=started)
    pearl_active = Batch(batch_number="AN-PEARL-ACTIVE", organization_id=org.id,
                         strain_id=pearl.id, current_stage=BatchStage.FRUITING,
                         status="active", start_date=started)
    blue_active = Batch(batch_number="AN-BLUE-ACTIVE", organization_id=org.id,
                        strain_id=blue.id, current_stage=BatchStage.FRUITING,
                        status="active", start_date=started)
    db_session.add_all([pearl_done, pearl_active, blue_active])
    db_session.flush()

    db_session.add_all([
        Harvest(batch_id=pearl_done.id, organization_id=org.id,
                quantity_kg=400.0, harvest_date=_hours_ago(48)),
        Harvest(batch_id=pearl_done.id, organization_id=org.id,
                quantity_kg=100.0, harvest_date=_hours_ago(47)),
        Harvest(batch_id=pearl_active.id, organization_id=org.id,
                quantity_kg=300.0, harvest_date=_hours_ago(24)),
    ])
    db_session.add_all([
        EnvironmentLog(organization_id=org.id, temperature=22.0, humidity=89.0,
                       co2=800.0, recorded_at=_hours_ago(hours))
        for hours in (1, 2, 3)
    ])
    db_session.commit()

    return SimpleNamespace(
        org=org, pearl=pearl, blue=blue,
        pearl_done=pearl_done, pearl_active=pearl_active, blue_active=blue_active,
    )


class TestPredictYieldForBatch:
    def test_uses_average_of_recorded_strain_harvests(self, db_session, analytics_farm):
        """Pearl history is 500 kg + 300 kg per batch -> average base of 400 kg."""
        result = AnalyticsService(db_session).predict_yield_for_batch(
            analytics_farm.pearl_active.id, analytics_farm.org.id
        )

        # Optimal environment keeps the factor at exactly 1.0.
        assert result["predicted_yield_kg"] == 400.0
        assert result["model_version"] == "v2-data-driven"

    def test_is_deterministic_across_calls(self, db_session, analytics_farm):
        service = AnalyticsService(db_session)
        first = service.predict_yield_for_batch(
            analytics_farm.pearl_active.id, analytics_farm.org.id
        )
        second = service.predict_yield_for_batch(
            analytics_farm.pearl_active.id, analytics_farm.org.id
        )

        assert first["predicted_yield_kg"] == second["predicted_yield_kg"]
        assert first["confidence_score"] == second["confidence_score"]

    def test_falls_back_to_bag_agronomy_without_strain_history(
        self, db_session, analytics_farm
    ):
        """Blue has no recorded harvests -> 0.75 kg/bag * 500 bags = 375 kg."""
        result = AnalyticsService(db_session).predict_yield_for_batch(
            analytics_farm.blue_active.id, analytics_farm.org.id
        )

        assert result["predicted_yield_kg"] == 375.0
        # 55 base + 0 historical batches + 5 for available environment data.
        assert result["confidence_score"] == 60.0

    def test_confidence_grows_with_harvest_history(self, db_session, analytics_farm):
        result = AnalyticsService(db_session).predict_yield_for_batch(
            analytics_farm.pearl_active.id, analytics_farm.org.id
        )

        # 55 base + 2 harvested batches * 4 + 5 for environment data.
        assert result["confidence_score"] == 68.0

    def test_suboptimal_environment_reduces_yield_predictably(
        self, db_session, analytics_farm
    ):
        """A second farm at 30 C (6 C above the band) loses 6% of its estimate."""
        org = Organization(name="Stressed Farm", slug="stressed-farm",
                           created_at=datetime.utcnow())
        db_session.add(org)
        db_session.flush()

        strain = Strain(name="Heat Pearl", species="Pleurotus ostreatus")
        db_session.add(strain)
        db_session.flush()

        batch = Batch(batch_number="AN-HOT-1", organization_id=org.id,
                      strain_id=strain.id, current_stage=BatchStage.FRUITING,
                      status="active",
                      start_date=datetime.utcnow() - timedelta(days=5))
        db_session.add(batch)
        db_session.flush()
        db_session.add(Harvest(batch_id=batch.id, organization_id=org.id,
                               quantity_kg=500.0, harvest_date=_hours_ago(12)))
        db_session.add(EnvironmentLog(organization_id=org.id, temperature=30.0,
                                      humidity=89.0, co2=900.0,
                                      recorded_at=_hours_ago(1)))
        db_session.commit()

        result = AnalyticsService(db_session).predict_yield_for_batch(
            batch.id, org.id
        )

        assert result["predicted_yield_kg"] == 470.0  # 500 kg * 0.94

    def test_expected_harvest_date_uses_strain_cycle_metadata(
        self, db_session, analytics_farm
    ):
        """Pearl cycle is 25 days and the batch started 10 days ago -> ~15 left."""
        result = AnalyticsService(db_session).predict_yield_for_batch(
            analytics_farm.pearl_active.id, analytics_farm.org.id
        )

        expected = datetime.fromisoformat(result["expected_harvest_date"])
        days_remaining = (expected - datetime.utcnow()).days
        assert 14 <= days_remaining <= 15

    def test_respects_tenant_boundaries(self, db_session, analytics_farm):
        other_org = Organization(name="Other Farm", slug="other-farm",
                                 created_at=datetime.utcnow())
        db_session.add(other_org)
        db_session.commit()

        result = AnalyticsService(db_session).predict_yield_for_batch(
            analytics_farm.pearl_active.id, other_org.id
        )

        assert result == {"error": "Batch not found"}
