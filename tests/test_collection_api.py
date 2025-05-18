import sys
import os
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__) + '/..'))

import pytest
from app import create_app

COLLECTION_URL = "https://steamcommunity.com/sharedfiles/filedetails/?id=3467491972"

def test_api_collection(client):
    response = client.post(
        "/api/collection",
        json={"collection_url": COLLECTION_URL},
    )
    print("RESPONSE STATUS:", response.status_code)
    print("RESPONSE DATA:", response.data)
    assert response.status_code == 200
    data = response.get_json()
    assert "workshop_ids" in data
    assert isinstance(data["workshop_ids"], list)
    # Should be non-empty for a real collection
    assert len(data["workshop_ids"]) > 0

@pytest.fixture
def client():
    app = create_app()
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client
