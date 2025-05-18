import pytest
from app import create_app


@pytest.fixture
def client():
    app = create_app()
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client


def test_api_collection_missing_url(client):
    resp = client.post("/api/collection", json={})
    assert resp.status_code == 400
    data = resp.get_json()
    assert "error" in data


def test_api_collection_invalid_url(client):
    resp = client.post("/api/collection", json={"collection_url": "not_a_url"})
    assert resp.status_code == 500
    data = resp.get_json()
    assert "error" in data


def test_api_export_missing_ids(client):
    resp = client.get("/api/export")
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["Mods"] == ""
    assert data["WorkshopItems"] == ""
