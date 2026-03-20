# Prometheus + Grafana - Guia de Referencia

## Indice

1. [Que son y como se relacionan](#1-que-son-y-como-se-relacionan)
2. [Conceptos clave de Prometheus](#2-conceptos-clave-de-prometheus)
3. [Tipos de metricas](#3-tipos-de-metricas)
4. [Instrumentar una API con Python](#4-instrumentar-una-api-con-python)
5. [Metricas custom para ML](#5-metricas-custom-para-ml)
6. [PromQL: consultas de metricas](#6-promql-consultas-de-metricas)
7. [Alertas con Prometheus](#7-alertas-con-prometheus)
8. [Grafana: dashboards](#8-grafana-dashboards)
9. [Ejemplo real: monitoreo de API de prediccion](#9-ejemplo-real-api-de-prediccion)
10. [Ejemplo real: monitoreo de modelo ML](#10-ejemplo-real-monitoreo-de-modelo-ml)
11. [Docker Compose completo](#11-docker-compose-completo)

---

## 1. Que son y como se relacionan

```
Tu aplicacion                Prometheus              Grafana
(expone metricas)     (recolecta y almacena)    (visualiza dashboards)

  /metrics ────────> scrape cada 15s ────────> queries PromQL
                     almacena en TSDB          graficos en tiempo real
                     evalua alertas            alertas visuales
```

- **Prometheus**: base de datos de series temporales. Recolecta numeros a lo largo del tiempo.
- **Grafana**: dashboard web. Lee de Prometheus (y otras fuentes) y dibuja graficos.
- Son **independientes**: puedes usar Prometheus sin Grafana (tiene UI basica) o Grafana sin Prometheus (conecta a otras DBs).

---

## 2. Conceptos clave de Prometheus

| Concepto | Que es | Ejemplo |
|----------|--------|---------|
| **Metric** | Un valor numerico con nombre | `http_requests_total` |
| **Label** | Etiqueta que da contexto | `method="POST"`, `endpoint="/predict"` |
| **Scrape** | Prometheus visita /metrics y recoge datos | Cada 15 segundos |
| **Target** | Servicio que Prometheus monitorea | `api-prediccion:8000` |
| **TSDB** | Base de datos de series temporales | Almacena valor + timestamp |
| **PromQL** | Lenguaje de consulta de Prometheus | `rate(requests[5m])` |

```
Una metrica con labels:

http_requests_total{method="GET", endpoint="/predict", status="200"} = 4523
http_requests_total{method="GET", endpoint="/predict", status="500"} = 12
http_requests_total{method="POST", endpoint="/train", status="200"} = 3

Cada combinacion unica de labels es una "serie temporal" independiente.
```

---

## 3. Tipos de metricas

```python
from prometheus_client import Counter, Gauge, Histogram, Summary

# =============================================
# COUNTER: solo sube (nunca baja)
# Uso: contar eventos (peticiones, errores, mensajes procesados)
# =============================================
requests_total = Counter(
    'api_requests_total',           # nombre
    'Total de peticiones HTTP',     # descripcion
    ['method', 'endpoint', 'status'] # labels
)

# Incrementar
requests_total.labels(method='GET', endpoint='/predict', status='200').inc()
requests_total.labels(method='GET', endpoint='/predict', status='500').inc()


# =============================================
# GAUGE: sube y baja (valor actual)
# Uso: valores que fluctuan (temperatura, RAM, modelos cargados)
# =============================================
active_vehicles = Gauge(
    'fleet_active_vehicles',
    'Vehiculos activos en este momento'
)

active_vehicles.set(48)      # establecer valor
active_vehicles.inc()        # +1 = 49
active_vehicles.dec(3)       # -3 = 46

# Gauge con labels
battery_temp = Gauge(
    'vehicle_battery_temp_celsius',
    'Temperatura de bateria por vehiculo',
    ['vehicle_id', 'vehicle_type']
)
battery_temp.labels(vehicle_id='V001', vehicle_type='electrico').set(35.2)
battery_temp.labels(vehicle_id='V002', vehicle_type='gasolina').set(42.1)


# =============================================
# HISTOGRAM: mide distribucion de valores
# Uso: latencias, tamanios, duraciones
# =============================================
prediction_latency = Histogram(
    'prediction_latency_seconds',
    'Latencia de prediccion',
    ['model_name'],
    buckets=[0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0]
    # Cuenta cuantas peticiones caen en cada rango:
    # [0-5ms, 5-10ms, 10-25ms, 25-50ms, 50-100ms, 100-250ms, 250-500ms, 500-1000ms]
)

# Medir latencia automaticamente
with prediction_latency.labels(model_name='consumption').time():
    result = model.predict(data)  # mide cuanto tarda esto

# O manualmente
prediction_latency.labels(model_name='consumption').observe(0.023)  # 23ms


# =============================================
# SUMMARY: similar a Histogram pero calcula percentiles en el cliente
# Uso: cuando necesitas percentiles exactos (no aproximados)
# =============================================
request_size = Summary(
    'request_size_bytes',
    'Tamano de peticiones en bytes'
)
request_size.observe(1024)
```

---

## 4. Instrumentar una API con Python

```python
"""
API FastAPI con metricas Prometheus integradas.
"""
from fastapi import FastAPI, Request, Response
from prometheus_client import (
    Counter, Histogram, Gauge, Info,
    generate_latest, CONTENT_TYPE_LATEST
)
import time

app = FastAPI()

# --- Definir metricas ---

# Peticiones totales por endpoint y status
REQUEST_COUNT = Counter(
    'http_requests_total',
    'Total HTTP requests',
    ['method', 'endpoint', 'status_code']
)

# Latencia por endpoint
REQUEST_LATENCY = Histogram(
    'http_request_duration_seconds',
    'HTTP request latency',
    ['method', 'endpoint'],
    buckets=[0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5]
)

# Peticiones en curso (concurrencia)
IN_PROGRESS = Gauge(
    'http_requests_in_progress',
    'HTTP requests currently being processed',
    ['endpoint']
)

# Info del servicio (version, etc.)
APP_INFO = Info('api_prediccion', 'Informacion del servicio')
APP_INFO.info({
    'version': '2.3.0',
    'model_version': 'consumption_v5',
    'environment': 'production'
})


# --- Middleware para capturar metricas automaticamente ---

@app.middleware("http")
async def metrics_middleware(request: Request, call_next):
    endpoint = request.url.path
    method = request.method

    # Incrementar peticiones en curso
    IN_PROGRESS.labels(endpoint=endpoint).inc()
    start_time = time.time()

    # Procesar peticion
    response = await call_next(request)

    # Registrar metricas
    duration = time.time() - start_time
    REQUEST_COUNT.labels(
        method=method,
        endpoint=endpoint,
        status_code=response.status_code
    ).inc()
    REQUEST_LATENCY.labels(
        method=method,
        endpoint=endpoint
    ).observe(duration)
    IN_PROGRESS.labels(endpoint=endpoint).dec()

    return response


# --- Endpoint /metrics para Prometheus ---

@app.get("/metrics")
async def metrics():
    """Prometheus scrapes este endpoint cada 15 segundos."""
    return Response(
        content=generate_latest(),
        media_type=CONTENT_TYPE_LATEST
    )


# --- Tus endpoints normales ---

@app.get("/health")
async def health():
    return {"status": "ok"}

@app.post("/predict")
async def predict(data: dict):
    # tu logica...
    return {"prediction": 8.5}


# Al visitar /metrics veras algo como:
#
# # HELP http_requests_total Total HTTP requests
# # TYPE http_requests_total counter
# http_requests_total{method="POST",endpoint="/predict",status_code="200"} 4523
# http_requests_total{method="GET",endpoint="/health",status_code="200"} 891
#
# # HELP http_request_duration_seconds HTTP request latency
# # TYPE http_request_duration_seconds histogram
# http_request_duration_seconds_bucket{method="POST",endpoint="/predict",le="0.01"} 3200
# http_request_duration_seconds_bucket{method="POST",endpoint="/predict",le="0.025"} 4100
# ...
```

---

## 5. Metricas custom para ML

```python
from prometheus_client import Counter, Gauge, Histogram

# =============================================
# Metricas del MODELO
# =============================================

# Predicciones por tipo de vehiculo
PREDICTIONS_BY_TYPE = Counter(
    'model_predictions_total',
    'Predicciones realizadas',
    ['model_name', 'vehicle_type']
)

# Valor de la prediccion (para detectar drift)
PREDICTION_VALUE = Histogram(
    'model_prediction_value',
    'Distribucion de valores predichos',
    ['model_name'],
    buckets=[2, 4, 6, 8, 10, 12, 14, 16, 18, 20, 25, 30]
)

# Rendimiento del modelo (actualizado periodicamente)
MODEL_R2 = Gauge(
    'model_r2_score',
    'R2 score del modelo en produccion',
    ['model_name']
)

MODEL_RMSE = Gauge(
    'model_rmse',
    'RMSE del modelo en produccion',
    ['model_name']
)

# Drift detectado
DRIFT_DETECTED = Gauge(
    'model_data_drift_detected',
    'Si hay data drift (1) o no (0)',
    ['feature']
)

# Version del modelo
MODEL_VERSION = Gauge(
    'model_version_timestamp',
    'Timestamp de cuando se entreno el modelo',
    ['model_name']
)


# =============================================
# Uso en la API
# =============================================

@app.post("/predict")
async def predict(data: TelemetryInput):
    # Hacer prediccion
    prediction = model.predict([data.features])
    value = prediction[0]

    # Registrar metricas
    PREDICTIONS_BY_TYPE.labels(
        model_name='consumption',
        vehicle_type=data.vehicle_type
    ).inc()

    PREDICTION_VALUE.labels(model_name='consumption').observe(value)

    return {"consumption_predicted": value}


# =============================================
# Tarea periodica: evaluar modelo (cada hora)
# =============================================

def evaluar_modelo_produccion():
    """Se ejecuta via Airflow o un cron job."""
    # Obtener predicciones recientes y compararlas con valores reales
    # r2 = calcular_r2(predicciones, reales)
    # rmse = calcular_rmse(predicciones, reales)
    r2 = 0.87
    rmse = 2.1

    MODEL_R2.labels(model_name='consumption').set(r2)
    MODEL_RMSE.labels(model_name='consumption').set(rmse)

    # Evaluar drift por feature
    # for feature, has_drift in drift_results.items():
    #     DRIFT_DETECTED.labels(feature=feature).set(1 if has_drift else 0)
    DRIFT_DETECTED.labels(feature='battery_temp').set(1)
    DRIFT_DETECTED.labels(feature='speed_kmh').set(0)
```

---

## 6. PromQL: consultas de metricas

```promql
# PromQL es el lenguaje de consulta de Prometheus
# Se usa en Grafana para crear paneles

# --- Consultas basicas ---

# Valor actual de una metrica
http_requests_total

# Filtrar por labels
http_requests_total{endpoint="/predict"}
http_requests_total{status_code="500"}
http_requests_total{method="POST", endpoint="/predict"}

# Regex en labels
http_requests_total{endpoint=~"/predict|/train"}   # predict O train
http_requests_total{endpoint!="/health"}             # todo excepto health


# --- Funciones de rango (sobre ventanas de tiempo) ---

# Tasa de peticiones por segundo (ultimos 5 min)
rate(http_requests_total[5m])

# Tasa de errores por segundo
rate(http_requests_total{status_code="500"}[5m])

# Incremento total en los ultimos 10 minutos
increase(http_requests_total[10m])


# --- Agregaciones ---

# Total de peticiones por endpoint (sumar todos los status_codes)
sum by (endpoint) (rate(http_requests_total[5m]))

# Promedio de latencia por endpoint
avg by (endpoint) (http_request_duration_seconds_sum / http_request_duration_seconds_count)

# Percentil 99 de latencia (usando histogramas)
histogram_quantile(0.99, rate(http_request_duration_seconds_bucket[5m]))

# Percentil 50 (mediana)
histogram_quantile(0.50, rate(http_request_duration_seconds_bucket[5m]))


# --- Ejemplos para ML ---

# Tasa de predicciones por segundo
rate(model_predictions_total[5m])

# Predicciones por tipo de vehiculo
sum by (vehicle_type) (rate(model_predictions_total[5m]))

# R2 del modelo (valor actual)
model_r2_score{model_name="consumption"}

# Alerta: R2 por debajo de umbral
model_r2_score{model_name="consumption"} < 0.80

# Alerta: latencia p99 por encima de 200ms
histogram_quantile(0.99, rate(prediction_latency_seconds_bucket[5m])) > 0.2

# Tasa de errores como porcentaje
rate(http_requests_total{status_code=~"5.."}[5m])
/
rate(http_requests_total[5m])
* 100


# --- Operaciones con tiempo ---

# Diferencia respecto a hace 1 hora
model_r2_score - model_r2_score offset 1h

# Diferencia respecto a hace 1 dia
model_r2_score - model_r2_score offset 1d

# Detectar caida: R2 bajo mas de 0.05 en la ultima hora
(model_r2_score offset 1h) - model_r2_score > 0.05
```

---

## 7. Alertas con Prometheus

```yaml
# alerting_rules.yml
# Reglas de alerta que Prometheus evalua continuamente

groups:
  - name: api_alerts
    rules:
      # Alerta si la API esta caida (no responde hace 2 min)
      - alert: APIDown
        expr: up{job="api-prediccion"} == 0
        for: 2m
        labels:
          severity: critical
        annotations:
          summary: "API de prediccion caida"
          description: "La API no responde desde hace {{ $value }} minutos"

      # Alerta si la latencia p99 supera 500ms
      - alert: HighLatency
        expr: histogram_quantile(0.99, rate(prediction_latency_seconds_bucket[5m])) > 0.5
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "Latencia alta en predicciones"
          description: "p99 = {{ $value }}s (umbral: 0.5s)"

      # Alerta si tasa de errores > 5%
      - alert: HighErrorRate
        expr: >
          rate(http_requests_total{status_code=~"5.."}[5m])
          / rate(http_requests_total[5m]) > 0.05
        for: 5m
        labels:
          severity: critical
        annotations:
          summary: "Tasa de errores alta"

  - name: ml_alerts
    rules:
      # Alerta si el R2 del modelo baja
      - alert: ModelDegradation
        expr: model_r2_score{model_name="consumption"} < 0.80
        for: 30m
        labels:
          severity: warning
        annotations:
          summary: "Modelo de consumo degradado"
          description: "R2 = {{ $value }} (umbral: 0.80). Considerar reentrenamiento."

      # Alerta si hay data drift
      - alert: DataDrift
        expr: model_data_drift_detected == 1
        for: 1h
        labels:
          severity: warning
        annotations:
          summary: "Data drift detectado en {{ $labels.feature }}"

      # Alerta si no hay predicciones (modelo posiblemente roto)
      - alert: NoPredictions
        expr: rate(model_predictions_total[10m]) == 0
        for: 10m
        labels:
          severity: critical
        annotations:
          summary: "Sin predicciones en los ultimos 10 minutos"
```

```yaml
# alertmanager.yml
# Donde enviar las alertas (Slack, email, PagerDuty...)

global:
  slack_api_url: 'https://hooks.slack.com/services/xxx/yyy/zzz'

route:
  group_by: ['severity']
  group_wait: 30s
  group_interval: 5m
  repeat_interval: 4h
  receiver: 'slack-notifications'

  routes:
    # Alertas criticas -> Slack + PagerDuty
    - match:
        severity: critical
      receiver: 'slack-critical'

    # Alertas warning -> solo Slack
    - match:
        severity: warning
      receiver: 'slack-notifications'

receivers:
  - name: 'slack-notifications'
    slack_configs:
      - channel: '#mlops-alertas'
        title: '{{ .GroupLabels.severity | toUpper }}: {{ .CommonAnnotations.summary }}'
        text: '{{ .CommonAnnotations.description }}'

  - name: 'slack-critical'
    slack_configs:
      - channel: '#mlops-urgente'
        title: 'CRITICO: {{ .CommonAnnotations.summary }}'
```

---

## 8. Grafana: dashboards

```
Grafana se configura desde la UI web (http://localhost:3000)
pero tambien puedes definir dashboards como JSON (Infrastructure as Code)
```

```json
{
  "dashboard": {
    "title": "API de Prediccion - Overview",
    "panels": [
      {
        "title": "Peticiones por segundo",
        "type": "timeseries",
        "targets": [
          {
            "expr": "sum(rate(http_requests_total[5m]))",
            "legendFormat": "Total req/s"
          }
        ]
      },
      {
        "title": "Latencia p50/p99",
        "type": "timeseries",
        "targets": [
          {
            "expr": "histogram_quantile(0.50, rate(prediction_latency_seconds_bucket[5m]))",
            "legendFormat": "p50"
          },
          {
            "expr": "histogram_quantile(0.99, rate(prediction_latency_seconds_bucket[5m]))",
            "legendFormat": "p99"
          }
        ]
      },
      {
        "title": "R2 del Modelo",
        "type": "gauge",
        "targets": [
          {
            "expr": "model_r2_score{model_name='consumption'}"
          }
        ],
        "fieldConfig": {
          "defaults": {
            "thresholds": {
              "steps": [
                { "color": "red", "value": 0 },
                { "color": "yellow", "value": 0.75 },
                { "color": "green", "value": 0.85 }
              ]
            },
            "min": 0,
            "max": 1
          }
        }
      },
      {
        "title": "Tasa de Errores (%)",
        "type": "stat",
        "targets": [
          {
            "expr": "rate(http_requests_total{status_code=~'5..'}[5m]) / rate(http_requests_total[5m]) * 100"
          }
        ]
      }
    ]
  }
}
```

```
Tipos de paneles en Grafana:
  - timeseries  : graficos de lineas (metricas a lo largo del tiempo)
  - gauge       : indicador circular (R2 = 0.87)
  - stat        : numero grande (127 req/s)
  - bar gauge   : barras horizontales
  - table       : tabla de datos
  - heatmap     : mapa de calor (latencia por hora)
  - logs        : panel de logs (con Loki)
  - geomap      : mapa geografico (vehiculos en mapa)
  - alert list  : lista de alertas activas

Variables de dashboard (el dropdown del que hablamos):
  - $vehicle_id  : dropdown con query "label_values(vehicle_battery_temp, vehicle_id)"
  - $vehicle_type: dropdown con query "label_values(vehicle_battery_temp, vehicle_type)"
  - $timerange   : selector de rango temporal (built-in)

Todos los paneles usan $vehicle_id en sus queries:
  vehicle_battery_temp{vehicle_id="$vehicle_id"}
  -> al cambiar el dropdown, todos los paneles se actualizan
```

---

## 9. Ejemplo real: API de prediccion monitorizada

```python
"""
API completa de prediccion con metricas Prometheus.
Combina todo lo anterior en un servicio listo para produccion.
"""
from fastapi import FastAPI, Request, Response, HTTPException
from pydantic import BaseModel
from prometheus_client import (
    Counter, Gauge, Histogram, Info,
    generate_latest, CONTENT_TYPE_LATEST
)
import joblib
import numpy as np
import time
import os

app = FastAPI(title="Vehicle Telemetry Prediction API")

# --- Cargar modelo ---
MODEL_PATH = os.getenv("MODEL_PATH", "models/consumption_model.pkl")
model = joblib.load(MODEL_PATH)
model_loaded_at = time.time()

# --- Metricas ---
APP_INFO = Info('prediction_api', 'API info')
APP_INFO.info({
    'version': '2.3.0',
    'model_path': MODEL_PATH,
    'model_loaded_at': str(model_loaded_at),
})

PREDICTIONS = Counter(
    'predictions_total', 'Total predictions',
    ['vehicle_type', 'status']
)

PREDICTION_LATENCY = Histogram(
    'prediction_duration_seconds', 'Prediction latency',
    buckets=[0.001, 0.005, 0.01, 0.025, 0.05, 0.1, 0.25]
)

PREDICTION_VALUE = Histogram(
    'prediction_value', 'Distribution of predicted values',
    buckets=[2, 4, 6, 8, 10, 12, 14, 16, 18, 20, 25, 30, 40]
)

MODEL_SCORE = Gauge('model_current_r2', 'Current R2 score')
ACTIVE_MODELS = Gauge('active_models_count', 'Number of loaded models')
ACTIVE_MODELS.set(1)


# --- Schema ---
class PredictionRequest(BaseModel):
    vehicle_id: str
    vehicle_type: str
    speed_mean: float
    speed_std: float
    battery_temp: float
    motor_rpm: float
    highway_ratio: float

class PredictionResponse(BaseModel):
    vehicle_id: str
    predicted_consumption: float
    model_version: str


# --- Endpoints ---

@app.get("/metrics")
async def metrics():
    return Response(
        content=generate_latest(),
        media_type=CONTENT_TYPE_LATEST
    )

@app.get("/health")
async def health():
    return {
        "status": "healthy",
        "model_loaded": model is not None,
        "uptime_seconds": time.time() - model_loaded_at
    }

@app.post("/predict", response_model=PredictionResponse)
async def predict(req: PredictionRequest):
    start = time.time()

    try:
        features = np.array([[
            req.speed_mean, req.speed_std,
            req.battery_temp, req.motor_rpm,
            req.highway_ratio
        ]])

        prediction = model.predict(features)[0]

        # Registrar metricas de exito
        PREDICTIONS.labels(vehicle_type=req.vehicle_type, status='success').inc()
        PREDICTION_VALUE.observe(prediction)

        return PredictionResponse(
            vehicle_id=req.vehicle_id,
            predicted_consumption=round(prediction, 2),
            model_version="v2.3"
        )

    except Exception as e:
        PREDICTIONS.labels(vehicle_type=req.vehicle_type, status='error').inc()
        raise HTTPException(status_code=500, detail=str(e))

    finally:
        PREDICTION_LATENCY.observe(time.time() - start)
```

---

## 10. Ejemplo real: monitoreo de modelo ML

```python
"""
Script que se ejecuta periodicamente (via Airflow) para evaluar
el modelo en produccion y actualizar metricas de Prometheus.
"""
from prometheus_client import CollectorRegistry, Gauge, push_to_gateway
import pandas as pd
import joblib
from sklearn.metrics import r2_score, mean_squared_error, mean_absolute_error
import numpy as np


def evaluar_y_reportar():
    """Evaluar modelo y enviar metricas a Prometheus via Push Gateway."""

    # Push Gateway: permite enviar metricas desde jobs batch
    # (Prometheus normalmente hace pull/scrape, pero los batch jobs
    #  no tienen un servidor HTTP corriendo permanentemente)

    registry = CollectorRegistry()

    # Definir metricas
    r2 = Gauge('model_evaluation_r2', 'R2 score', ['model'], registry=registry)
    rmse = Gauge('model_evaluation_rmse', 'RMSE', ['model'], registry=registry)
    mae = Gauge('model_evaluation_mae', 'MAE', ['model'], registry=registry)
    drift = Gauge('data_drift_score', 'Drift p-value', ['feature'], registry=registry)
    n_samples = Gauge('evaluation_sample_size', 'Samples used', ['model'], registry=registry)

    # Cargar modelo y datos recientes
    model = joblib.load("models/consumption_model.pkl")
    # df = pd.read_sql("SELECT * FROM predictions_last_24h", engine)

    # Simulacion
    y_true = np.random.uniform(5, 20, 1000)
    y_pred = y_true + np.random.normal(0, 1.5, 1000)

    # Calcular metricas
    r2_val = r2_score(y_true, y_pred)
    rmse_val = np.sqrt(mean_squared_error(y_true, y_pred))
    mae_val = mean_absolute_error(y_true, y_pred)

    r2.labels(model='consumption').set(r2_val)
    rmse.labels(model='consumption').set(rmse_val)
    mae.labels(model='consumption').set(mae_val)
    n_samples.labels(model='consumption').set(len(y_true))

    # Evaluar drift por feature
    # Para cada feature, comparar distribucion de entrenamiento vs produccion
    # usando Kolmogorov-Smirnov test
    from scipy.stats import ks_2samp

    # train_data = pd.read_parquet("data/training_reference.parquet")
    # prod_data = df[feature_columns]
    #
    # for feature in feature_columns:
    #     stat, p_value = ks_2samp(train_data[feature], prod_data[feature])
    #     drift.labels(feature=feature).set(p_value)

    drift.labels(feature='speed_kmh').set(0.45)       # sin drift
    drift.labels(feature='battery_temp').set(0.003)    # drift!
    drift.labels(feature='consumption').set(0.12)      # sin drift

    # Enviar a Prometheus Push Gateway
    push_to_gateway(
        'prometheus-pushgateway:9091',
        job='model_evaluation',
        registry=registry
    )

    print(f"Metricas enviadas: R2={r2_val:.3f}, RMSE={rmse_val:.3f}")


if __name__ == "__main__":
    evaluar_y_reportar()
```

---

## 11. Docker Compose completo

```yaml
# docker-compose.yml
# Stack completo de monitoreo: Prometheus + Grafana + Alertmanager

version: '3.8'

services:
  # Tu API de prediccion
  api:
    build: .
    ports:
      - "8000:8000"
    environment:
      MODEL_PATH: /models/consumption_model.pkl
    volumes:
      - ./models:/models

  # Prometheus: recolecta metricas
  prometheus:
    image: prom/prometheus:v2.48.0
    ports:
      - "9090:9090"
    volumes:
      - ./monitoring/prometheus.yml:/etc/prometheus/prometheus.yml
      - ./monitoring/alerting_rules.yml:/etc/prometheus/alerting_rules.yml
      - prometheus_data:/prometheus
    command:
      - '--config.file=/etc/prometheus/prometheus.yml'
      - '--storage.tsdb.retention.time=30d'  # retener 30 dias

  # Push Gateway: para jobs batch (Airflow)
  pushgateway:
    image: prom/pushgateway:v1.6.2
    ports:
      - "9091:9091"

  # Alertmanager: envia alertas a Slack/email
  alertmanager:
    image: prom/alertmanager:v0.26.0
    ports:
      - "9093:9093"
    volumes:
      - ./monitoring/alertmanager.yml:/etc/alertmanager/alertmanager.yml

  # Grafana: dashboards
  grafana:
    image: grafana/grafana:10.2.0
    ports:
      - "3000:3000"   # http://localhost:3000 (admin/admin)
    environment:
      GF_SECURITY_ADMIN_PASSWORD: admin
    volumes:
      - grafana_data:/var/lib/grafana
      - ./monitoring/grafana/dashboards:/var/lib/grafana/dashboards
      - ./monitoring/grafana/provisioning:/etc/grafana/provisioning

volumes:
  prometheus_data:
  grafana_data:
```

```yaml
# monitoring/prometheus.yml
# Configuracion de Prometheus: a quien monitorear

global:
  scrape_interval: 15s     # recolectar cada 15 segundos
  evaluation_interval: 15s # evaluar alertas cada 15 segundos

rule_files:
  - "alerting_rules.yml"

alerting:
  alertmanagers:
    - static_configs:
        - targets: ['alertmanager:9093']

scrape_configs:
  # Monitorear a Prometheus mismo
  - job_name: 'prometheus'
    static_configs:
      - targets: ['localhost:9090']

  # Monitorear tu API
  - job_name: 'api-prediccion'
    static_configs:
      - targets: ['api:8000']
    metrics_path: /metrics
    scrape_interval: 10s  # cada 10s para la API

  # Push Gateway (metricas de batch jobs)
  - job_name: 'pushgateway'
    static_configs:
      - targets: ['pushgateway:9091']
    honor_labels: true
```
