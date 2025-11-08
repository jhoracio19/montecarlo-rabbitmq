import sqlite3
import time
import os

def get_db_path():
    ruta_actual = os.path.dirname(os.path.abspath(__file__))
    return os.path.abspath(os.path.join(ruta_actual, "..", "database", "results.db"))

def calcular_resultados_finales():
    conn = sqlite3.connect(get_db_path())
    cur = conn.cursor()

    # 1. Leer todos los resultados
    cur.execute("""
        SELECT tiempo, costo_total, riesgo
        FROM resultados
    """)
    rows = cur.fetchall()

    if not rows:
        print("⚠️ No hay resultados aún.")
        conn.close()
        return

    tiempos = [r[0] for r in rows]
    costos = [r[1] for r in rows]
    riesgos = [r[2] for r in rows]

    tiempo_prom = sum(tiempos) / len(tiempos)
    costo_prom = sum(costos) / len(costos)
    riesgo_prom = sum(riesgos) / len(riesgos)

    # 2. Guardar en tabla resultados_finales
    cur.execute("""
        INSERT INTO resultados_finales (tiempo_promedio, costo_promedio, riesgo_promedio)
        VALUES (?, ?, ?)
    """, (tiempo_prom, costo_prom, riesgo_prom))

    conn.commit()
    conn.close()

    print("✅ Resultados finales agregados correctamente")

def main():
    print("📊 Calculador de resultados finales iniciado...")
    while True:
        calcular_resultados_finales()
        time.sleep(10)  # cada 10 segundos refresca

if __name__ == "__main__":
    main()
