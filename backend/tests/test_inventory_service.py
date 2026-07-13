"""Tests for InventoryService stock movements and tenant scoping."""
import pytest
from fastapi import HTTPException

from app.models.inventory import ItemCategory, TransactionType
from app.services.inventory_service import InventoryService


def test_create_item_defaults_to_zero_stock(db_session):
    svc = InventoryService(db_session, organization_id=1)
    item = svc.create_item("Spawn", ItemCategory.SPAWN, "kg", reorder_level=5)
    assert item.current_stock == 0
    assert item.organization_id == 1


def test_in_transaction_increases_stock(db_session):
    svc = InventoryService(db_session, 1)
    item = svc.create_item("Spawn", ItemCategory.SPAWN, "kg", 5)
    tx = svc.record_transaction(item.id, TransactionType.IN, 10, "restock", user_id=1)
    db_session.refresh(item)
    assert tx.quantity == 10
    assert item.current_stock == 10


def test_out_transaction_decreases_stock(db_session):
    svc = InventoryService(db_session, 1)
    item = svc.create_item("Spawn", ItemCategory.SPAWN, "kg", 5)
    svc.record_transaction(item.id, TransactionType.IN, 10, "in", 1)
    svc.record_transaction(item.id, TransactionType.OUT, 4, "out", 1)
    db_session.refresh(item)
    assert item.current_stock == 6


def test_out_rejects_insufficient_stock(db_session):
    svc = InventoryService(db_session, 1)
    item = svc.create_item("Spawn", ItemCategory.SPAWN, "kg", 5)
    with pytest.raises(HTTPException) as exc:
        svc.record_transaction(item.id, TransactionType.OUT, 100, "x", 1)
    assert exc.value.status_code == 400


def test_transaction_rejects_nonpositive_quantity(db_session):
    svc = InventoryService(db_session, 1)
    item = svc.create_item("Spawn", ItemCategory.SPAWN, "kg", 5)
    with pytest.raises(HTTPException) as exc:
        svc.record_transaction(item.id, TransactionType.IN, 0, "x", 1)
    assert exc.value.status_code == 400


def test_transaction_unknown_item_404(db_session):
    svc = InventoryService(db_session, 1)
    with pytest.raises(HTTPException) as exc:
        svc.record_transaction(9999, TransactionType.IN, 1, "x", 1)
    assert exc.value.status_code == 404


def test_low_stock_detection(db_session):
    svc = InventoryService(db_session, 1)
    low = svc.create_item("Low", ItemCategory.SPAWN, "kg", reorder_level=10)
    svc.record_transaction(low.id, TransactionType.IN, 5, "in", 1)  # 5 <= 10
    high = svc.create_item("High", ItemCategory.SUBSTRATE, "kg", reorder_level=2)
    svc.record_transaction(high.id, TransactionType.IN, 20, "in", 1)  # 20 > 2
    low_ids = {i.id for i in svc.get_low_stock_items()}
    assert low.id in low_ids
    assert high.id not in low_ids


def test_service_is_tenant_scoped(db_session):
    svc_a = InventoryService(db_session, 1)
    svc_b = InventoryService(db_session, 2)
    svc_a.create_item("A-item", ItemCategory.SPAWN, "kg", 1)
    svc_b.create_item("B-item", ItemCategory.SPAWN, "kg", 1)
    assert {i.name for i in svc_a.get_all_items()} == {"A-item"}
    assert {i.name for i in svc_b.get_all_items()} == {"B-item"}
