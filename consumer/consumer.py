import json
import pika
import os
import sqlite3

# === RUTAS ===
def cargar_modelo():
    ruta_actual = os.path.dirname(os.path.abspath(__file__))
    ruta_modelo = os.path.join(ruta_actual, '..', 'data', 'model.json')
    ruta_modelo = os.path.abspath(ruta_modelo)

    with open(ruta_modelo, 'r') as file:
        return json.load(file)

# === FUNCIÓN DEL MODELO ===
def ejecutar_modelo(escenario):
    tiempo = escenario["tiempo"]
    costo_hora = escenario["costo_hora"]
    riesgo = escenario.get("riesgo", 0)

    costo_total = (tiempo * costo_hora) + riesgo

    return {
        "tiempo": tiempo,
        "costo_hora": costo_hora,
        "riesgo": riesgo,
        "costo_total": costo_total
    }

# === GUARDAR EN SQLITE ===
def guardar_en_db(resultado):
    ruta_db = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "database", "results.db")
    ruta_db = os.path.abspath(ruta_db)

    conn = sqlite3.connect(ruta_db)
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO resultados (tiempo, costo_hora, riesgo, costo_total)
        VALUES (?, ?, ?, ?)
    """, (
        resultado["tiempo"],
        resultado["costo_hora"],
        resultado["riesgo"],
        resultado["costo_total"]
    ))

    conn.commit()
    conn.close()

# === CONSUMIDOR ===
def main():
    modelo = cargar_modelo()

    connection = pika.BlockingConnection(
        pika.ConnectionParameters(host='localhost')
    )
    channel = connection.channel()

    print("✅ Consumidor iniciado. Esperando escenarios...")


    # ✅ ✅ ✅ AQUÍ VA EL CALLBACK ✅ ✅ ✅
    def callback(ch, method, properties, body):
        escenario = json.loads(body)
        print(f"📥 Recibido escenario: {escenario}")

        resultado = ejecutar_modelo(escenario)

        # ✅ Guardar en SQLite
        guardar_en_db(resultado)
        print("💾 Guardado en DB:", resultado)

        # ✅ Publicar en results_queue
        channel.basic_publish(
            exchange='',
            routing_key='results_queue',
            body=json.dumps(resultado)
        )
        print(f"📤 Resultado enviado: {resultado}")

        # ✅ Confirmar a RabbitMQ
        ch.basic_ack(delivery_tag=method.delivery_tag)


    channel.basic_consume(
        queue='scenario_queue',
        on_message_callback=callback,
        auto_ack=False
    )

    channel.start_consuming()

if __name__ == "__main__":
    main()
