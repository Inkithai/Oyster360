"""Tests for strains and Sri Lanka DOA cultivation guide API endpoints."""
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


def test_get_doa_varieties_and_cultivation_guide(client):
    varieties_res = client.get("/api/strains/doa-varieties")
    assert varieties_res.status_code == 200
    varieties = varieties_res.json()
    assert any("American Oyster" in v["name"] for v in varieties)
    assert any("Abalone" in v["name"] for v in varieties)
    assert any("Pink Oyster" in v["name"] for v in varieties)

    guide_res = client.get("/api/strains/cultivation-guide")
    assert guide_res.status_code == 200
    guide = guide_res.json()
    assert "Department of Agriculture" in guide["source"]
    assert len(guide["stage_checklists"]) == 5
