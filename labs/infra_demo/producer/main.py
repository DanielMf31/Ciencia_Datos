"""
PRODUCER: Envia un mensaje a Kafka cada 2 segundos.

Simula un sensor/dispositivo que reporta datos periodicamente.
Cada mensaje tiene un ID incremental, un timestamp, y un valor aleatorio.
"""
import json
import time
import random
import logging
from datetime import datetime, timezone
from kafka import KafkaProducer

# Logging estructurado (JSON) para que Loki pueda parsearlo
logging.basicConfig(
    level=logging.INFO,
    format='{"time":"%(asctime)s","level":"%(levelname)s","service":"producer","message":"%(message)s"}'
)
log = logging.getLogger("producer")


def create_producer(retries=30):
    """Crear productor Kafka con reintentos (Kafka tarda en arrancar)."""
    for attempt in range(retries):
        try:
            producer = KafkaProducer(
                bootstrap_servers=["kafka:9092"],
                value_serializer=lambda v: json.dumps(v).encode("utf-8"),
                key_serializer=lambda k: k.encode("utf-8") if k else None,
            )
            log.info("Conectado a Kafka")
            return producer
        except Exception as e:
            log.warning(f"Kafka no disponible (intento {attempt+1}/{retries}): {e}")
            time.sleep(2)
    raise ConnectionError("No se pudo conectar a Kafka")


def main():
    producer = create_producer()
    message_id = 0

    log.info("Iniciando envio de mensajes cada 2 segundos...")

    while True:
        message_id += 1
        message = {
            "id": message_id,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "sensor": random.choice(["temperatura", "velocidad", "presion"]),
            "value": round(random.uniform(10, 100), 2),
            "unit": "unidad",
        }

        producer.send("eventos", key=f"sensor-{message_id % 3}", value=message)
        log.info(f"Enviado mensaje #{message_id}: {message['sensor']}={message['value']}")

        time.sleep(2)


if __name__ == "__main__":
    main()
