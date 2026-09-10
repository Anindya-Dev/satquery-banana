import time
from fastapi.testclient import TestClient
from backend.main import app

client = TestClient(app)

def test_health_endpoint():
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["liveness"] is True

def test_scenarios_endpoint():
    response = client.get("/api/v1/scenarios")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 5

def test_analyze_endpoint_vqa():
    payload = {
        "query": "Calculate mean NDVI reflectance across Kolkata canopy zones.",
        "task_type": "Visual Question Answering"
    }
    response = client.post("/api/v1/analyze", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["refusal_triggered"] is False
    assert len(data["evidence_chain"]) >= 1
    assert data["confidence"]["rating"] in ["HIGH", "MEDIUM"]

def test_analyze_endpoint_refusal():
    payload = {
        "query": "write a poem about space"
    }
    response = client.post("/api/v1/analyze", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["refusal_triggered"] is True
    assert "outside the domain" in data["refusal_reason"]

def test_job_lifecycle_submit_and_poll():
    payload = {
        "query": "Detect water body extent changes near Kolkata.",
        "task_type": "Bi-Temporal Change Detection"
    }
    submit_res = client.post("/api/v1/jobs", json=payload)
    assert submit_res.status_code == 200
    job_id = submit_res.json()["job_id"]
    
    # Poll job status
    time.sleep(0.3)
    poll_res = client.get(f"/api/v1/jobs/{job_id}")
    assert poll_res.status_code == 200
    poll_data = poll_res.json()
    assert poll_data["status"] in ["PENDING", "RUNNING", "COMPLETED"]

def test_invalid_request_schema():
    payload = {} # Missing required field 'query'
    response = client.post("/api/v1/analyze", json=payload)
    assert response.status_code == 422 # Unprocessable entity validation error
