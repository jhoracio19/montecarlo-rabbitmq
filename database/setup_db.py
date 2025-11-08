import sqlite3
import os

def crear_db():
    ruta_actual = os.path.dirname(os.path.abspath(__file__))
    ruta_db = os.path.join(ruta_actual, "results.db")

    conn = sqlite3.connect(ruta_db)
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS resultados (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            tiempo REAL,
            costo_hora REAL,
            riesgo REAL,
            costo_total REAL
        )
    """)

    conn.commit()
    conn.close()
    print("✅ Base de datos lista.")

if __name__ == "__main__":
    crear_db()
