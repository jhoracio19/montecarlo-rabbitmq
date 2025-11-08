import os
import sqlite3
from typing import Tuple, Dict, Any
from dotenv import load_dotenv

load_dotenv()

DB_PATH = os.getenv("DB_PATH")



def get_db_path() -> str:
    if DB_PATH:
        return DB_PATH
    # por si no hay .env
    ruta_actual = os.path.dirname(os.path.abspath(__file__))
    return os.path.abspath(os.path.join(ruta_actual, "..", "database", "results.db"))

def connect() -> sqlite3.Connection:
    conn = sqlite3.connect(get_db_path())
    conn.row_factory = sqlite3.Row
    return conn

def get_results(limit: int = 100, offset: int = 0):
    with connect() as conn:
        cur = conn.cursor()
        cur.execute(
            "SELECT id, tiempo, costo_hora, riesgo, costo_total, created_at "
            "FROM resultados ORDER BY id DESC LIMIT ? OFFSET ?",
            (limit, offset,)
        )
        return [dict(r) for r in cur.fetchall()]

def get_final_results(limit: int = 100, offset: int = 0):
    with connect() as conn:
        cur = conn.cursor()
        cur.execute(
            "SELECT id, tiempo_promedio, costo_promedio, riesgo_promedio, created_at "
            "FROM resultados_finales ORDER BY id DESC LIMIT ? OFFSET ?",
            (limit, offset,)
        )
        return [dict(r) for r in cur.fetchall()]

def get_stats() -> Dict[str, Any]:
    with connect() as conn:
        cur = conn.cursor()
        cur.execute(
            """
            SELECT 
              COUNT(*) as n,
              AVG(tiempo) as tiempo_avg, MIN(tiempo) as tiempo_min, MAX(tiempo) as tiempo_max,
              AVG(costo_total) as costo_avg, MIN(costo_total) as costo_min, MAX(costo_total) as costo_max,
              AVG(riesgo) as riesgo_avg
            FROM resultados
            """
        )
        row = cur.fetchone()
        return dict(row) if row else {}

