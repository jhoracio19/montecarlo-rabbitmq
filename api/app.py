import os
import json
import pika
from typing import List

from fastapi import FastAPI, HTTPException, Query, Body, Request
from fastapi.responses import HTMLResponse, StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.templating import Jinja2Templates
from dotenv import load_dotenv

from .schemas import ScenarioIn, ScenarioOut, ResultRow, FinalResult
from .db import (
    get_results,
    get_final_results,
    get_stats,
    count_results,
    count_final_results
)

load_dotenv()

app = FastAPI(title="Montecarlo API", version="1.0.0")

templates = Jinja2Templates(directory="templates")

# ------------------------
# CORS
# ------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ------------------------
# RabbitMQ Config
# ------------------------
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


# ------------------------
# ENDPOINTS
# ------------------------

@app.get("/")
def home():
    return {"status": "ok", "message": "Montecarlo API lista ✅"}


@app.get("/health")
def health():
    return {"status": "ok"}


# ✅ RESULTADOS PAGINADOS
@app.get("/results", response_model=list[ResultRow])
def list_results(limit: int = 50, offset: int = 0):
    return get_results(limit=limit, offset=offset)


@app.get("/results/count")
def results_count():
    return {"total": count_results()}


# ✅ RESULTADOS FINALES PAGINADOS
@app.get("/results/finales", response_model=list[FinalResult])
def list_final_results(limit: int = 50, offset: int = 0):
    return get_final_results(limit=limit, offset=offset)


@app.get("/results/finales/count")
def final_results_count():
    return {"total": count_final_results()}


# ✅ ESTADÍSTICAS
@app.get("/stats")
def stats():
    return get_stats()


# ✅ SIMULACIÓN
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


@app.post("/simulate/batch", response_model=List[ScenarioOut])
def simulate_batch(items: List[ScenarioIn] = Body(...)):
    outs = []
    for s in items:
        costo_total = s.tiempo * s.costo_hora
        payload = {"tiempo": s.tiempo, "costo_hora": s.costo_hora, "riesgo": s.riesgo}

        try:
            publish_scenario(payload)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"RabbitMQ error: {e}")

        outs.append({
            "tiempo": s.tiempo,
            "costo_hora": s.costo_hora,
            "riesgo": s.riesgo,
            "costo_total": costo_total
        })

    return outs


# ✅ DASHBOARD (render HTML)
@app.get("/dashboard", response_class=HTMLResponse)
def dashboard(request: Request):
    stats = get_stats()
    finales = get_final_results(limit=2000)
    return templates.TemplateResponse(
        "dashboard.html",
        {"request": request, "stats": stats, "finales": finales}
    )


# ✅ STREAMING SSE PARA TIEMPO REAL
@app.get("/stream/results")
async def stream_results():
    async def event_generator():
        import asyncio
        while True:
            recent = get_results(limit=30)
            finales = get_final_results(limit=1)

            payload = {
                "recent": recent,       # ✅ dicts OK
                "final": finales
            }

            yield f"data: {json.dumps(payload)}\n\n"
            await asyncio.sleep(1)

    return StreamingResponse(event_generator(), media_type="text/event-stream")
