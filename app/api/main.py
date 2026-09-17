import os
import signal

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from prometheus_fastapi_instrumentator import Instrumentator

from database import get_connection
from agent.agent import investigate_incident

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

Instrumentator().instrument(app).expose(app)

@app.get("/health")
def health():
    return {"status": "ok"}

@app.get("/constants")
def constants():
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT name, symbol, value, unit, description "
                "FROM constants ORDER BY id"
            )
            rows = cur.fetchall()

    return [
        {
            "name": r[0],
            "symbol": r[1],
            "value": r[2],
            "unit": r[3],
            "description": r[4],
        }
        for r in rows
    ]

@app.get("/constant/{name}")
def constant(name: str):
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT name, symbol, value, unit, description "
                "FROM constants WHERE name = %s",
                (name,)
            )
            row = cur.fetchone()

    if row is None:
        raise HTTPException(status_code=404, detail="Constant not found")

    return {
        "name": row[0],
        "symbol": row[1],
        "value": row[2],
        "unit": row[3],
        "description": row[4],
    }

@app.get("/calculate")
def calculate(a: float, b: float):
    return {
        "a": a,
        "b": b,
        "sum": a + b,
        "product": a * b
    }

@app.get("/crash")
def crash():
    os.kill(os.getpid(), signal.SIGKILL)

@app.get("/investigate/{incident_id}")
def investigate(incident_id: str):
    try:
        return investigate_incident(incident_id)
    except FileNotFoundError:
        raise HTTPException(
            status_code=404,
            detail=f"Incident {incident_id} not found"
        )
