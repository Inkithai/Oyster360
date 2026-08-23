"""Pure unit tests for the analytics math in analytics_calculations."""
from datetime import datetime, timedelta

from app.services import analytics_calculations as calc
from app.models.batch import Batch, BatchStage


class TestEnvironmentalFactor:
    def test_returns_neutral_factor_without_data(self):
        assert calc.environmental_factor([], []) == (1.0, False)

    def test_optimal_conditions_score_full_factor(self):
        factor, has_data = calc.environmental_factor([22.0], [89.0])
        assert factor == 1.0
        assert has_data is True

    def test_hot_and_dry_conditions_shrink_yield(self):
        factor, _ = calc.environmental_factor([30.0], [70.0])
        # 6 degrees over band * 1% + 15 %RH under band * 0.5% => 0.865
        assert factor < 1.0
        assert factor == 0.865

    def test_factor_is_clamped_to_bounded_corridor(self):
        extreme, _ = calc.environmental_factor([80.0], [10.0])
        assert extreme == calc.ENVIRONMENT_FACTOR_BOUNDS[0]

    def test_none_readings_are_ignored(self):
        factor, has_data = calc.environmental_factor([None, 22.0], [None, None])
        assert has_data is True
        assert factor == 1.0


class TestConfidenceScore:
    def test_confidence_grows_with_history(self):
        low = calc.confidence_score(0, False)
        high = calc.confidence_score(5, True)
        assert high > low

    def test_environment_data_adds_confidence(self):
        assert calc.confidence_score(2, True) > calc.confidence_score(2, False)

    def test_confidence_is_bounded(self):
        assert calc.confidence_score(0, False) == calc.MIN_CONFIDENCE
        assert calc.confidence_score(1000, True) == calc.MAX_CONFIDENCE


class TestDaysToHarvest:
    def test_uses_strain_cycle_when_metadata_present(self):
        strain = type("S", (), {"colonization_days": 14, "fruiting_days": 7})()
        batch = type("B", (), {"start_date": None})()
        assert calc.days_to_harvest(batch, strain) == 21

    def test_falls_back_to_default_cycle(self):
        assert calc.days_to_harvest(type("B", (), {"start_date": None})(), None) == (
            calc.DEFAULT_CYCLE_DAYS
        )

    def test_already_running_batch_has_fewer_days_left(self):
        strain = type("S", (), {"colonization_days": 14, "fruiting_days": 7})()
        batch = type(
            "B", (), {"start_date": datetime.utcnow() - timedelta(days=10)}
        )()
        assert calc.days_to_harvest(batch, strain) == 11

    def test_never_reports_zero_days(self):
        strain = type("S", (), {"colonization_days": 14, "fruiting_days": 7})()
        batch = type(
            "B", (), {"start_date": datetime.utcnow() - timedelta(days=90)}
        )()
        assert calc.days_to_harvest(batch, strain) == 1


class TestPerformanceRow:
    def test_aggregates_yield_and_completion(self):
        batches = [
            Batch(id=1, current_stage=BatchStage.COMPLETED),
            Batch(id=2, current_stage=BatchStage.FRUITING),
        ]
        row = calc.performance_row("Grey Oyster", batches, {1: 10.0, 2: 20.0})
        assert row == {
            "name": "Grey Oyster",
            "batches": 2,
            "avg_yield": 15.0,
            "success_rate": 50.0,
        }

    def test_unharvested_batches_do_not_zero_the_average(self):
        batches = [Batch(id=1, current_stage=BatchStage.FRUITING)]
        row = calc.performance_row("King Oyster", batches, {})
        assert row["avg_yield"] == 0.0
        assert row["success_rate"] == 0.0
