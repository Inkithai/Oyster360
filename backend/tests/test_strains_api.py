"""Tests for strains API endpoints."""
import pytest
from app.models.strain import Strain


def test_get_strains_returns_list(client, db_session):
    s1 = Strain(name="Blue Oyster", species="Pleurotus ostreatus", difficulty="EASY", colonization_days=14)
    s2 = Strain(name="King Oyster", species="Pleurotus eryngii", difficulty="MEDIUM", colonization_days=21)
    db_session.add_all([s1, s2])
    db_session.commit()

    response = client.get("/api/strains/")
    assert response.status_code == 200
    strains = response.json()
    assert len(strains) >= 2
    names = [s["name"] for s in strains]
    assert "Blue Oyster" in names
    assert "King Oyster" in names
