import sqlite3
import os
import time

def get_db_path():
    ruta_actual = os.path.dirname(os.path.abspath(__file__))
    return os.path.abspath(os.path.join(ruta_actual, "..", "database", "results.db"))

def obtener_totales():
    conn = sqlite3.connect(get_db_path())
    cur = conn.cursor()

    cur.execute("SELECT COUNT(*) FROM resultados")
    total = cur.fetchone()[0]

    conn.close()
    return total

def calcular_y_guardar():
    conn = sqlite3.connect(get_db_path())
    cur = conn.cursor()

    cur.execute("""
        SELECT 
            AVG(tiempo),
            AVG(costo_total),
            AVG(riesgo)
        FROM resultados
    """)

    row = cur.fetchone()

    if not row or row[0] is None:
        print("⚠️ No hay resultados aún.")
        conn.close()
        return

    tiempo_prom, costo_prom, riesgo_prom = row

    cur.execute("""
        INSERT INTO resultados_finales (
            tiempo_promedio,
            costo_promedio,
            riesgo_promedio,
            created_at
        )
        VALUES (?, ?, ?, CURRENT_TIMESTAMP)
    """, (
        tiempo_prom,
        costo_prom,
        riesgo_prom
    ))

    conn.commit()
    conn.close()

    print("✅ Resultados finales actualizados")

def main():
    print("📊 Agregador Final iniciado...\n")

    last_total = obtener_totales()

    while True:
        time.sleep(5)  # revisa cada 5 segundos

        nuevo_total = obtener_totales()

        if nuevo_total != last_total:
            print("🔄 Nuevos datos detectados. Recalculando...")
            calcular_y_guardar()
            last_total = nuevo_total
        else:
            print("⏳ Sin cambios...")

if __name__ == "__main__":
    main()
