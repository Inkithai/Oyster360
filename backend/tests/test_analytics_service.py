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
from app.models.recipe import Recipe, RecipeVersion
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


@pytest.fixture
def recipe_farm(db_session, analytics_farm):
    """Attach a two-version recipe to the analytics farm's batches.

    Version 1 feeds the completed Pearl batch (500 kg harvested) and one
    fruited-but-unharvested batch; version 2 feeds the active Pearl batch
    (300 kg harvested).
    """
    recipe = Recipe(name="Straw Bran Analytic", organization_id=analytics_farm.org.id,
                    created_at=datetime.utcnow())
    db_session.add(recipe)
    db_session.flush()

    version_one = RecipeVersion(recipe_id=recipe.id, version=1,
                                ingredients={"straw": 70, "bran": 30})
    version_two = RecipeVersion(recipe_id=recipe.id, version=2,
                                ingredients={"straw": 80, "bran": 20})
    db_session.add_all([version_one, version_two])
    db_session.flush()

    unharvested = Batch(batch_number="AN-RECIPE-OPEN",
                        organization_id=analytics_farm.org.id,
                        strain_id=analytics_farm.pearl.id,
                        recipe_version_id=version_one.id,
                        current_stage=BatchStage.COMPLETED, status="completed",
                        start_date=datetime.utcnow() - timedelta(days=30))
    db_session.add(unharvested)
    analytics_farm.pearl_done.recipe_version_id = version_one.id
    analytics_farm.pearl_active.recipe_version_id = version_two.id
    db_session.commit()

    analytics_farm.recipe = recipe
    analytics_farm.unharvested = unharvested
    return analytics_farm


class TestStrainPerformance:
    def test_metrics_come_from_recorded_batches_and_harvests(
        self, db_session, analytics_farm
    ):
        rows = AnalyticsService(db_session).get_strain_performance(
            analytics_farm.org.id
        )

        by_name = {row["name"]: row for row in rows}
        # Pearl: batches harvested 500 kg and 300 kg -> average 400.0; one of
        # the two batches has completed its cycle.
        assert by_name["Pearl Analytic"] == {
            "name": "Pearl Analytic",
            "batches": 2,
            "avg_yield": 400.0,
            "success_rate": 50.0,
        }
        # Blue: one batch, no harvests yet, still fruiting.
        assert by_name["Blue Analytic"] == {
            "name": "Blue Analytic",
            "batches": 1,
            "avg_yield": 0.0,
            "success_rate": 0.0,
        }

    def test_is_tenant_scoped(self, db_session, analytics_farm):
        other_org = Organization(name="Stranger Farm", slug="stranger-farm",
                                 created_at=datetime.utcnow())
        db_session.add(other_org)
        db_session.flush()
        other_strain = Strain(name="Stranger Strain", species="Pleurotus ostreatus")
        db_session.add(other_strain)
        db_session.flush()
        db_session.add(Batch(batch_number="STRANGER-1", organization_id=other_org.id,
                             strain_id=other_strain.id, status="active"))
        db_session.commit()

        rows = AnalyticsService(db_session).get_strain_performance(
            analytics_farm.org.id
        )

        assert {row["name"] for row in rows} == {"Pearl Analytic", "Blue Analytic"}


class TestRecipePerformance:
    def test_metrics_come_from_version_usage_and_harvests(
        self, db_session, recipe_farm
    ):
        rows = AnalyticsService(db_session).get_recipe_performance(
            recipe_farm.org.id
        )

        assert len(rows) == 1
        assert rows[0]["name"] == "Straw Bran Analytic"
        assert rows[0]["versions"] == 2
        # Three batches use the recipe; only two have harvests (500, 300).
        assert rows[0]["batches"] == 3
        assert rows[0]["avg_yield"] == 400.0
        # Two of the three batches completed.
        assert rows[0]["success_rate"] == 66.7

    def test_recipe_without_batches_reports_zero_metrics(
        self, db_session, analytics_farm
    ):
        db_session.add(Recipe(name="Unused Analytic",
                              organization_id=analytics_farm.org.id,
                              created_at=datetime.utcnow()))
        db_session.commit()

        rows = AnalyticsService(db_session).get_recipe_performance(
            analytics_farm.org.id
        )

        unused = next(r for r in rows if r["name"] == "Unused Analytic")
        assert unused["batches"] == 0
        assert unused["avg_yield"] == 0.0
        assert unused["success_rate"] == 0.0
