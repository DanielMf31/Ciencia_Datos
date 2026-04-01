"""
CONSUMER: Lee mensajes de Kafka, los cuenta, y expone metricas para Prometheus.

Tambien guarda el conteo en PostgreSQL para que Airflow pueda consultarlo.
Expone /metrics en el puerto 8001 para que Prometheus haga scrape.
"""
import json
import time
import logging
import threading
from datetime import datetime, timezone
from http.server import HTTPServer, BaseHTTPRequestHandler

import psycopg2
from kafka import KafkaConsumer

# Logging estructurado
logging.basicConfig(
    level=logging.INFO,
    format='{"time":"%(asctime)s","level":"%(levelname)s","service":"consumer","message":"%(message)s"}'
)
log = logging.getLogger("consumer")


# =============================================
# Metricas (contadores para Prometheus)
# =============================================
class Metrics:
    def __init__(self):
        self.messages_total = 0
        self.messages_by_sensor = {"temperatura": 0, "velocidad": 0, "presion": 0}
        self.last_message_time = ""
        self.errors_total = 0

    def to_prometheus(self):
        """Formato que Prometheus entiende (/metrics endpoint)."""
        lines = []
        lines.append("# HELP messages_processed_total Total de mensajes procesados")
        lines.append("# TYPE messages_processed_total counter")
        lines.append(f"messages_processed_total {self.messages_total}")

        lines.append("# HELP messages_by_sensor Mensajes por tipo de sensor")
        lines.append("# TYPE messages_by_sensor counter")
        for sensor, count in self.messages_by_sensor.items():
            lines.append(f'messages_by_sensor{{sensor="{sensor}"}} {count}')

        lines.append("# HELP consumer_errors_total Total de errores")
        lines.append("# TYPE consumer_errors_total counter")
        lines.append(f"consumer_errors_total {self.errors_total}")

        lines.append("# HELP consumer_up Consumer esta vivo")
        lines.append("# TYPE consumer_up gauge")
        lines.append("consumer_up 1")

        return "\n".join(lines) + "\n"


metrics = Metrics()


# =============================================
# Servidor HTTP para /metrics (Prometheus lo scrapeara)
# =============================================
class MetricsHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/metrics":
            body = metrics.to_prometheus().encode()
            self.send_response(200)
            self.send_header("Content-Type", "text/plain; version=0.0.4")
            self.end_headers()
            self.wfile.write(body)
        elif self.path == "/health":
            self.send_response(200)
            self.end_headers()
            self.wfile.write(b'{"status":"ok"}')
        else:
            self.send_response(404)
            self.end_headers()

    def log_message(self, format, *args):
        pass  # silenciar logs del HTTP server


def start_metrics_server():
    server = HTTPServer(("0.0.0.0", 8001), MetricsHandler)
    log.info("Servidor de metricas escuchando en :8001/metrics")
    server.serve_forever()


# =============================================
# PostgreSQL: guardar conteo
# =============================================
def get_db_connection(retries=30):
    for attempt in range(retries):
        try:
            conn = psycopg2.connect(
                host="postgres",
                database="demo",
                user="demo",
                password="demo"
            )
            return conn
        except Exception as e:
            log.warning(f"PostgreSQL no disponible (intento {attempt+1}): {e}")
            time.sleep(2)
    raise ConnectionError("No se pudo conectar a PostgreSQL")


def init_db(conn):
    with conn.cursor() as cur:
        cur.execute("""
            CREATE TABLE IF NOT EXISTS message_counts (
                id SERIAL PRIMARY KEY,
                sensor VARCHAR(50),
                count INTEGER DEFAULT 0,
                last_updated TIMESTAMP DEFAULT NOW()
            )
        """)
        # Insertar filas iniciales si no existen
        for sensor in ["temperatura", "velocidad", "presion"]:
            cur.execute(
                "INSERT INTO message_counts (sensor, count) "
                "SELECT %s, 0 WHERE NOT EXISTS "
                "(SELECT 1 FROM message_counts WHERE sensor = %s)",
                (sensor, sensor)
            )
    conn.commit()
    log.info("Base de datos inicializada")


def update_db(conn, sensor):
    with conn.cursor() as cur:
        cur.execute(
            "UPDATE message_counts SET count = count + 1, last_updated = NOW() "
            "WHERE sensor = %s",
            (sensor,)
        )
    conn.commit()


# =============================================
# Consumer Kafka
# =============================================
def create_consumer(retries=30):
    for attempt in range(retries):
        try:
            consumer = KafkaConsumer(
                "eventos",
                bootstrap_servers=["kafka:9092"],
                group_id="consumer-demo",
                value_deserializer=lambda v: json.loads(v.decode("utf-8")),
                auto_offset_reset="earliest",
            )
            log.info("Conectado a Kafka")
            return consumer
        except Exception as e:
            log.warning(f"Kafka no disponible (intento {attempt+1}): {e}")
            time.sleep(2)
    raise ConnectionError("No se pudo conectar a Kafka")


def main():
    # Arrancar servidor de metricas en un thread aparte
    metrics_thread = threading.Thread(target=start_metrics_server, daemon=True)
    metrics_thread.start()

    # Conectar a PostgreSQL
    conn = get_db_connection()
    init_db(conn)

    # Conectar a Kafka
    consumer = create_consumer()

    log.info("Esperando mensajes de Kafka...")

    for message in consumer:
        try:
            data = message.value
            sensor = data.get("sensor", "desconocido")

            # Actualizar metricas en memoria (para Prometheus)
            metrics.messages_total += 1
            if sensor in metrics.messages_by_sensor:
                metrics.messages_by_sensor[sensor] += 1
            metrics.last_message_time = data.get("timestamp", "")

            # Guardar en PostgreSQL
            update_db(conn, sensor)

            log.info(
                f"Procesado #{data['id']}: {sensor}={data['value']} "
                f"(total: {metrics.messages_total})"
            )

        except Exception as e:
            metrics.errors_total += 1
            log.error(f"Error procesando mensaje: {e}")


if __name__ == "__main__":
    main()
