"""Tenant enforcement integration tests."""

from app.models.batch import Batch


def test_batch_creation_assigns_organization(client, db_session, tenant_test_data):
    data = tenant_test_data
    response = client.post(
        "/api/batches",
        json={
            "batch_number": "TENANT-A-NEW",
            "room_id": 1,
            "strain_id": 1,
            "recipe_version_id": 1,
        },
        headers={"Authorization": f"Bearer {data['token_a']}"},
    )

    assert response.status_code == 200
    batch = db_session.query(Batch).filter(
        Batch.id == response.json()["id"]
    ).one()
    assert batch.organization_id == data["org_a"]


def test_batch_query_filters_by_organization(client, tenant_test_data):
    data = tenant_test_data
    response = client.get(
        "/api/batches",
        headers={"Authorization": f"Bearer {data['token_a']}"},
    )

    assert response.status_code == 200
    returned_ids = {batch["id"] for batch in response.json()}
    assert data["batch_a"] in returned_ids
    assert data["batch_b"] not in returned_ids
