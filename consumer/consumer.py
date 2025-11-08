import json
import pika
import os
import sqlite3
from dotenv import load_dotenv

load_dotenv()

# ============================================================
#   CARGA DE ARCHIVOS Y MODELO
# ============================================================
def cargar_modelo():
    ruta_actual = os.path.dirname(os.path.abspath(__file__))
    ruta_modelo = os.path.join(ruta_actual, '..', 'data', 'model.json')
    ruta_modelo = os.path.abspath(ruta_modelo)

    with open(ruta_modelo, 'r') as file:
        return json.load(file)


# ============================================================
#   LÓGICA DEL MODELO
# ============================================================
def ejecutar_modelo(escenario):
    tiempo = escenario["tiempo"]
    costo_hora = escenario["costo_hora"]
    riesgo = escenario.get("riesgo", 0)

    # Modelo simple, ajustable
    costo_total = tiempo * costo_hora

    return {
        "tiempo": tiempo,
        "costo_hora": costo_hora,
        "riesgo": riesgo,
        "costo_total": costo_total
    }


# ============================================================
#   GUARDAR RESULTADO EN SQLITE
# ============================================================
def guardar_en_db(resultado):
    ruta_db = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "database", "results.db")
    ruta_db = os.path.abspath(ruta_db)

    conn = sqlite3.connect(ruta_db)
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO resultados (tiempo, costo_hora, riesgo, costo_total, created_at)
        VALUES (?, ?, ?, ?, CURRENT_TIMESTAMP)
    """, (
        resultado["tiempo"],
        resultado["costo_hora"],
        resultado["riesgo"],
        resultado["costo_total"]
    ))

    conn.commit()
    conn.close()


# ============================================================
#   CONSUMIDOR
# ============================================================
def main():
    modelo = cargar_modelo()

    RABBITMQ_URL = os.getenv("RABBITMQ_URL", "amqp://guest:guest@localhost:5672/")
    SCENARIO_QUEUE = os.getenv("SCENARIO_QUEUE", "scenario_queue")
    RESULTS_QUEUE = os.getenv("RESULTS_QUEUE", "results_queue")

    params = pika.URLParameters(RABBITMQ_URL)
    connection = pika.BlockingConnection(params)
    channel = connection.channel()

    channel.queue_declare(queue=SCENARIO_QUEUE, durable=True)
    channel.queue_declare(queue=RESULTS_QUEUE, durable=True)

    print("✅ Consumidor iniciado. Esperando escenarios...\n")


    # --------------------------------------------------------
    # CALLBACK
    # --------------------------------------------------------
    def callback(ch, method, properties, body):
        escenario = json.loads(body)
        print(f"📥 Escenario recibido: {escenario}")

        # Ejecutar modelo
        resultado = ejecutar_modelo(escenario)

        # Guardar en DB
        guardar_en_db(resultado)
        print("💾 Guardado en DB:", resultado)

        # Publicar en results_queue usando el canal correcto
        ch.basic_publish(
            exchange='',
            routing_key=RESULTS_QUEUE,
            body=json.dumps(resultado),
            properties=pika.BasicProperties(delivery_mode=2)
        )
        print(f"📤 Resultado enviado a {RESULTS_QUEUE}: {resultado}")

        # ACK
        ch.basic_ack(delivery_tag=method.delivery_tag)


    channel.basic_consume(
        queue=SCENARIO_QUEUE,
        on_message_callback=callback,
        auto_ack=False
    )

    channel.start_consuming()


if __name__ == "__main__":
    main()
