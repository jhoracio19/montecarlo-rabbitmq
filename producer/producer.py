import json
import pika
import random
import os

# ===========================
# CARGAR MODELO
# ===========================
def cargar_modelo():
    ruta_actual = os.path.dirname(os.path.abspath(__file__))
    ruta_modelo = os.path.abspath(os.path.join(ruta_actual, '..', 'data', 'model.json'))
    
    with open(ruta_modelo, 'r') as file:
        return json.load(file)

# ===========================
# FUNCIONES DE GENERACIÓN
# ===========================
def normal_bounded(mean, stddev, min_val, max_val):
    while True:
        val = random.gauss(mean, stddev)
        if min_val <= val <= max_val:
            return val

def elegir_discreto(values):
    r = random.random()
    suma = 0
    for item in values:
        suma += item["prob"]
        if r <= suma:
            return item["value"]

def generar_escenario(modelo):
    t_cfg = modelo["variables"]["tiempo"]
    c_cfg = modelo["variables"]["costo_hora"]
    r_cfg = modelo["variables"]["penalizacion_riesgo"]

    return {
        "tiempo": normal_bounded(t_cfg["mean"], t_cfg["stddev"], t_cfg["min"], t_cfg["max"]),
        "costo_hora": random.uniform(c_cfg["min"], c_cfg["max"]),
        "riesgo": elegir_discreto(r_cfg["values"])
    }

# ===========================
# CONEXIÓN A RABBIT
# ===========================
def conectar_rabbit():
    connection = pika.BlockingConnection(
        pika.ConnectionParameters(host='localhost')
    )
    ch = connection.channel()
    ch.confirm_delivery()  # ✅ confirmación
    ch.queue_declare(queue='scenario_queue', durable=True)
    return ch

# ===========================
# MAIN
# ===========================
def main():
    modelo = cargar_modelo()
    channel = conectar_rabbit()

    N = int(os.getenv("PRODUCER_BATCH", 200))

    print(f"✅ Productor iniciado. Enviando {N} escenarios...")

    for i in range(N):
        escenario = generar_escenario(modelo)
        msg = json.dumps(escenario)

        channel.basic_publish(
            exchange='',
            routing_key='scenario_queue',
            body=msg,
            properties=pika.BasicProperties(delivery_mode=2)
        )

        print(f"→ Escenario enviado {i+1}/{N}")

    print("✅ Todos los escenarios fueron enviados.")
    channel.close()

if __name__ == "__main__":
    main()
