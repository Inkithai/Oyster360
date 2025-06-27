"""Tests for PurchaseService suppliers and orders (app.services.purchase_service)."""
from datetime import datetime

import pytest
from fastapi import HTTPException

from app.models.purchase import PurchaseOrderStatus
from app.services.purchase_service import PurchaseService


def test_create_supplier_is_tenant_scoped(db_session):
    svc_a = PurchaseService(db_session, 1)
    svc_b = PurchaseService(db_session, 2)
    svc_a.create_supplier("Acme", "Jane", "555", "a@x.com")
    svc_b.create_supplier("Other", "Joe", "556", "b@x.com")
    assert {s.name for s in svc_a.get_all_suppliers()} == {"Acme"}
    assert {s.name for s in svc_b.get_all_suppliers()} == {"Other"}


def test_create_purchase_order_computes_total(db_session):
    svc = PurchaseService(db_session, 1)
    supplier = svc.create_supplier("Acme", "Jane", "555", "a@x.com")
    order = svc.create_purchase_order(
        supplier.id,
        items=[
            {"name": "sawdust", "quantity": 10, "unit_price": 2.5},
            {"name": "bran", "quantity": 4, "unit_price": 1.5},
        ],
        expected_date=datetime.utcnow(),
        user_id=7,
    )
    assert order.total_amount == 10 * 2.5 + 4 * 1.5
    assert order.status == PurchaseOrderStatus.PENDING
    assert order.order_number.startswith("PO-")
    assert order.created_by == 7


def test_create_order_unknown_supplier_404(db_session):
    svc = PurchaseService(db_session, 1)
    with pytest.raises(HTTPException) as exc:
        svc.create_purchase_order(9999, [], datetime.utcnow(), 1)
    assert exc.value.status_code == 404


def test_get_all_orders_ordered_desc(db_session):
    svc = PurchaseService(db_session, 1)
    supplier = svc.create_supplier("Acme", "Jane", "555", "a@x.com")
    svc.create_purchase_order(supplier.id, [{"name": "x", "quantity": 1, "unit_price": 1}], datetime.utcnow(), 1)
    svc.create_purchase_order(supplier.id, [{"name": "y", "quantity": 2, "unit_price": 1}], datetime.utcnow(), 1)
    orders = svc.get_all_orders()
    assert len(orders) == 2
