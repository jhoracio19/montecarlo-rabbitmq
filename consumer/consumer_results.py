import json
import pika
import sqlite3
import os
from dotenv import load_dotenv

load_dotenv()

# ============================================================
#   RUTA DB
# ============================================================
def get_db_path():
    ruta_actual = os.path.dirname(os.path.abspath(__file__))
    return os.path.abspath(os.path.join(ruta_actual, "..", "database", "results.db"))

# ============================================================
#   CALCULAR PROMEDIOS PARA resultados_finales
# ============================================================
def calcular_promedios():
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
    conn.close()

    if row and row[0] is not None:
        return {
            "tiempo_promedio": row[0],
            "costo_promedio": row[1],
            "riesgo_promedio": row[2]
        }

    return None

# ============================================================
#   GUARDAR EN resultados_finales
# ============================================================
def guardar_final(promedios):
    conn = sqlite3.connect(get_db_path())
    cur = conn.cursor()

    cur.execute("""
        INSERT INTO resultados_finales (
            tiempo_promedio,
            costo_promedio,
            riesgo_promedio,
            created_at
        )
        VALUES (?, ?, ?, CURRENT_TIMESTAMP)
    """, (
        promedios["tiempo_promedio"],
        promedios["costo_promedio"],
        promedios["riesgo_promedio"]
    ))

    conn.commit()
    conn.close()

# ============================================================
#   CONSUMIDOR
# ============================================================
def main():
    RABBITMQ_URL = os.getenv("RABBITMQ_URL", "amqp://guest:guest@localhost:5672/")
    RESULTS_QUEUE = os.getenv("RESULTS_QUEUE", "results_queue")

    params = pika.URLParameters(RABBITMQ_URL)
    connection = pika.BlockingConnection(params)
    channel = connection.channel()

    channel.queue_declare(queue=RESULTS_QUEUE, durable=True)

    print("✅ Consumidor de resultados escuchando...")

    def callback(ch, method, properties, body):
        resultado = json.loads(body)
        print(f"📥 Resultado recibido: {resultado}")

        # ✅ RECOMPUTAR PROMEDIOS
        promedios = calcular_promedios()

        if promedios:
            guardar_final(promedios)
            print("✅ Guardado en resultados_finales:", promedios)

        # Confirmación
        ch.basic_ack(delivery_tag=method.delivery_tag)

    channel.basic_consume(
        queue=RESULTS_QUEUE,
        on_message_callback=callback,
        auto_ack=False
    )

    channel.start_consuming()


if __name__ == "__main__":
    main()
