"""Tests for ImageService inspection records (app.services.image_service)."""
from app.services.image_service import ImageService


def test_create_inspection_defaults_to_pending(db_session):
    inspection = ImageService(db_session).create_inspection(
        batch_id=1, room_id=2, image_url="https://cdn/x.png", user_id=5
    )
    assert inspection.id
    assert inspection.ai_status == "pending"
    assert inspection.image_url == "https://cdn/x.png"


def test_get_inspection_by_id(db_session):
    svc = ImageService(db_session)
    created = svc.create_inspection(1, 2, "https://cdn/y.png", 1)
    found = svc.get_inspection(created.id)
    assert found is not None
    assert found.id == created.id
    assert svc.get_inspection(99999) is None


def test_get_batch_inspections(db_session):
    svc = ImageService(db_session)
    svc.create_inspection(batch_id=1, room_id=1, image_url="a", user_id=1)
    svc.create_inspection(batch_id=1, room_id=1, image_url="b", user_id=1)
    svc.create_inspection(batch_id=2, room_id=1, image_url="c", user_id=1)
    assert len(svc.get_batch_inspections(1)) == 2
    assert len(svc.get_batch_inspections(2)) == 1
