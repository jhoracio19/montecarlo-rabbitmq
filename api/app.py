import os
import json
import pika
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

from .schemas import ScenarioIn, ScenarioOut, ResultRow, FinalResult
from .db import get_results, get_final_results, get_stats

load_dotenv()

app = FastAPI(title="Montecarlo API", version="1.0.0")

# --- CORS ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- RabbitMQ config ---
RABBITMQ_URL = os.getenv("RABBITMQ_URL", "amqp://guest:guest@localhost:5672/")
SCENARIO_QUEUE = os.getenv("SCENARIO_QUEUE", "scenario_queue")


def publish_scenario(payload: dict):
    params = pika.URLParameters(RABBITMQ_URL)
    conn = pika.BlockingConnection(params)
    ch = conn.channel()

    ch.queue_declare(queue=SCENARIO_QUEUE, durable=True)

    ch.basic_publish(
        exchange="",
        routing_key=SCENARIO_QUEUE,
        body=json.dumps(payload),
        properties=pika.BasicProperties(delivery_mode=2),
    )

    conn.close()


# --- ENDPOINTS ---

@app.get("/")
def home():
    return {"status": "ok", "message": "Montecarlo API lista ✅"}


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/results", response_model=list[ResultRow])
def list_results(limit: int = Query(50, ge=1), offset: int = Query(0, ge=0)):
    return get_results(limit=limit, offset=offset)


@app.get("/results/finales", response_model=list[FinalResult])
def list_final_results(limit: int = Query(50, ge=1), offset: int = Query(0, ge=0)):
    return get_final_results(limit=limit, offset=offset)


@app.get("/stats")
def stats():
    return get_stats()


@app.post("/simulate", response_model=ScenarioOut)
def simulate(s: ScenarioIn):
    payload = {"tiempo": s.tiempo, "costo_hora": s.costo_hora, "riesgo": s.riesgo}
    costo_total = s.tiempo * s.costo_hora

    try:
        publish_scenario(payload)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"RabbitMQ error: {e}")

    return {
        "tiempo": s.tiempo,
        "costo_hora": s.costo_hora,
        "riesgo": s.riesgo,
        "costo_total": costo_total,
    }
