"""
Pure calculation helpers backing AnalyticsService.

Every function here is deterministic and database-free, which keeps the
agronomy math (yield baselines, environment penalties, confidence scoring,
performance aggregation) unit-testable in isolation. The service layer in
analytics_service.py owns the tenant-scoped queries and delegates the math.
"""
from datetime import datetime
from typing import Dict, Iterable, List, Tuple

from app.models.batch import Batch, BatchStage
from app.models.strain import Strain

# Agronomic reference values for oyster mushroom cultivation. Every constant is
# only a fallback: as soon as a tenant records its own harvests, strain
# metadata, or environment logs, those real values take over.
BASE_YIELD_KG_PER_BAG = 0.75
DEFAULT_BAG_COUNT = 500
DEFAULT_CYCLE_DAYS = 28
OPTIMAL_TEMPERATURE_C = (20.0, 24.0)
OPTIMAL_HUMIDITY_PCT = (85.0, 93.0)
TEMPERATURE_PENALTY_PER_DEGREE = 0.01
HUMIDITY_PENALTY_PER_PERCENT = 0.005
ENVIRONMENT_FACTOR_BOUNDS = (0.85, 1.15)
ENVIRONMENT_LOOKBACK_DAYS = 30
MIN_CONFIDENCE = 50.0
MAX_CONFIDENCE = 95.0
MODEL_VERSION = "v2-data-driven"


def environmental_factor(
    temperatures: Iterable[float], humidities: Iterable[float]
) -> Tuple[float, bool]:
    """Score recent room conditions against the optimal oyster band.

    Returns ``(factor, has_environment_data)`` where ``factor`` shrinks by
    1% per degree Celsius and 0.5% per %RH outside the optimal range, and
    stays clamped to a bounded corridor so it can never dominate history.
    """
    temperatures = [t for t in temperatures if t is not None]
    humidities = [h for h in humidities if h is not None]
    if not temperatures and not humidities:
        return 1.0, False

    factor = 1.0
    temp_low, temp_high = OPTIMAL_TEMPERATURE_C
    humidity_low, humidity_high = OPTIMAL_HUMIDITY_PCT
    if temperatures:
        mean_temperature = sum(temperatures) / len(temperatures)
        deviation = max(
            temp_low - mean_temperature, mean_temperature - temp_high, 0.0
        )
        factor -= TEMPERATURE_PENALTY_PER_DEGREE * deviation
    if humidities:
        mean_humidity = sum(humidities) / len(humidities)
        deviation = max(
            humidity_low - mean_humidity, mean_humidity - humidity_high, 0.0
        )
        factor -= HUMIDITY_PENALTY_PER_PERCENT * deviation

    lower, upper = ENVIRONMENT_FACTOR_BOUNDS
    return round(max(lower, min(upper, factor)), 4), True


def confidence_score(
    historical_batch_count: int, has_environment_data: bool
) -> float:
    """Confidence grows with the amount of real tenant data behind the estimate."""
    confidence = 55.0 + 4.0 * historical_batch_count
    confidence += 5.0 if has_environment_data else -5.0
    return round(max(MIN_CONFIDENCE, min(MAX_CONFIDENCE, confidence)), 1)


def days_to_harvest(batch: Batch, strain: Strain) -> int:
    """Remaining days until harvest for a batch, from strain metadata or defaults."""
    if strain and strain.colonization_days and strain.fruiting_days:
        cycle_days = strain.colonization_days + strain.fruiting_days
    else:
        cycle_days = DEFAULT_CYCLE_DAYS
    if batch.start_date:
        elapsed_days = max((datetime.utcnow() - batch.start_date).days, 0)
        return max(1, cycle_days - elapsed_days)
    return max(1, cycle_days)


def performance_row(
    name: str, batches: List[Batch], harvest_totals: Dict[int, float]
) -> Dict:
    """Average harvested kg and completion rate for one group of batches."""
    harvested_batches = [
        harvest_totals[b.id] for b in batches if b.id in harvest_totals
    ]
    avg_yield = (
        round(sum(harvested_batches) / len(harvested_batches), 1)
        if harvested_batches
        else 0.0
    )
    completed = sum(1 for b in batches if b.current_stage == BatchStage.COMPLETED)
    success_rate = round((completed / len(batches)) * 100, 1) if batches else 0.0
    return {
        "name": name,
        "batches": len(batches),
        "avg_yield": avg_yield,
        "success_rate": success_rate,
    }
