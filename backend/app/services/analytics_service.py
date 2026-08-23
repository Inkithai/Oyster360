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
from app.services.analytics_calculations import (
    BASE_YIELD_KG_PER_BAG,
    DEFAULT_BAG_COUNT,
    ENVIRONMENT_LOOKBACK_DAYS,
    MODEL_VERSION,
    confidence_score as _confidence_score,
    days_to_harvest as _days_to_harvest,
    environmental_factor as _environmental_factor,
    performance_row as _performance_row,
)
from app.services.cache_service import cache


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

        Tenant-scoped query wrapper; the penalty math lives in
        ``analytics_calculations.environmental_factor`` so it stays
        unit-testable without a database.
        """
        logs = (
            self.db.query(EnvironmentLog)
            .filter(EnvironmentLog.organization_id == organization_id)
            .order_by(EnvironmentLog.recorded_at.desc())
            .limit(ENVIRONMENT_LOOKBACK_DAYS)
            .all()
        )
        temperatures = [log.temperature for log in logs]
        humidities = [log.humidity for log in logs]
        return _environmental_factor(temperatures, humidities)

    def _confidence_score(
        self, historical_batch_count: int, has_environment_data: bool
    ) -> float:
        """Confidence grows with the amount of real tenant data behind the estimate."""
        return _confidence_score(historical_batch_count, has_environment_data)

    def _days_to_harvest(self, batch: Batch, strain: Strain) -> int:
        return _days_to_harvest(batch, strain)

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
        """Average harvested kg and completion rate for one group of batches.

        Delegates to ``analytics_calculations.performance_row``.
        """
        return _performance_row(name, batches, harvest_totals)
