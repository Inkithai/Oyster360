"""Tests for batch lifecycle, grow-bag tracking, and daily tasks."""
from datetime import datetime, timedelta
import pytest
from fastapi import HTTPException

from app.models.batch import Batch, BatchStage
from app.models.inventory import InventoryItem
from app.services import batch_service


def _make_batch(db, org, number, stage=BatchStage.PREPARATION):
    batch = Batch(batch_number=number, organization_id=org, current_stage=stage)
    db.add(batch)
    db.commit()
    db.refresh(batch)
    return batch


def test_create_batch_assigns_organization_and_expected_harvest(db_session):
    batch = batch_service.create_batch(
        db_session,
        {"batch_number": "B-1", "bags_prepared": 600},
        organization_id=5,
    )
    assert batch.organization_id == 5
    assert batch.current_stage == BatchStage.PREPARATION
    assert batch.bags_prepared == 600
    assert batch.bags_inoculated == 600
    assert batch.expected_harvest_date is not None


def test_get_user_batches_is_tenant_scoped(db_session):
    batch_service.create_batch(db_session, {"batch_number": "A"}, 10)
    batch_service.create_batch(db_session, {"batch_number": "B"}, 20)
    assert len(batch_service.get_user_batches(db_session, 10)) == 1


def test_valid_stage_transition(db_session):
    batch = _make_batch(db_session, 1, "X")
    updated = batch_service.update_batch_stage(
        db_session, batch.id, BatchStage.INOCULATION.value, 1
    )
    assert updated.current_stage == BatchStage.INOCULATION.value


def test_invalid_stage_transition_raises(db_session):
    batch = _make_batch(db_session, 1, "Y")
    with pytest.raises(ValueError):
        batch_service.update_batch_stage(
            db_session, batch.id, BatchStage.HARVEST.value, 1
        )


def test_update_stage_cross_tenant_denied(db_session):
    batch = _make_batch(db_session, 1, "Z")
    with pytest.raises(HTTPException) as exc:
        batch_service.update_batch_stage(
            db_session, batch.id, BatchStage.INOCULATION.value, 99
        )
    assert exc.value.status_code == 404


def test_update_batch_bags_and_daily_tasks(db_session):
    batch = batch_service.create_batch(
        db_session,
        {
            "batch_number": "B-BAG-1",
            "bags_prepared": 500,
            "current_stage": BatchStage.FRUITING,
            "start_date": datetime.utcnow() - timedelta(days=30),
        },
        organization_id=7,
    )
    updated = batch_service.update_batch_bags(
        db_session,
        batch.id,
        {"bags_contaminated": 75, "bags_harvested": 400, "notes": "Green mold in corner"},
        organization_id=7,
    )
    assert updated.bags_contaminated == 75
    assert updated.bags_harvested == 400

    with pytest.raises(ValueError):
        batch_service.update_batch_bags(
            db_session, batch.id, {"bags_contaminated": 900}, organization_id=7
        )

    db_session.add(
        InventoryItem(
            name="Polypropylene Bags",
            category="GROW_BAG",
            unit="pcs",
            current_stock=50,
            reorder_level=200,
            organization_id=7,
        )
    )
    db_session.commit()

    tasks = batch_service.get_daily_tasks(db_session, organization_id=7)
    task_types = {t["type"] for t in tasks}
    assert "contamination_alert" in task_types
    assert "harvest_ready" in task_types
    assert "low_stock" in task_types
