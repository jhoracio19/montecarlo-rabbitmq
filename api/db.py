import os
import sqlite3
from typing import Dict, Any
from dotenv import load_dotenv

load_dotenv()

# Intentar leer ruta de .env
DB_PATH = os.getenv("DB_PATH")

def get_db_path() -> str:
    """
    Devuelve la ruta absoluta a la base de datos.
    Si existe DB_PATH en .env, usa esa ruta.
    Si no, usa database/results.db relativo al proyecto.
    """
    if DB_PATH:
        return os.path.abspath(DB_PATH)

    # Ruta por defecto si no hay .env
    ruta_actual = os.path.dirname(os.path.abspath(__file__))
    return os.path.abspath(os.path.join(ruta_actual, "..", "database", "results.db"))


def connect() -> sqlite3.Connection:
    conn = sqlite3.connect(get_db_path())
    conn.row_factory = sqlite3.Row
    return conn



# ✅ Obtener resultados (paginado)
def get_results(limit: int = 100, offset: int = 0):
    with connect() as conn:
        cur = conn.cursor()
        cur.execute(
            """
            SELECT 
                id, tiempo, costo_hora, riesgo, costo_total, created_at
            FROM resultados
            ORDER BY id DESC
            LIMIT ? OFFSET ?
            """,
            (limit, offset),
        )
        return [dict(r) for r in cur.fetchall()]


# ✅ Obtener resultados finales (paginado)
def get_final_results(limit: int = 100, offset: int = 0):
    with connect() as conn:
        cur = conn.cursor()
        cur.execute(
            """
            SELECT 
                id, tiempo_promedio, costo_promedio, riesgo_promedio, created_at
            FROM resultados_finales
            ORDER BY id DESC
            LIMIT ? OFFSET ?
            """,
            (limit, offset),
        )
        return [dict(r) for r in cur.fetchall()]



# ✅ Obtener estadísticas generales
def get_stats() -> Dict[str, Any]:
    with connect() as conn:
        cur = conn.cursor()
        cur.execute(
            """
            SELECT 
              COUNT(*) as total,
              AVG(tiempo) as tiempo_avg, 
              MIN(tiempo) as tiempo_min, 
              MAX(tiempo) as tiempo_max,

              AVG(costo_total) as costo_avg, 
              MIN(costo_total) as costo_min, 
              MAX(costo_total) as costo_max,

              AVG(riesgo) as riesgo_avg
            FROM resultados
            """
        )
        row = cur.fetchone()
        return dict(row) if row else {}



# ✅ ✅ NUEVO: Contar resultados para paginación
def count_results() -> int:
    """Cuenta cuántos registros totales hay en resultados."""
    with connect() as conn:
        cur = conn.cursor()
        cur.execute("SELECT COUNT(*) FROM resultados")
        (count,) = cur.fetchone()
        return count


# ✅ ✅ NUEVO: Contar resultados finales si quieres paginarlos
def count_final_results() -> int:
    """Cuenta cuántos registros totales hay en resultados_finales."""
    with connect() as conn:
        cur = conn.cursor()
        cur.execute("SELECT COUNT(*) FROM resultados_finales")
        (count,) = cur.fetchone()
        return count
