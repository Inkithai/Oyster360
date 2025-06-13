"""Tests for batch lifecycle / stage transitions (app.services.batch_service)."""
import pytest
from fastapi import HTTPException

from app.models.batch import Batch, BatchStage
from app.services import batch_service


def _make_batch(db, org, number, stage=BatchStage.PREPARATION):
    batch = Batch(batch_number=number, organization_id=org, current_stage=stage)
    db.add(batch)
    db.commit()
    db.refresh(batch)
    return batch


def test_create_batch_assigns_organization(db_session):
    batch = batch_service.create_batch(db_session, {"batch_number": "B-1"}, organization_id=5)
    assert batch.organization_id == 5
    assert batch.current_stage == BatchStage.PREPARATION


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
