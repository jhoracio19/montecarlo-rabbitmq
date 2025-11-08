from fastapi.testclient import TestClient
from api.app import app

client = TestClient(app)

def test_health():
    r = client.get("/health")
    assert r.status_code == 200

def test_simulate_basic():
    r = client.post("/simulate", json={"tiempo": 2, "costo_hora": 100, "riesgo": 0})
    assert r.status_code == 200
    assert r.json()["costo_total"] == 200.0
