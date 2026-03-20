# Loki + Promtail - Guia de Referencia

## Indice

1. [Que es Loki y como funciona](#1-que-es-loki)
2. [Arquitectura: Loki vs ELK](#2-arquitectura-loki-vs-elk)
3. [Promtail: recoleccion de logs](#3-promtail)
4. [Structured logging en Python](#4-structured-logging-en-python)
5. [LogQL: consultas de logs](#5-logql-consultas-de-logs)
6. [Logs en FastAPI con contexto ML](#6-logs-en-fastapi-con-contexto-ml)
7. [Correlacion logs + metricas en Grafana](#7-correlacion-logs-metricas)
8. [Enviar logs directamente desde Python](#8-enviar-logs-desde-python)
9. [Ejemplo real: pipeline de telemetria](#9-ejemplo-real-pipeline-telemetria)
10. [Docker Compose con Loki](#10-docker-compose-con-loki)

---

## 1. Que es Loki

Loki es un **sistema de logs** disenado para ser el complemento de Prometheus:
- **Prometheus** almacena **numeros** (metricas)
- **Loki** almacena **texto** (logs)
- **Grafana** visualiza ambos en el mismo dashboard

```
Diferencia clave con ELK (Elasticsearch):
  ELK:  indexa TODO el contenido del log (potente pero costoso en recursos)
  Loki: solo indexa las LABELS, no el contenido (ligero y barato)

Ejemplo:
  Log: "2025-01-15 14:23:01 ERROR vehicle V032 battery_temp 48.5 exceeds threshold"

  ELK indexa:  cada palabra ("vehicle", "V032", "battery_temp", "48.5", "threshold"...)
  Loki indexa: solo labels {app="api", level="error"} y guarda el texto sin indexar

  Para buscar en Loki usas: {app="api"} |= "V032"
  Loki filtra por label (rapido) y luego busca en el texto (secuencial pero OK)
```

---

## 2. Arquitectura: Loki vs ELK

```
ELK Stack (pesado):
  App -> Logstash (procesar) -> Elasticsearch (indexar TODO) -> Kibana (visualizar)
  RAM: Elasticsearch necesita 4-8GB minimo
  Disco: indexa todo = mucho espacio

Loki Stack (ligero):
  App -> Promtail (recolectar) -> Loki (solo indexar labels) -> Grafana (visualizar)
  RAM: Loki funciona con 256MB-1GB
  Disco: mucho menos que ELK

Cuando usar cada uno:
  ELK:  necesitas busqueda full-text avanzada (como Google pero para logs)
  Loki: quieres logs integrados con Prometheus/Grafana (90% de los casos)
```

---

## 3. Promtail

Promtail es el **agente** que recolecta logs y los envia a Loki.
Se instala en cada servidor/contenedor que genera logs.

```yaml
# promtail-config.yml
server:
  http_listen_port: 9080

positions:
  filename: /tmp/positions.yaml  # recuerda donde se quedo leyendo

clients:
  - url: http://loki:3100/loki/api/v1/push  # a donde enviar

scrape_configs:
  # Recolectar logs de archivos
  - job_name: api-logs
    static_configs:
      - targets:
          - localhost
        labels:
          app: api-prediccion
          environment: production
          __path__: /var/log/api/*.log  # que archivos leer

  # Recolectar logs de Docker automaticamente
  - job_name: docker
    docker_sd_configs:
      - host: unix:///var/run/docker.sock
    relabel_configs:
      - source_labels: ['__meta_docker_container_name']
        target_label: 'container'

  # Pipeline: parsear y enriquecer logs
  - job_name: api-structured
    static_configs:
      - targets: [localhost]
        labels:
          app: api-prediccion
          __path__: /var/log/api/structured.log
    pipeline_stages:
      # Parsear JSON
      - json:
          expressions:
            level: level
            vehicle_id: vehicle_id
            latency: latency_ms
      # Usar campos parseados como labels
      - labels:
          level:
          vehicle_id:
      # Filtrar: solo enviar errores y warnings
      - match:
          selector: '{level=~"error|warning"}'
          action: keep
```

---

## 4. Structured logging en Python

```python
"""
Logging estructurado: logs en formato JSON para que Loki/Promtail
pueda parsear campos automaticamente.
"""
import logging
import json
from datetime import datetime


# =============================================
# Opcion 1: Formato JSON basico (manual)
# =============================================

class JSONFormatter(logging.Formatter):
    """Formatea logs como JSON para facilitar parseo en Loki."""

    def format(self, record):
        log_entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": record.levelname,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }

        # Incluir campos extra si existen
        if hasattr(record, 'vehicle_id'):
            log_entry['vehicle_id'] = record.vehicle_id
        if hasattr(record, 'latency_ms'):
            log_entry['latency_ms'] = record.latency_ms
        if hasattr(record, 'prediction'):
            log_entry['prediction'] = record.prediction

        # Incluir traceback si hay excepcion
        if record.exc_info:
            log_entry['exception'] = self.formatException(record.exc_info)

        return json.dumps(log_entry)


# Configurar logger
logger = logging.getLogger("api")
handler = logging.StreamHandler()  # o FileHandler para archivo
handler.setFormatter(JSONFormatter())
logger.addHandler(handler)
logger.setLevel(logging.INFO)

# Uso
logger.info("Prediccion realizada",
            extra={"vehicle_id": "V032", "prediction": 12.5, "latency_ms": 23})

# Output:
# {"timestamp": "2025-01-15T14:23:01", "level": "INFO",
#  "message": "Prediccion realizada", "module": "api", "function": "predict",
#  "line": 45, "vehicle_id": "V032", "prediction": 12.5, "latency_ms": 23}


# =============================================
# Opcion 2: structlog (libreria recomendada)
# =============================================

# pip install structlog

import structlog

# Configurar structlog
structlog.configure(
    processors=[
        structlog.stdlib.add_log_level,        # anadir level
        structlog.processors.TimeStamper(fmt="iso"), # anadir timestamp
        structlog.processors.JSONRenderer()     # output JSON
    ],
    wrapper_class=structlog.stdlib.BoundLogger,
    logger_factory=structlog.PrintLoggerFactory(),
)

log = structlog.get_logger()

# Uso basico
log.info("servidor iniciado", port=8000, model_version="v2.3")
# {"event": "servidor iniciado", "port": 8000, "model_version": "v2.3",
#  "level": "info", "timestamp": "2025-01-15T14:23:01"}

# Bind: anadir contexto persistente
log = log.bind(service="api-prediccion", environment="production")

# Ahora todos los logs incluyen service y environment automaticamente
log.info("prediccion", vehicle_id="V032", result=12.5)
# {"event": "prediccion", "vehicle_id": "V032", "result": 12.5,
#  "service": "api-prediccion", "environment": "production", ...}

log.error("fallo prediccion", vehicle_id="V032", error="model not loaded")
# {"event": "fallo prediccion", "vehicle_id": "V032", "error": "model not loaded",
#  "service": "api-prediccion", "environment": "production", ...}
```

---

## 5. LogQL: consultas de logs

```logql
# LogQL es el lenguaje de consulta de Loki
# Similar a PromQL pero para logs

# =============================================
# Filtros basicos por labels
# =============================================

# Todos los logs de la API
{app="api-prediccion"}

# Solo errores
{app="api-prediccion", level="error"}

# Logs de un vehiculo especifico
{app="api-prediccion", vehicle_id="V032"}

# Regex en labels
{app=~"api-.*"}                        # todos los servicios api-*
{level=~"error|warning"}               # errores y warnings


# =============================================
# Filtros de contenido (texto del log)
# =============================================

# Buscar texto exacto
{app="api-prediccion"} |= "battery_temp"

# Buscar texto (case insensitive)
{app="api-prediccion"} |~ "(?i)error"

# Excluir texto
{app="api-prediccion"} != "health"     # excluir health checks

# Combinar filtros
{app="api-prediccion"} |= "V032" |= "battery"
{app="api-prediccion"} |= "ERROR" != "timeout"


# =============================================
# Parsear JSON en los logs
# =============================================

# Si tus logs son JSON (recomendado):
{app="api-prediccion"} | json

# Filtrar por campo parseado
{app="api-prediccion"} | json | latency_ms > 100
{app="api-prediccion"} | json | vehicle_id = "V032"
{app="api-prediccion"} | json | level = "error"

# Formatear output
{app="api-prediccion"} | json | line_format "{{.vehicle_id}}: {{.message}} ({{.latency_ms}}ms)"


# =============================================
# Metricas desde logs (logs -> numeros)
# =============================================

# Contar logs por segundo (como rate() en PromQL)
rate({app="api-prediccion"}[5m])

# Contar errores por segundo
rate({app="api-prediccion", level="error"}[5m])

# Contar logs que mencionan un vehiculo
count_over_time({app="api-prediccion"} |= "V032" [1h])

# Extraer valores numericos y calcular estadisticas
# Latencia media de los logs JSON
avg_over_time({app="api-prediccion"} | json | unwrap latency_ms [5m])

# Percentil 99 de latencia desde logs
quantile_over_time(0.99, {app="api-prediccion"} | json | unwrap latency_ms [5m])

# Top vehiculos con mas errores
topk(5, count_over_time({app="api-prediccion", level="error"} | json [1h]) by (vehicle_id))

# Tasa de errores vs total (porcentaje)
sum(rate({app="api-prediccion", level="error"}[5m]))
/
sum(rate({app="api-prediccion"}[5m]))
* 100
```

---

## 6. Logs en FastAPI con contexto ML

```python
"""
Logging completo para una API de ML con contexto enriquecido.
"""
import structlog
import time
import uuid
from fastapi import FastAPI, Request
from contextvars import ContextVar

app = FastAPI()

# Variable de contexto para request_id (unico por peticion)
request_id_var: ContextVar[str] = ContextVar("request_id", default="")

# Configurar structlog
structlog.configure(
    processors=[
        structlog.stdlib.add_log_level,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.JSONRenderer()
    ],
    logger_factory=structlog.PrintLoggerFactory(),
)

log = structlog.get_logger()


@app.middleware("http")
async def logging_middleware(request: Request, call_next):
    """Middleware que loguea cada peticion con contexto."""
    # Generar ID unico para esta peticion
    req_id = str(uuid.uuid4())[:8]
    request_id_var.set(req_id)
    start = time.time()

    # Log de entrada
    log.info("request_start",
             request_id=req_id,
             method=request.method,
             path=request.url.path,
             client_ip=request.client.host)

    response = await call_next(request)

    # Log de salida
    duration_ms = (time.time() - start) * 1000
    log.info("request_end",
             request_id=req_id,
             method=request.method,
             path=request.url.path,
             status_code=response.status_code,
             duration_ms=round(duration_ms, 2))

    return response


@app.post("/predict")
async def predict(data: dict):
    req_id = request_id_var.get()

    log.info("prediction_start",
             request_id=req_id,
             vehicle_id=data.get("vehicle_id"),
             vehicle_type=data.get("vehicle_type"),
             features_count=len(data))

    try:
        # Simular prediccion
        start = time.time()
        prediction = 12.5  # model.predict(...)
        latency = (time.time() - start) * 1000

        log.info("prediction_success",
                 request_id=req_id,
                 vehicle_id=data.get("vehicle_id"),
                 prediction=prediction,
                 latency_ms=round(latency, 2))

        return {"prediction": prediction}

    except Exception as e:
        log.error("prediction_error",
                  request_id=req_id,
                  vehicle_id=data.get("vehicle_id"),
                  error=str(e),
                  error_type=type(e).__name__)
        raise


# Logs generados:
#
# {"event": "request_start", "request_id": "a1b2c3d4",
#  "method": "POST", "path": "/predict", "client_ip": "10.0.0.5", ...}
#
# {"event": "prediction_start", "request_id": "a1b2c3d4",
#  "vehicle_id": "V032", "vehicle_type": "electrico", "features_count": 7, ...}
#
# {"event": "prediction_success", "request_id": "a1b2c3d4",
#  "vehicle_id": "V032", "prediction": 12.5, "latency_ms": 23.4, ...}
#
# {"event": "request_end", "request_id": "a1b2c3d4",
#  "method": "POST", "path": "/predict", "status_code": 200, "duration_ms": 25.1, ...}
#
# Todos los logs de la misma peticion comparten request_id="a1b2c3d4"
# -> en Grafana/Loki puedes buscar {app="api"} | json | request_id = "a1b2c3d4"
#    y ver todo el ciclo de vida de esa peticion
```

---

## 7. Correlacion logs + metricas en Grafana

```
En Grafana puedes tener:

Panel 1 (Prometheus): grafico de latencia
Panel 2 (Loki): logs filtrados

Cuando haces clic en un pico de latencia en Panel 1:
  -> Grafana automaticamente filtra Panel 2 al mismo rango de tiempo
  -> Ves los logs de ese momento exacto

Configuracion en Grafana:
  1. Data Sources -> Add Loki (http://loki:3100)
  2. Data Sources -> Add Prometheus (http://prometheus:9090)
  3. En Prometheus data source -> Derived Fields:
     - Name: "TraceID"
     - Regex: "request_id=(\w+)"
     - Internal Link: Loki
     - Query: {app="api"} | json | request_id = "${__value.raw}"

Ahora al hacer clic en un request_id en un log,
Grafana te muestra todos los logs relacionados.
```

---

## 8. Enviar logs directamente desde Python

```python
"""
Enviar logs directamente a Loki sin Promtail.
Util para scripts, notebooks, o jobs de Airflow.
"""
import requests
import json
import time


class LokiHandler:
    """Handler que envia logs directamente a Loki via HTTP."""

    def __init__(self, loki_url="http://localhost:3100", labels=None):
        self.url = f"{loki_url}/loki/api/v1/push"
        self.labels = labels or {"app": "python-script"}

    def send(self, message: str, level: str = "info", extra_labels: dict = None):
        """Enviar un log a Loki."""
        labels = {**self.labels, "level": level}
        if extra_labels:
            labels.update(extra_labels)

        # Formato de labels: {key="value", key2="value2"}
        labels_str = ", ".join(f'{k}="{v}"' for k, v in labels.items())

        payload = {
            "streams": [
                {
                    "stream": labels,
                    "values": [
                        # [timestamp_nanoseconds, log_line]
                        [str(int(time.time() * 1e9)), message]
                    ]
                }
            ]
        }

        requests.post(
            self.url,
            json=payload,
            headers={"Content-Type": "application/json"}
        )

    def info(self, message, **kwargs):
        self.send(json.dumps({"event": message, **kwargs}), level="info")

    def error(self, message, **kwargs):
        self.send(json.dumps({"event": message, **kwargs}), level="error")

    def warning(self, message, **kwargs):
        self.send(json.dumps({"event": message, **kwargs}), level="warning")


# --- Uso ---

loki = LokiHandler(
    loki_url="http://localhost:3100",
    labels={"app": "airflow-pipeline", "dag": "telemetria_diaria"}
)

# En tu DAG de Airflow o script:
loki.info("Pipeline iniciado", fecha="2025-01-15")
loki.info("Datos cargados", registros=15000, vehiculos=48)
loki.warning("Data drift detectado", feature="battery_temp", p_value=0.003)
loki.info("Pipeline completado", duracion_min=12.5)

# En Grafana/Loki:
# {app="airflow-pipeline", dag="telemetria_diaria"} | json
```

---

## 9. Ejemplo real: pipeline de telemetria

```python
"""
Ejemplo completo: script ETL con logging a Loki
para poder monitorear el pipeline desde Grafana.
"""
import structlog
import time
import pandas as pd

# Configurar logging (JSON a stdout, Promtail lo envia a Loki)
structlog.configure(
    processors=[
        structlog.stdlib.add_log_level,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.JSONRenderer()
    ],
    logger_factory=structlog.PrintLoggerFactory(),
)

log = structlog.get_logger().bind(
    pipeline="telemetria_diaria",
    run_id="20250115_030000"
)


def pipeline_diario(fecha: str):
    """Pipeline ETL con logging completo."""

    # --- Paso 1: Extraer ---
    log.info("step_start", step="extraer", fecha=fecha)
    start = time.time()

    try:
        # df = pd.read_sql(f"SELECT * FROM raw WHERE date='{fecha}'", engine)
        n_registros = 150000  # simulado

        log.info("step_complete",
                 step="extraer",
                 registros=n_registros,
                 duracion_s=round(time.time() - start, 2))

    except Exception as e:
        log.error("step_failed",
                  step="extraer",
                  error=str(e),
                  error_type=type(e).__name__)
        raise

    # --- Paso 2: Limpiar ---
    log.info("step_start", step="limpiar")
    start = time.time()

    nulos_antes = 1200  # simulado
    nulos_despues = 0
    outliers_removidos = 350

    log.info("step_complete",
             step="limpiar",
             nulos_eliminados=nulos_antes - nulos_despues,
             outliers_removidos=outliers_removidos,
             registros_restantes=n_registros - outliers_removidos,
             duracion_s=round(time.time() - start, 2))

    # --- Paso 3: Detectar anomalias ---
    log.info("step_start", step="anomalias")
    start = time.time()

    anomalias = [
        {"vehicle_id": "V032", "tipo": "TEMP_ALTA", "valor": 48.5},
        {"vehicle_id": "V017", "tipo": "CONSUMO_ALTO", "valor": 18.2},
    ]

    for a in anomalias:
        log.warning("anomalia_detectada",
                    step="anomalias",
                    vehicle_id=a["vehicle_id"],
                    tipo=a["tipo"],
                    valor=a["valor"])

    log.info("step_complete",
             step="anomalias",
             total_anomalias=len(anomalias),
             duracion_s=round(time.time() - start, 2))

    # --- Paso 4: Evaluar modelo ---
    log.info("step_start", step="evaluar_modelo")
    r2 = 0.82

    if r2 < 0.85:
        log.warning("model_degradation",
                    step="evaluar_modelo",
                    r2_actual=r2,
                    r2_umbral=0.85,
                    recomendacion="reentrenar")
    else:
        log.info("model_ok", step="evaluar_modelo", r2=r2)

    # --- Resumen ---
    log.info("pipeline_complete",
             fecha=fecha,
             registros_procesados=n_registros - outliers_removidos,
             anomalias=len(anomalias),
             model_r2=r2)


if __name__ == "__main__":
    pipeline_diario("2025-01-15")

# En Grafana con Loki puedes:
#   {pipeline="telemetria_diaria"} | json                          # todos los logs
#   {pipeline="telemetria_diaria"} | json | step = "anomalias"     # solo anomalias
#   {pipeline="telemetria_diaria"} | json | level = "warning"      # warnings
#   count_over_time({pipeline="telemetria_diaria", level="error"} [24h])  # errores/dia
```

---

## 10. Docker Compose con Loki

```yaml
# docker-compose.yml
# Stack completo: Loki + Promtail + Grafana

version: '3.8'

services:
  # Loki: almacena logs
  loki:
    image: grafana/loki:2.9.0
    ports:
      - "3100:3100"
    volumes:
      - ./monitoring/loki-config.yml:/etc/loki/local-config.yaml
      - loki_data:/loki
    command: -config.file=/etc/loki/local-config.yaml

  # Promtail: recolecta logs y los envia a Loki
  promtail:
    image: grafana/promtail:2.9.0
    volumes:
      - ./monitoring/promtail-config.yml:/etc/promtail/config.yml
      - /var/log:/var/log                    # logs del sistema
      - /var/lib/docker/containers:/var/lib/docker/containers:ro  # logs Docker
    command: -config.file=/etc/promtail/config.yml

  # Grafana: visualiza (conecta a Prometheus Y Loki)
  grafana:
    image: grafana/grafana:10.2.0
    ports:
      - "3000:3000"
    environment:
      GF_SECURITY_ADMIN_PASSWORD: admin
    volumes:
      - grafana_data:/var/lib/grafana

volumes:
  loki_data:
  grafana_data:
```

```yaml
# monitoring/loki-config.yml
auth_enabled: false

server:
  http_listen_port: 3100

common:
  ring:
    instance_addr: 127.0.0.1
    kvstore:
      store: inmemory
  replication_factor: 1
  path_prefix: /loki

schema_config:
  configs:
    - from: 2020-10-24
      store: tsdb
      object_store: filesystem
      schema: v12
      index:
        prefix: index_
        period: 24h

storage_config:
  filesystem:
    directory: /loki/chunks

limits_config:
  retention_period: 720h  # 30 dias
```
