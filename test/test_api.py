from fastapi.testclient import TestClient
from unittest.mock import patch
from api.app import app

client = TestClient(app)

# --- Helpers ---
valid_payload = {
    "tiempo": 5,
    "costo_hora": 100,
    "riesgo": 0.2
}


# ✅ 1. Test de salud del API
def test_health():
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json()["status"] == "ok"


# ✅ 2. Test /simulate con mock a RabbitMQ para no conectarse
@patch("api.app.publish_scenario")
def test_simulate_basic(mock_publish):
    r = client.post("/simulate", json=valid_payload)

    assert r.status_code == 200

    data = r.json()

    # Costo esperado
    assert data["costo_total"] == valid_payload["tiempo"] * valid_payload["costo_hora"]

    # publish_scenario debe haber sido llamado
    mock_publish.assert_called_once()


# ✅ 3. Test /simulate/batch
@patch("api.app.publish_scenario")
def test_simulate_batch(mock_publish):
    items = [
        {"tiempo": 2, "costo_hora": 50, "riesgo": 0},
        {"tiempo": 3, "costo_hora": 70, "riesgo": 0.1},
    ]

    r = client.post("/simulate/batch", json=items)
    assert r.status_code == 200

    data = r.json()
    assert len(data) == 2

    # Debe llamar publish 2 veces
    assert mock_publish.call_count == 2

    assert data[0]["costo_total"] == 100
    assert data[1]["costo_total"] == 210


# ✅ 4. Test GET /results (solo valida que responde)
def test_results_endpoint():
    r = client.get("/results?limit=10")
    assert r.status_code == 200
    assert isinstance(r.json(), list)


# ✅ 5. Test GET /results/finales
def test_results_finales():
    r = client.get("/results/finales?limit=5")
    assert r.status_code == 200
    assert isinstance(r.json(), list)


# ✅ 6. Test /stats
def test_stats_endpoint():
    r = client.get("/stats")
    assert r.status_code == 200
    assert isinstance(r.json(), dict)
