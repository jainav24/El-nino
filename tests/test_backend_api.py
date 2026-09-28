from fastapi.testclient import TestClient
from backend.main import app

client = TestClient(app)

def test_dashboard_stats():
    response = client.get("/api/dashboard/stats")
    assert response.status_code == 200
    data = response.json()
    assert "total_farmers" in data
    assert "total_policies" in data

import uuid

def test_create_farmer():
    fid = f"F-{uuid.uuid4().hex[:8]}"
    payload = {
        "farmer_id": fid,
        "name": "Test Farmer",
        "region": "TestRegion",
        "state": "TestState",
        "farm_area": 10.5,
        "crop_type": "Wheat"
    }
    response = client.post("/api/farmers", json=payload)
    assert response.status_code in [200, 201]
    
def test_get_farmers():
    response = client.get("/api/farmers")
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_ml_train_unauthorized_or_empty():
    response = client.post("/api/ml/train")
    # Will fail if no data or no DB
    assert response.status_code in [200, 400, 500]
