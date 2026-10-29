from datetime import datetime, timedelta
from typing import Any, Dict, List

from sqlalchemy.orm import Session

from app.core.tenant_enforcer import TenantEnforcer
from app.models.batch import Batch, BatchStage
from app.models.inventory import InventoryItem
from app.models.strain import Strain

VALID_TRANSITIONS = {
    BatchStage.PREPARATION: [BatchStage.INOCULATION],
    BatchStage.INOCULATION: [BatchStage.COLONIZATION],
    BatchStage.COLONIZATION: [BatchStage.FRUITING],
    BatchStage.FRUITING: [BatchStage.HARVEST],
    BatchStage.HARVEST: [BatchStage.COMPLETED],
}


def update_batch_stage(
    db: Session, batch_id: int, new_stage: str, organization_id: int
) -> Batch:
    enforcer = TenantEnforcer(db, organization_id)
    batch = enforcer.safe_get(Batch, batch_id)

    current = BatchStage(batch.current_stage)
    target = BatchStage(new_stage)

    if target not in VALID_TRANSITIONS.get(current, []):
        raise ValueError(f"Invalid stage transition from {current} to {target}")

    batch.current_stage = target
    db.commit()
    db.refresh(batch)
    return batch


def create_batch(db: Session, batch_data: dict, organization_id: int) -> Batch:
    """Create batch with automatic organization assignment and expected harvest date."""
    payload = dict(batch_data)
    bags_prepared = payload.get("bags_prepared") or 500
    if payload.get("bags_inoculated") is None:
        payload["bags_inoculated"] = bags_prepared

    start_date = payload.get("start_date") or datetime.utcnow()
    payload["start_date"] = start_date

    if payload.get("expected_harvest_date") is None:
        cycle_days = 28
        strain_id = payload.get("strain_id")
        if strain_id:
            strain = db.query(Strain).filter(Strain.id == strain_id).first()
            if strain and strain.colonization_days:
                fruiting = strain.fruiting_days or 7
                cycle_days = int(strain.colonization_days) + int(fruiting)
        payload["expected_harvest_date"] = start_date + timedelta(days=cycle_days)

    enforcer = TenantEnforcer(db, organization_id)
    return enforcer.safe_create(Batch, **payload)


def update_batch_bags(
    db: Session, batch_id: int, update_data: dict, organization_id: int
) -> Batch:
    """Update grow-bag counts, contamination figures, and notes for a batch."""
    enforcer = TenantEnforcer(db, organization_id)
    batch = enforcer.safe_get(Batch, batch_id)

    for field in (
        "bags_prepared",
        "bags_inoculated",
        "bags_contaminated",
        "bags_harvested",
        "expected_harvest_date",
        "notes",
    ):
        if field in update_data and update_data[field] is not None:
            setattr(batch, field, update_data[field])

    if batch.bags_contaminated > batch.bags_prepared:
        raise ValueError("Contaminated bags cannot exceed prepared bags")

    db.commit()
    db.refresh(batch)
    return batch


def get_user_batches(db: Session, organization_id: int) -> List[Batch]:
    """Get all batches for user's organization."""
    enforcer = TenantEnforcer(db, organization_id)
    return enforcer.get_all(Batch)


def get_daily_tasks(db: Session, organization_id: int) -> List[Dict[str, Any]]:
    """Build actionable daily tasks and overdue alerts for Sri Lankan farm workers."""
    batches = (
        db.query(Batch)
        .filter(Batch.organization_id == organization_id, Batch.status == "active")
        .all()
    )
    now = datetime.utcnow()
    tasks: List[Dict[str, Any]] = []

    for batch in batches:
        stage = BatchStage(batch.current_stage)
        prepared = batch.bags_prepared or 500
        contaminated = batch.bags_contaminated or 0
        contam_pct = round((contaminated / prepared) * 100.0, 1) if prepared > 0 else 0.0

        if contam_pct >= 10.0:
            tasks.append({
                "type": "contamination_alert",
                "priority": "high",
                "batch_id": batch.id,
                "batch_number": batch.batch_number,
                "overdue": True,
                "title": (
                    f"High contamination on {batch.batch_number} "
                    f"({contaminated}/{prepared} bags, {contam_pct}%)"
                ),
                "action": "Isolate contaminated bags and inspect room humidity/airflow",
            })

        if stage in (BatchStage.FRUITING, BatchStage.HARVEST):
            is_overdue = bool(
                batch.expected_harvest_date and batch.expected_harvest_date < now
            )
            tasks.append({
                "type": "harvest_ready",
                "priority": "high" if is_overdue else "medium",
                "batch_id": batch.id,
                "batch_number": batch.batch_number,
                "overdue": is_overdue,
                "title": f"Record harvest flush for {batch.batch_number}",
                "action": "Weigh harvested mushrooms and log flush weight in kg",
            })
        elif batch.start_date and (now - batch.start_date).days >= 21 and stage in (
            BatchStage.PREPARATION,
            BatchStage.INOCULATION,
            BatchStage.COLONIZATION,
        ):
            tasks.append({
                "type": "stage_overdue",
                "priority": "medium",
                "batch_id": batch.id,
                "batch_number": batch.batch_number,
                "overdue": True,
                "title": f"{batch.batch_number} in {stage.value} for >21 days",
                "action": "Check mycelium colonization and move to fruiting room if ready",
            })

    low_stock_items = (
        db.query(InventoryItem)
        .filter(
            InventoryItem.organization_id == organization_id,
            InventoryItem.current_stock <= InventoryItem.reorder_level,
        )
        .all()
    )
    for item in low_stock_items:
        tasks.append({
            "type": "low_stock",
            "priority": "medium",
            "batch_id": None,
            "batch_number": None,
            "overdue": False,
            "title": f"Low stock: {item.name} ({item.current_stock} {item.unit} left)",
            "action": f"Reorder {item.name} (threshold: {item.reorder_level} {item.unit})",
        })

    return tasks
