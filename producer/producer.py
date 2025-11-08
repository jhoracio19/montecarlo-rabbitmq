import json
import pika
import random
import os

# Leer el archivo del modelo

def cargar_modelo():
    # Ruta real del archivo producer.py
    ruta_actual = os.path.dirname(os.path.abspath(__file__))
    
    # Subir a la carpeta raíz y entrar a data/model.json
    ruta_modelo = os.path.join(ruta_actual, '..', 'data', 'model.json')

    # Convertir a ruta absoluta
    ruta_modelo = os.path.abspath(ruta_modelo)

    with open(ruta_modelo, 'r') as file:
        return json.load(file)


# Generar un valor con distribución normal (acotada)
def normal_bounded(mean, stddev, min_val, max_val):
    while True:
        value = random.gauss(mean, stddev)
        if min_val <= value <= max_val:
            return value

# Elegir penalización discreta
def elegir_discreto(values):
    r = random.random()
    acumulado = 0
    for item in values:
        acumulado += item["prob"]
        if r <= acumulado:
            return item["value"]

# Generar un escenario individual
def generar_escenario(modelo):
    tiempo_cfg = modelo["variables"]["tiempo"]
    costo_cfg = modelo["variables"]["costo_hora"]
    riesgo_cfg = modelo["variables"]["penalizacion_riesgo"]

    escenario = {
        "tiempo": normal_bounded(
            tiempo_cfg["mean"],
            tiempo_cfg["stddev"],
            tiempo_cfg["min"],
            tiempo_cfg["max"]
        ),
        "costo_hora": random.uniform(
            costo_cfg["min"],
            costo_cfg["max"]
        ),
        "riesgo": elegir_discreto(
            riesgo_cfg["values"]
        )
    }

    return escenario

# Conexión a RabbitMQ
def conectar_rabbit():
    connection = pika.BlockingConnection(
        pika.ConnectionParameters(host='localhost')
    )
    return connection.channel()

def main():
    # Cargar modelo
    modelo = cargar_modelo()

    # Conexión
    channel = conectar_rabbit()

    print("✅ Productor iniciado. Enviando escenarios...")

    # Generar N escenarios
    N = 100  # Puedes poner 1000 después
    for i in range(N):
        escenario = generar_escenario(modelo)
        msg = json.dumps(escenario)
        
        channel.basic_publish(
            exchange='',
            routing_key='scenario_queue',
            body=msg
        )

        print(f"→ Enviado escenario {i+1}: {msg}")

    print("✅ Escenarios enviados correctamente.")
    channel.close()

if __name__ == "__main__":
    main()
