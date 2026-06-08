from datetime import datetime, timedelta
from typing import Any, Dict, List, Tuple

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models.batch import Batch, BatchStage
from app.models.environment_log import EnvironmentLog
from app.models.harvest import Harvest
from app.models.recipe import Recipe
from app.models.strain import Strain
from app.models.yield_prediction import YieldPrediction
from app.services.cache_service import cache

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


class AnalyticsService:
    def __init__(self, db: Session):
        self.db = db
        self.cache = cache

    def _harvest_totals_by_batch(
        self, organization_id: int, strain_id: int = None
    ) -> Dict[int, float]:
        """Total harvested kg per batch, tenant-scoped and optionally strain-scoped.

        Real aggregation over the Harvest table so downstream metrics are
        derived from recorded production data instead of pseudo-random values.
        """
        query = (
            self.db.query(Harvest.batch_id, func.sum(Harvest.quantity_kg))
            .join(Batch, Harvest.batch_id == Batch.id)
            .filter(
                Batch.organization_id == organization_id,
                Harvest.quantity_kg.isnot(None),
            )
        )
        if strain_id is not None:
            query = query.filter(Batch.strain_id == strain_id)
        rows = query.group_by(Harvest.batch_id).all()
        return {batch_id: float(total or 0) for batch_id, total in rows}

    def _environmental_factor(self, organization_id: int) -> Tuple[float, bool]:
        """Score recent room conditions against the optimal oyster band.

        Returns ``(factor, has_environment_data)`` where ``factor`` shrinks by
        1% per degree Celsius and 0.5% per %RH outside the optimal range, and
        stays clamped to a bounded corridor so it can never dominate history.
        """
        logs = (
            self.db.query(EnvironmentLog)
            .filter(EnvironmentLog.organization_id == organization_id)
            .order_by(EnvironmentLog.recorded_at.desc())
            .limit(ENVIRONMENT_LOOKBACK_DAYS)
            .all()
        )
        temperatures = [log.temperature for log in logs if log.temperature is not None]
        humidities = [log.humidity for log in logs if log.humidity is not None]
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

    def _confidence_score(
        self, historical_batch_count: int, has_environment_data: bool
    ) -> float:
        """Confidence grows with the amount of real tenant data behind the estimate."""
        confidence = 55.0 + 4.0 * historical_batch_count
        confidence += 5.0 if has_environment_data else -5.0
        return round(max(MIN_CONFIDENCE, min(MAX_CONFIDENCE, confidence)), 1)

    def _days_to_harvest(self, batch: Batch, strain: Strain) -> int:
        if strain and strain.colonization_days and strain.fruiting_days:
            cycle_days = strain.colonization_days + strain.fruiting_days
        else:
            cycle_days = DEFAULT_CYCLE_DAYS
        if batch.start_date:
            elapsed_days = max((datetime.utcnow() - batch.start_date).days, 0)
            return max(1, cycle_days - elapsed_days)
        return max(1, cycle_days)

    def predict_yield_for_batch(
        self,
        batch_id: int,
        organization_id: int,
    ) -> Dict[str, Any]:
        batch = self.db.query(Batch).filter(
            Batch.id == batch_id,
            Batch.organization_id == organization_id,
        ).first()
        if not batch:
            return {"error": "Batch not found"}

        strain = self.db.query(Strain).filter(Strain.id == batch.strain_id).first()

        # Base the estimate on the tenant's own recorded production for this
        # strain; fall back to per-bag agronomy only when no history exists.
        historical_totals = self._harvest_totals_by_batch(
            organization_id, batch.strain_id
        )
        if historical_totals:
            base_yield = sum(historical_totals.values()) / len(historical_totals)
        else:
            bag_count = len(batch.grow_bags) or DEFAULT_BAG_COUNT
            base_yield = BASE_YIELD_KG_PER_BAG * bag_count

        environmental_factor, has_environment_data = self._environmental_factor(
            organization_id
        )
        predicted_yield = round(base_yield * environmental_factor, 1)
        confidence = self._confidence_score(
            len(historical_totals), has_environment_data
        )
        days_to_harvest = self._days_to_harvest(batch, strain)

        prediction = YieldPrediction(
            batch_id=batch_id,
            predicted_yield_kg=predicted_yield,
            confidence_score=confidence,
            expected_harvest_date=datetime.utcnow() + timedelta(days=days_to_harvest),
            model_version=MODEL_VERSION,
            created_at=datetime.utcnow(),
        )
        self.db.add(prediction)
        self.db.commit()
        self.db.refresh(prediction)

        return {
            "batch_id": batch_id,
            "predicted_yield_kg": predicted_yield,
            "confidence_score": confidence,
            "expected_harvest_date": prediction.expected_harvest_date.isoformat(),
            "model_version": prediction.model_version,
        }

    def get_dashboard_stats(self, organization_id: int) -> Dict[str, Any]:
        """Return cached analytics scoped to one organization."""
        cache_key = self.cache.get_dashboard_cache_key(organization_id)
        cached_data = self.cache.get(cache_key)
        if cached_data:
            return cached_data

        batches = self.db.query(Batch).filter(
            Batch.organization_id == organization_id
        )
        active_batches = batches.filter(Batch.status == "active").count()
        total_batches = batches.count()
        completed_batches = batches.filter(
            Batch.current_stage == BatchStage.COMPLETED
        ).count()

        total_production = self.db.query(func.sum(Harvest.quantity_kg)).filter(
            Harvest.organization_id == organization_id
        ).scalar() or 0
        success_rate = (
            round((completed_batches / total_batches) * 100, 1)
            if total_batches
            else 0
        )
        best_recipe = self.db.query(Recipe).filter(
            Recipe.organization_id == organization_id
        ).first()

        result = {
            "active_batches": active_batches,
            "total_production_kg": round(total_production, 1),
            "success_rate": success_rate,
            "contamination_rate": 8.5,
            "average_cultivation_days": 28,
            "best_strain": "N/A",
            "best_recipe": best_recipe.name if best_recipe else "N/A",
        }
        self.cache.set(cache_key, result, ttl=300)
        return result

    def get_environment_trends(self, organization_id: int) -> Dict[str, Any]:
        logs = self.db.query(EnvironmentLog).filter(
            EnvironmentLog.organization_id == organization_id
        ).order_by(EnvironmentLog.recorded_at.desc()).limit(30).all()

        if not logs:
            return {"temperature": [], "humidity": [], "co2": []}

        return {
            "temperature": [
                {"date": log.recorded_at.strftime("%m/%d"), "value": log.temperature}
                for log in logs
            ],
            "humidity": [
                {"date": log.recorded_at.strftime("%m/%d"), "value": log.humidity}
                for log in logs
            ],
            "co2": [
                {"date": log.recorded_at.strftime("%m/%d"), "value": log.co2}
                for log in logs
            ],
        }

    def get_strain_performance(self, organization_id: int) -> List[Dict]:
        """Per-strain metrics aggregated from real batches and harvests."""
        batches = self.db.query(Batch).filter(
            Batch.organization_id == organization_id
        ).all()
        strain_ids = {b.strain_id for b in batches if b.strain_id is not None}
        if not strain_ids:
            return []

        strains = self.db.query(Strain).filter(
            Strain.id.in_(strain_ids)
        ).order_by(Strain.name).all()
        harvest_totals = self._harvest_totals_by_batch(organization_id)

        result = []
        for strain in strains:
            strain_batches = [b for b in batches if b.strain_id == strain.id]
            result.append(
                self._performance_row(strain.name, strain_batches, harvest_totals)
            )
        return result

    def get_recipe_performance(self, organization_id: int) -> List[Dict]:
        """Per-recipe metrics aggregated from real batches and harvests."""
        recipes = self.db.query(Recipe).filter(
            Recipe.organization_id == organization_id
        ).order_by(Recipe.name).all()
        batches = self.db.query(Batch).filter(
            Batch.organization_id == organization_id
        ).all()
        harvest_totals = self._harvest_totals_by_batch(organization_id)

        result = []
        for recipe in recipes:
            version_ids = {version.id for version in recipe.versions}
            recipe_batches = [
                b for b in batches if b.recipe_version_id in version_ids
            ]
            row = self._performance_row(recipe.name, recipe_batches, harvest_totals)
            row["versions"] = len(version_ids)
            result.append(row)
        return result

    @staticmethod
    def _performance_row(
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
        completed = sum(
            1 for b in batches if b.current_stage == BatchStage.COMPLETED
        )
        success_rate = (
            round((completed / len(batches)) * 100, 1) if batches else 0.0
        )
        return {
            "name": name,
            "batches": len(batches),
            "avg_yield": avg_yield,
            "success_rate": success_rate,
        }
