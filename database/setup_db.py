import sqlite3
import os

def crear_db():
    ruta_actual = os.path.dirname(os.path.abspath(__file__))
    ruta_db = os.path.join(ruta_actual, "results.db")

    conn = sqlite3.connect(ruta_db)
    cursor = conn.cursor()

    # ✅ Tabla de resultados individuales
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS resultados (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            tiempo REAL NOT NULL,
            costo_hora REAL NOT NULL,
            riesgo REAL NOT NULL,
            costo_total REAL NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # ✅ Tabla de resultados finales
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS resultados_finales (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            tiempo_promedio REAL NOT NULL,
            costo_promedio REAL NOT NULL,
            riesgo_promedio REAL NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    conn.commit()
    conn.close()
    print("✅ Base de datos lista con tablas completas.")

if __name__ == "__main__":
    crear_db()
