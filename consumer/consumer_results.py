import json
import pika
import sqlite3
import os

# Ruta absoluta a la DB
def get_db_path():
    ruta_actual = os.path.dirname(os.path.abspath(__file__))
    return os.path.abspath(os.path.join(ruta_actual, "..", "database", "results.db"))

def guardar_en_db(resultado):
    conn = sqlite3.connect(get_db_path())
    cur = conn.cursor()

    cur.execute("""
        INSERT INTO resultados (tiempo, costo_hora, riesgo, costo_total)
        VALUES (?, ?, ?, ?)
    """, (
        resultado["tiempo"],
        resultado["costo_hora"],
        resultado.get("riesgo", 0),
        resultado["costo_total"]
    ))

    conn.commit()
    conn.close()


def main():
    connection = pika.BlockingConnection(
        pika.ConnectionParameters('localhost')
    )
    channel = connection.channel()

    print("✅ Consumidor de resultados escuchando...")

    def callback(ch, method, properties, body):
        resultado = json.loads(body)
        print(f"📥 Resultado recibido: {resultado}")

        guardar_en_db(resultado)

        print("✅ Guardado en SQLite")

        ch.basic_ack(delivery_tag=method.delivery_tag)

    channel.basic_consume(
        queue='results_queue',
        on_message_callback=callback,
        auto_ack=False
    )

    channel.start_consuming()


if __name__ == "__main__":
    main()
