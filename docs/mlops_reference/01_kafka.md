# Apache Kafka - Guia de Referencia con Python

## Indice

1. [Que es Kafka](#1-que-es-kafka)
2. [Conceptos clave](#2-conceptos-clave)
3. [Instalacion y setup](#3-instalacion-y-setup)
4. [Productor basico](#4-productor-basico)
5. [Consumidor basico](#5-consumidor-basico)
6. [Serializacion JSON](#6-serializacion-json)
7. [Consumer Groups](#7-consumer-groups)
8. [Multiples consumidores del mismo topic](#8-multiples-consumidores-del-mismo-topic)
9. [Particiones y keys](#9-particiones-y-keys)
10. [Offsets y control manual](#10-offsets-y-control-manual)
11. [Productor asincrono con callbacks](#11-productor-asincrono-con-callbacks)
12. [Batch producing (alto rendimiento)](#12-batch-producing)
13. [Ejemplo real: telemetria vehicular](#13-ejemplo-real-telemetria-vehicular)
14. [Kafka con FastAPI](#14-kafka-con-fastapi)
15. [Docker Compose para desarrollo](#15-docker-compose-para-desarrollo)

---

## 1. Que es Kafka

Kafka es un **log distribuido** (no una cola tradicional):
- Los mensajes se **persisten en disco** (no solo en RAM)
- Multiples consumidores pueden leer los **mismos mensajes**
- Los mensajes no se borran al leerlos (se retienen por tiempo configurable)
- Escala horizontalmente con **particiones**

```
Arquitectura basica:

Productores ──> [Broker 1] [Broker 2] [Broker 3]  <── Consumidores
                      (cluster de Kafka)

Topic "telemetria":
  Particion 0: [msg0, msg3, msg6, msg9,  ...]
  Particion 1: [msg1, msg4, msg7, msg10, ...]
  Particion 2: [msg2, msg5, msg8, msg11, ...]
```

---

## 2. Conceptos clave

| Concepto | Que es | Analogia |
|----------|--------|----------|
| **Topic** | Canal/categoria de mensajes | Una tabla de base de datos |
| **Partition** | Subdivision del topic para paralelismo | Sharding de una tabla |
| **Producer** | Envia mensajes a un topic | INSERT en una tabla |
| **Consumer** | Lee mensajes de un topic | SELECT de una tabla |
| **Consumer Group** | Conjunto de consumidores que se reparten las particiones | Workers de Celery |
| **Offset** | Posicion del consumidor en la particion | Cursor/bookmark |
| **Broker** | Servidor de Kafka | Nodo de la base de datos |
| **Key** | Clave del mensaje (determina la particion) | Primary key |
| **Retention** | Cuanto tiempo se guardan los mensajes | TTL / expiracion |

---

## 3. Instalacion y setup

```bash
# Libreria Python para Kafka
pip install kafka-python

# Alternativa mas moderna (confluent, mas rapida)
pip install confluent-kafka

# Para desarrollo local, usa Docker (ver seccion 15)
```

---

## 4. Productor basico

```python
from kafka import KafkaProducer

# Crear productor - se conecta al broker
producer = KafkaProducer(
    bootstrap_servers=['localhost:9092'],  # direccion del broker
    # Si tienes multiples brokers:
    # bootstrap_servers=['broker1:9092', 'broker2:9092', 'broker3:9092']
)

# Enviar un mensaje (debe ser bytes)
producer.send('mi-topic', value=b'Hola Kafka!')

# send() es asincrono - el mensaje se encola en un buffer interno
# Para asegurar que se envio:
future = producer.send('mi-topic', value=b'Mensaje importante')
result = future.get(timeout=10)  # bloquea hasta confirmar
print(f"Enviado a particion {result.partition}, offset {result.offset}")

# Forzar envio de todos los mensajes en buffer
producer.flush()

# Cerrar conexion al terminar
producer.close()
```

---

## 5. Consumidor basico

```python
from kafka import KafkaConsumer

# Crear consumidor
consumer = KafkaConsumer(
    'mi-topic',                             # topic a leer
    bootstrap_servers=['localhost:9092'],
    auto_offset_reset='earliest',           # desde donde leer si es nuevo:
                                            #   'earliest' = desde el principio
                                            #   'latest'   = solo mensajes nuevos
    enable_auto_commit=True,                # confirmar lectura automaticamente
    group_id='mi-grupo'                     # grupo de consumidores
)

# Leer mensajes (bucle infinito)
for message in consumer:
    print(f"Topic: {message.topic}")
    print(f"Particion: {message.partition}")
    print(f"Offset: {message.offset}")
    print(f"Key: {message.key}")
    print(f"Valor: {message.value.decode('utf-8')}")
    print(f"Timestamp: {message.timestamp}")
    print("---")

# El consumer se queda bloqueado esperando mensajes nuevos
# Para salir limpiamente:
consumer.close()
```

---

## 6. Serializacion JSON

```python
import json
from kafka import KafkaProducer, KafkaConsumer

# --- PRODUCTOR con JSON ---
producer = KafkaProducer(
    bootstrap_servers=['localhost:9092'],
    # Serializador: convierte dict -> bytes automaticamente
    value_serializer=lambda v: json.dumps(v).encode('utf-8'),
    key_serializer=lambda k: k.encode('utf-8') if k else None
)

# Ahora puedes enviar dicts directamente
telemetry_data = {
    "vehicle_id": "V001",
    "timestamp": "2025-01-15T14:23:01",
    "speed_kmh": 85.3,
    "battery_temp": 42.1,
    "battery_soc": 78.5,
    "gps_lat": 19.4326,
    "gps_lon": -99.1332
}

producer.send('telemetria', key="V001", value=telemetry_data)
producer.flush()


# --- CONSUMIDOR con JSON ---
consumer = KafkaConsumer(
    'telemetria',
    bootstrap_servers=['localhost:9092'],
    # Deserializador: convierte bytes -> dict automaticamente
    value_deserializer=lambda v: json.loads(v.decode('utf-8')),
    key_deserializer=lambda k: k.decode('utf-8') if k else None,
    auto_offset_reset='earliest',
    group_id='procesador'
)

for message in consumer:
    data = message.value  # ya es un dict
    print(f"Vehiculo {data['vehicle_id']}: {data['speed_kmh']} km/h")

    if data['battery_temp'] > 45:
        print(f"  ALERTA: temperatura critica {data['battery_temp']}C!")
```

---

## 7. Consumer Groups

Multiples consumidores en el mismo grupo se **reparten** las particiones:

```python
# Si el topic tiene 4 particiones y lanzas 2 consumidores del mismo grupo:
#   Consumidor 1 lee: particiones 0, 1
#   Consumidor 2 lee: particiones 2, 3
# Kafka balancea automaticamente.

# --- worker_1.py ---
consumer = KafkaConsumer(
    'telemetria',
    bootstrap_servers=['localhost:9092'],
    group_id='guardado_db',  # mismo grupo
    auto_offset_reset='earliest'
)
for msg in consumer:
    save_to_database(msg.value)

# --- worker_2.py ---
# Ejecutas el mismo codigo en otro proceso
# Kafka asigna particiones diferentes automaticamente

# --- Si un worker se cae ---
# Kafka reasigna sus particiones a los workers vivos (rebalanceo)
```

---

## 8. Multiples consumidores del mismo topic

Grupos **diferentes** leen los **mismos mensajes** independientemente:

```python
# --- servicio_1.py: guardar en base de datos ---
consumer_db = KafkaConsumer(
    'telemetria',
    bootstrap_servers=['localhost:9092'],
    group_id='guardado_db',          # grupo A
    value_deserializer=lambda v: json.loads(v)
)
for msg in consumer_db:
    save_to_postgres(msg.value)


# --- servicio_2.py: deteccion de anomalias ---
consumer_ml = KafkaConsumer(
    'telemetria',
    bootstrap_servers=['localhost:9092'],
    group_id='anomalias',            # grupo B (diferente!)
    value_deserializer=lambda v: json.loads(v)
)
for msg in consumer_ml:
    prediction = anomaly_model.predict(msg.value)
    if prediction == "anomalia":
        send_alert(msg.value)


# --- servicio_3.py: metricas para Grafana ---
consumer_metrics = KafkaConsumer(
    'telemetria',
    bootstrap_servers=['localhost:9092'],
    group_id='metricas',             # grupo C (diferente!)
    value_deserializer=lambda v: json.loads(v)
)
for msg in consumer_metrics:
    update_prometheus_metrics(msg.value)


# Los tres servicios reciben TODOS los mensajes
# Son independientes entre si
# Si uno se cae, los otros siguen funcionando
```

---

## 9. Particiones y keys

```python
# La KEY determina a que particion va el mensaje
# Misma key = misma particion = orden garantizado

producer = KafkaProducer(
    bootstrap_servers=['localhost:9092'],
    value_serializer=lambda v: json.dumps(v).encode('utf-8'),
    key_serializer=lambda k: k.encode('utf-8')
)

# Todos los mensajes de V001 van a la MISMA particion
# Esto garantiza orden cronologico por vehiculo
producer.send('telemetria', key='V001', value={"speed": 80, "temp": 35})
producer.send('telemetria', key='V001', value={"speed": 85, "temp": 36})
producer.send('telemetria', key='V001', value={"speed": 82, "temp": 35})

# V002 puede ir a otra particion (Kafka decide por hash de la key)
producer.send('telemetria', key='V002', value={"speed": 60, "temp": 30})

# Sin key = round-robin entre particiones (no hay orden garantizado)
producer.send('telemetria', value={"log": "evento generico"})

# Visualizacion:
# Particion 0: [V001:msg1, V001:msg2, V001:msg3, ...]  <- orden garantizado
# Particion 1: [V002:msg1, V002:msg2, ...]
# Particion 2: [V003:msg1, V005:msg1, ...]              <- varias keys pueden
#                                                           compartir particion
```

---

## 10. Offsets y control manual

```python
# Por defecto, Kafka hace auto-commit del offset
# Pero para procesamiento critico, quieres control manual:

consumer = KafkaConsumer(
    'telemetria',
    bootstrap_servers=['localhost:9092'],
    group_id='procesamiento_critico',
    enable_auto_commit=False,  # NO confirmar automaticamente
    auto_offset_reset='earliest'
)

for message in consumer:
    try:
        # Procesar el mensaje
        result = process_telemetry(message.value)
        save_to_database(result)

        # Solo confirmar DESPUES de procesar exitosamente
        consumer.commit()
        # Si la app se cae antes del commit, Kafka reenvia el mensaje

    except Exception as e:
        print(f"Error procesando mensaje: {e}")
        # NO hacemos commit -> Kafka reenviara este mensaje
        # Puedes implementar logica de reintento, dead letter queue, etc.


# --- Rebobinar: volver a leer desde el principio ---
from kafka import TopicPartition

consumer = KafkaConsumer(
    bootstrap_servers=['localhost:9092'],
    group_id='reprocesamiento'
)
# Asignar particion manualmente
tp = TopicPartition('telemetria', 0)  # topic, particion
consumer.assign([tp])
consumer.seek_to_beginning(tp)  # volver al inicio

for msg in consumer:
    reprocess(msg.value)


# --- Saltar a un timestamp especifico ---
import datetime

consumer.assign([tp])
# Buscar offset del timestamp deseado
target_time = int(datetime.datetime(2025, 1, 15, 14, 0).timestamp() * 1000)
offsets = consumer.offsets_for_times({tp: target_time})
consumer.seek(tp, offsets[tp].offset)
# Ahora lee desde el 15 de enero a las 14:00
```

---

## 11. Productor asincrono con callbacks

```python
from kafka import KafkaProducer

producer = KafkaProducer(
    bootstrap_servers=['localhost:9092'],
    value_serializer=lambda v: json.dumps(v).encode('utf-8'),
    # Configuracion de rendimiento
    acks='all',            # esperar confirmacion de todas las replicas
    retries=3,             # reintentar 3 veces si falla
    linger_ms=10,          # esperar 10ms para agrupar mensajes (batch)
    batch_size=32768,      # tamano del batch en bytes (32KB)
    compression_type='gzip' # comprimir para reducir red
)

# Callback cuando el mensaje se envia exitosamente
def on_success(metadata):
    print(f"Enviado a {metadata.topic}[{metadata.partition}] offset {metadata.offset}")

# Callback cuando falla
def on_error(exception):
    print(f"Error enviando mensaje: {exception}")

# Enviar con callbacks (no bloquea)
producer.send(
    'telemetria',
    value={"vehicle_id": "V001", "speed": 85}
).add_callback(on_success).add_errback(on_error)

# El programa sigue ejecutandose sin esperar
print("Mensaje en camino...")

producer.flush()  # esperar a que todos los pendientes se envien
```

---

## 12. Batch producing

```python
import time
from kafka import KafkaProducer

producer = KafkaProducer(
    bootstrap_servers=['localhost:9092'],
    value_serializer=lambda v: json.dumps(v).encode('utf-8'),
    key_serializer=lambda k: k.encode('utf-8'),
    linger_ms=50,       # esperar 50ms para agrupar en batches
    batch_size=65536,   # batches de 64KB
    compression_type='snappy'
)

# Simular envio masivo de telemetria
vehicles = [f"V{str(i).zfill(3)}" for i in range(1, 51)]

while True:
    for vehicle_id in vehicles:
        data = {
            "vehicle_id": vehicle_id,
            "timestamp": time.time(),
            "speed_kmh": random.uniform(0, 130),
            "battery_temp": random.uniform(20, 50),
            "fuel_consumption": random.uniform(3, 20),
        }
        # No bloquea - se acumula en buffer interno
        producer.send('telemetria', key=vehicle_id, value=data)

    # Kafka agrupa automaticamente los mensajes del buffer en batches
    # y los envia juntos (mucho mas eficiente que uno por uno)
    time.sleep(1)  # enviar cada segundo

# Rendimiento tipico: >100,000 mensajes/segundo por productor
```

---

## 13. Ejemplo real: telemetria vehicular

```python
"""
Sistema completo de telemetria vehicular con Kafka.

Arquitectura:
  Coches -> Gateway -> Kafka -> [DB, ML, Dashboard, Alertas]
"""
import json
import time
from datetime import datetime
from kafka import KafkaProducer, KafkaConsumer
from threading import Thread


# =============================================================
# PRODUCTOR: Gateway que recibe datos de los coches
# =============================================================

class TelemetryGateway:
    """Recibe telemetria via HTTP/MQTT y la publica en Kafka."""

    def __init__(self, kafka_servers):
        self.producer = KafkaProducer(
            bootstrap_servers=kafka_servers,
            value_serializer=lambda v: json.dumps(v).encode('utf-8'),
            key_serializer=lambda k: k.encode('utf-8'),
            acks='all',
            compression_type='snappy'
        )

    def publish(self, vehicle_id: str, telemetry: dict):
        """Publicar telemetria de un vehiculo."""
        telemetry['timestamp'] = datetime.utcnow().isoformat()
        telemetry['vehicle_id'] = vehicle_id

        # Key = vehicle_id -> misma particion -> orden garantizado
        self.producer.send(
            topic='telemetria-raw',
            key=vehicle_id,
            value=telemetry
        )

    def close(self):
        self.producer.flush()
        self.producer.close()


# =============================================================
# CONSUMIDOR 1: Guardar en base de datos
# =============================================================

class DatabaseSaver:
    """Consume telemetria y la guarda en PostgreSQL."""

    def __init__(self, kafka_servers):
        self.consumer = KafkaConsumer(
            'telemetria-raw',
            bootstrap_servers=kafka_servers,
            group_id='svc-database',
            value_deserializer=lambda v: json.loads(v),
            enable_auto_commit=False,
            auto_offset_reset='earliest'
        )
        self.batch = []
        self.batch_size = 100

    def run(self):
        print("[DB] Esperando mensajes...")
        for message in self.consumer:
            self.batch.append(message.value)

            # Insertar en lotes de 100 (mas eficiente)
            if len(self.batch) >= self.batch_size:
                self._flush_batch()
                self.consumer.commit()

    def _flush_batch(self):
        # En produccion: INSERT batch a PostgreSQL/TimescaleDB
        print(f"[DB] Guardando {len(self.batch)} registros")
        # db.execute("INSERT INTO telemetry VALUES (%s, %s, ...)", self.batch)
        self.batch = []


# =============================================================
# CONSUMIDOR 2: Deteccion de anomalias en tiempo real
# =============================================================

class AnomalyDetector:
    """Consume telemetria y detecta anomalias con el modelo ML."""

    def __init__(self, kafka_servers, model_path):
        self.consumer = KafkaConsumer(
            'telemetria-raw',
            bootstrap_servers=kafka_servers,
            group_id='svc-anomalias',
            value_deserializer=lambda v: json.loads(v),
            auto_offset_reset='latest'  # solo datos nuevos
        )
        # self.model = joblib.load(model_path)
        self.alert_producer = KafkaProducer(
            bootstrap_servers=kafka_servers,
            value_serializer=lambda v: json.dumps(v).encode('utf-8')
        )

    def run(self):
        print("[ML] Esperando mensajes...")
        for message in self.consumer:
            data = message.value

            # Verificaciones basadas en reglas (rapido)
            alerts = []
            if data.get('battery_temp', 0) > 45:
                alerts.append({
                    "type": "TEMP_CRITICA",
                    "severity": "HIGH",
                    "vehicle_id": data['vehicle_id'],
                    "value": data['battery_temp'],
                    "threshold": 45,
                    "timestamp": data['timestamp']
                })

            if data.get('speed_kmh', 0) > 120:
                alerts.append({
                    "type": "VELOCIDAD_EXCESIVA",
                    "severity": "MEDIUM",
                    "vehicle_id": data['vehicle_id'],
                    "value": data['speed_kmh'],
                    "threshold": 120,
                    "timestamp": data['timestamp']
                })

            # Publicar alertas en otro topic
            for alert in alerts:
                self.alert_producer.send('alertas', value=alert)
                print(f"[ML] ALERTA: {alert['type']} en {alert['vehicle_id']}")


# =============================================================
# CONSUMIDOR 3: Alertas -> Notificaciones
# =============================================================

class AlertNotifier:
    """Consume alertas y envia notificaciones."""

    def __init__(self, kafka_servers):
        self.consumer = KafkaConsumer(
            'alertas',
            bootstrap_servers=kafka_servers,
            group_id='svc-notificaciones',
            value_deserializer=lambda v: json.loads(v),
            auto_offset_reset='latest'
        )

    def run(self):
        print("[NOTIFY] Esperando alertas...")
        for message in self.consumer:
            alert = message.value

            if alert['severity'] == 'HIGH':
                self._send_slack(alert)
                self._send_sms(alert)
            elif alert['severity'] == 'MEDIUM':
                self._send_slack(alert)

    def _send_slack(self, alert):
        print(f"[SLACK] {alert['type']}: vehiculo {alert['vehicle_id']}")
        # requests.post(SLACK_WEBHOOK, json={"text": f"..."})

    def _send_sms(self, alert):
        print(f"[SMS] Alerta critica: {alert['vehicle_id']}")
        # twilio_client.messages.create(...)


# =============================================================
# LANZAR TODO
# =============================================================

if __name__ == "__main__":
    KAFKA = ['localhost:9092']

    # Lanzar consumidores en threads separados
    db_saver = DatabaseSaver(KAFKA)
    anomaly_detector = AnomalyDetector(KAFKA, "models/anomaly.pkl")
    notifier = AlertNotifier(KAFKA)

    Thread(target=db_saver.run, daemon=True).start()
    Thread(target=anomaly_detector.run, daemon=True).start()
    Thread(target=notifier.run, daemon=True).start()

    # Simular envio de telemetria
    gateway = TelemetryGateway(KAFKA)

    import random
    vehicles = [f"V{str(i).zfill(3)}" for i in range(1, 11)]

    while True:
        for vid in vehicles:
            gateway.publish(vid, {
                "speed_kmh": random.uniform(0, 130),
                "battery_temp": random.uniform(20, 55),
                "battery_soc": random.uniform(50, 100),
                "fuel_consumption": random.uniform(3, 20),
            })
        time.sleep(1)
```

---

## 14. Kafka con FastAPI

```python
"""
API REST que recibe telemetria via HTTP y la publica en Kafka.
Util cuando los dispositivos no pueden conectarse a Kafka directamente.
"""
from fastapi import FastAPI
from pydantic import BaseModel
from kafka import KafkaProducer
import json

app = FastAPI()

# Productor Kafka (singleton, se reutiliza)
producer = KafkaProducer(
    bootstrap_servers=['localhost:9092'],
    value_serializer=lambda v: json.dumps(v).encode('utf-8'),
    key_serializer=lambda k: k.encode('utf-8')
)


class TelemetryData(BaseModel):
    vehicle_id: str
    speed_kmh: float
    battery_temp: float
    battery_soc: float
    fuel_consumption: float
    gps_lat: float
    gps_lon: float


@app.post("/api/telemetry")
async def receive_telemetry(data: TelemetryData):
    """Endpoint que recibe telemetria y la publica en Kafka."""
    producer.send(
        topic='telemetria-raw',
        key=data.vehicle_id,
        value=data.model_dump()
    )
    return {"status": "ok", "vehicle_id": data.vehicle_id}


@app.on_event("shutdown")
def shutdown():
    producer.flush()
    producer.close()


# Ejecutar: uvicorn main:app --host 0.0.0.0 --port 8000
# Probar:   curl -X POST http://localhost:8000/api/telemetry \
#             -H "Content-Type: application/json" \
#             -d '{"vehicle_id":"V001","speed_kmh":85,...}'
```

---

## 15. Docker Compose para desarrollo

```yaml
# docker-compose.yml
# Levantar Kafka en local para desarrollo

version: '3.8'
services:
  zookeeper:
    image: confluentinc/cp-zookeeper:7.5.0
    environment:
      ZOOKEEPER_CLIENT_PORT: 2181
    ports:
      - "2181:2181"

  kafka:
    image: confluentinc/cp-kafka:7.5.0
    depends_on:
      - zookeeper
    ports:
      - "9092:9092"
    environment:
      KAFKA_BROKER_ID: 1
      KAFKA_ZOOKEEPER_CONNECT: zookeeper:2181
      KAFKA_ADVERTISED_LISTENERS: PLAINTEXT://localhost:9092
      KAFKA_OFFSETS_TOPIC_REPLICATION_FACTOR: 1
      KAFKA_AUTO_CREATE_TOPICS_ENABLE: "true"
      KAFKA_LOG_RETENTION_HOURS: 168  # 7 dias

  # UI para visualizar topics y mensajes (opcional pero muy util)
  kafka-ui:
    image: provectuslabs/kafka-ui
    depends_on:
      - kafka
    ports:
      - "8080:8080"
    environment:
      KAFKA_CLUSTERS_0_NAME: local
      KAFKA_CLUSTERS_0_BOOTSTRAPSERVERS: kafka:9092

# Uso:
#   docker-compose up -d
#   Kafka disponible en localhost:9092
#   UI disponible en http://localhost:8080
#
#   docker-compose down    # parar
#   docker-compose down -v # parar y borrar datos
```
