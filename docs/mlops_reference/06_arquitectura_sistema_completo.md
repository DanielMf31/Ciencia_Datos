# Arquitectura Completa: Sistema de Telemetria Vehicular

## Vista General

```
                            INTERNET
                               │
                         ┌─────┴─────┐
                         │  NGINX    │ (reverse proxy + SSL)
                         │  :443     │ puerto 443 (HTTPS)
                         └─────┬─────┘
                               │
              ┌────────────────┼────────────────┐
              │                │                │
              ▼                ▼                ▼
        ┌──────────┐    ┌──────────┐    ┌──────────┐
        │ React    │    │ FastAPI  │    │ Grafana  │
        │ Dashboard│    │ API      │    │ Dashboards│
        │ :3000    │    │ :8000    │    │ :3001    │
        └──────────┘    └────┬─────┘    └──────────┘
              │              │                │
              │              ▼                │
              │        ┌──────────┐           │
              │        │  KAFKA   │           │
              │        │  :9092   │           │
              │        └────┬─────┘           │
              │              │                │
              │    ┌─────────┼─────────┐      │
              │    ▼         ▼         ▼      │
              │ ┌──────┐ ┌──────┐ ┌──────┐   │
              │ │Cons. │ │Cons. │ │Cons. │   │
              │ │  DB  │ │Alert │ │Metric│   │
              │ └──┬───┘ └──┬───┘ └──┬───┘   │
              │    │        │        │        │
              │    ▼        ▼        ▼        │
              │ ┌──────┐ ┌──────┐ ┌──────┐   │
              │ │Postgr│ │Slack │ │Promet│   │
              │ │  SQL  │ │Email │ │heus  │───┘
              │ └──┬───┘ └──────┘ └──────┘
              │    │
              │    ▼
              │ ┌───────────────────┐
              └─┤ Datos procesados  │
                │ (para dashboards) │
                └──────┬────────────┘
                       │
              ┌────────┴─────────┐
              │   AIRFLOW        │
              │   (3:00 AM)      │
              │                  │
              │ 1. Leer BD       │
              │ 2. Procesar      │
              │ 3. ML predict    │
              │ 4. Cloud Storage │
              │ 5. Reportes      │
              └──────────────────┘
```

---

## 1. Vehiculos envian datos a la API

```
10 coches (o simulador en un contenedor)
         │
         │ HTTPS POST cada 5-30 segundos
         │
         ▼
    FastAPI :8000/api/telemetry

    POST /api/telemetry
    {
      "vehicle_id": "V001",
      "timestamp": "2026-03-15T14:23:01Z",
      "speed_kmh": 85.3,
      "battery_temp": 42.1,
      "gps_lat": 19.4326,
      "gps_lon": -99.1332,
      ...
    }
```

```python
# FastAPI recibe y publica en Kafka (NO guarda en BD directamente)
@app.post("/api/telemetry")
async def receive_telemetry(data: TelemetryData):
    # Validar datos
    # Publicar en Kafka (instantaneo, no bloquea)
    producer.send("telemetria-raw", key=data.vehicle_id, value=data.dict())
    return {"status": "ok"}
```

Por que no guardar directo en BD: si llegan 10.000 mensajes/segundo, la BD se satura. Kafka absorbe el pico y los consumers escriben a su ritmo.

---

## 2. Kafka distribuye a multiples consumers

```
Topic "telemetria-raw"
         │
         ├──> Consumer 1 (grupo: "guardado-db")
         │    → INSERT en PostgreSQL/TimescaleDB
         │    → Datos crudos para analisis posterior
         │
         ├──> Consumer 2 (grupo: "alertas-tiempo-real")
         │    → Si battery_temp > 45°C → Slack/Email INMEDIATO
         │    → Si speed > 130 km/h → alerta
         │    → Latencia: < 5 segundos desde que el coche envia
         │
         └──> Consumer 3 (grupo: "metricas-prometheus")
              → Actualiza contadores para Grafana
              → messages_total, avg_speed, avg_consumption
              → Dashboard se actualiza en tiempo real
```

---

## 3. PostgreSQL: dos tipos de datos

```
┌─────────────────────────────────────────────────────┐
│  PostgreSQL                                          │
│                                                      │
│  Tabla: telemetry_raw (datos crudos, crece rapido)   │
│  ┌─────────┬──────┬───────┬──────────┬─────────┐    │
│  │timestamp│veh_id│speed  │bat_temp  │gps_lat  │... │
│  │ 14:23:01│ V001 │ 85.3  │  42.1    │ 19.43   │    │
│  │ 14:23:02│ V002 │ 60.0  │  31.5    │ 19.45   │    │
│  │ ...     │      │       │          │         │    │
│  │ MILLONES de filas                            │    │
│  └──────────────────────────────────────────────┘    │
│                                                      │
│  Tabla: dashboard_metrics (procesada, pequena)       │
│  ┌─────────┬──────┬──────────┬──────────┬──────┐    │
│  │  date   │veh_id│avg_speed │avg_consmp│trips │    │
│  │ 2026-03 │ V001 │   72.3   │   8.5    │  12  │    │
│  │ 2026-03 │ V002 │   55.1   │   6.2    │   8  │    │
│  │ Solo filas agregadas por dia/vehiculo        │    │
│  └──────────────────────────────────────────────┘    │
│                                                      │
│  Tabla: alerts (historial de alertas)                │
│  Tabla: predictions (resultados del modelo ML)       │
│  Tabla: users (autenticacion del dashboard)          │
│                                                      │
└─────────────────────────────────────────────────────┘

React Dashboard lee de dashboard_metrics (rapido, pocas filas)
NO lee de telemetry_raw (lento, millones de filas)
```

---

## 4. Procesamiento: tiempo real vs batch

```
TIEMPO REAL (cada segundo):
  Coche → API → Kafka → Consumers → BD + Alertas + Metricas
  Latencia: < 5 segundos
  Para: alertas urgentes, dashboard en vivo, metricas Grafana

NEAR-REAL-TIME (cada 1-5 minutos):
  Airflow o un cron job:
    1. Lee ultimos 5 min de telemetry_raw
    2. Agrega: avg_speed, avg_consumption por vehiculo
    3. Escribe en dashboard_metrics
    4. React Dashboard se actualiza al refrescar
  Para: KPIs del dashboard, graficas de tendencias

BATCH (3:00 AM, diario):
  Airflow DAG completo:
    1. Lee TODO el dia anterior de telemetry_raw
    2. Procesa con Pandas/Spark segun volumen
    3. Feature engineering
    4. Pasa features por modelo ML → predicciones
    5. Detecta anomalias con Isolation Forest
    6. Identifica vehiculos que necesitan mantenimiento
    7. Guarda predicciones en PostgreSQL
    8. Archiva datos crudos en Cloud Storage
    9. Genera resumen ejecutivo (email/Slack)
```

---

## 5. Cloud Storage: archivo permanente

```
gs://mi-empresa-telemetria/
├── raw/                          ← Airflow archiva aqui cada noche
│   ├── 2026-03-01.parquet
│   ├── 2026-03-02.parquet
│   └── ...
├── processed/                    ← Datos ya procesados/agregados
│   ├── daily_metrics/
│   └── monthly_reports/
├── models/                       ← Modelos ML versionados
│   ├── consumption_v1.pkl
│   ├── consumption_v2.pkl
│   └── anomaly_v1.pkl
└── backups/                      ← Backups de PostgreSQL
    └── pg_backup_2026-03-14.sql.gz

PostgreSQL solo mantiene los ultimos 30-90 dias de datos crudos.
Datos mas antiguos se borran de PostgreSQL (ya estan en Cloud Storage).
Si necesitas analizar datos de hace 6 meses → lees de Cloud Storage.
```

---

## 6. Monitoreo: Prometheus + Grafana + Loki

```
┌────────────────────────────────────────────────────────┐
│  MONITOREO (siempre corriendo)                         │
│                                                         │
│  Prometheus ← scrape cada 15s ─┐                       │
│  (metricas)                     ├─ FastAPI /metrics     │
│       │                         ├─ Consumer /metrics    │
│       │                         ├─ PostgreSQL exporter  │
│       │                         └─ Node exporter (CPU)  │
│       │                                                 │
│       ▼                                                 │
│  Grafana ◄──────── Loki ◄──── Promtail                 │
│  (dashboards)     (logs)     (recolecta logs Docker)    │
│                                                         │
│  Dashboard "Sistema":                                   │
│    - API: 127 req/s, latencia p99 = 23ms               │
│    - Kafka: 500 msg/s, lag = 0 (consumers al dia)      │
│    - PostgreSQL: 85% disco, 45% CPU                     │
│    - Modelo ML: R2 = 0.87, ultima ejecucion 03:45 AM   │
│                                                         │
│  Dashboard "Flota" (lo que ve el negocio):              │
│    - 48/50 vehiculos activos                            │
│    - 3 alertas activas                                  │
│    - Consumo medio: 8.2 L/100km (3% menos vs mes ant.) │
│                                                         │
│  Alertas automaticas:                                   │
│    → API latencia > 500ms → Slack #ops                  │
│    → Consumer lag > 1000 → Slack #ops                   │
│    → Modelo R2 < 0.80 → Slack #ml-team                  │
│    → Vehiculo temp > 45°C → Slack #fleet + SMS gestor  │
│                                                         │
└────────────────────────────────────────────────────────┘
```

---

## 7. Como exponer a Internet

### Opcion 1: Nginx reverse proxy (lo mas comun)

```
Internet → Nginx (:443 HTTPS) → servicios internos

  dashboard.miempresa.com  →  React :3000
  api.miempresa.com        →  FastAPI :8000
  grafana.miempresa.com    →  Grafana :3001
  airflow.miempresa.com    →  Airflow :8080

Kafka, PostgreSQL, Prometheus, Loki:
  → NO se exponen a internet (solo red interna Docker)
```

### Opcion 2: Cloudflare Tunnel (gratis, sin abrir puertos)

```
Tu servidor ──(tunel encriptado)──> Cloudflare ──> Internet

No abres ningun puerto en tu router.
Cloudflare te da SSL gratis.
Puedes proteger con Cloudflare Access (login con Google/GitHub).
```

### Opcion 3: Cloud (Google Cloud Run, AWS)

```
Todo corre en la nube.
Ellos gestionan SSL, DNS, load balancing.
```

---

## 8. Seguridad: que se expone y que NO

```
EXPUESTO A INTERNET (con autenticacion):
  ✓ React Dashboard     → usuarios del negocio (login)
  ✓ FastAPI API          → vehiculos (API key) + dashboard (JWT)
  ✓ Grafana              → equipo tecnico (login Grafana)

NO EXPUESTO (solo red interna Docker):
  ✗ Kafka                → solo consumers internos lo necesitan
  ✗ PostgreSQL           → solo la API y Airflow lo necesitan
  ✗ Prometheus           → solo Grafana lo consulta
  ✗ Loki                 → solo Grafana lo consulta
  ✗ Airflow              → opcionalmente expuesto con VPN/auth
  ✗ Promtail             → solo envia a Loki internamente
```

---

## Docker Compose de produccion (simplificado)

```yaml
services:
  # === EXPUESTOS (detras de Nginx) ===
  nginx:
    image: nginx:alpine
    ports:
      - "443:443"
      - "80:80"
    volumes:
      - ./nginx/conf.d:/etc/nginx/conf.d
      - ./certbot/certs:/etc/letsencrypt

  api:
    build: ./api
    expose: ["8000"]

  dashboard:
    build: ./dashboard
    expose: ["3000"]

  grafana:
    image: grafana/grafana
    expose: ["3000"]

  # === INTERNOS (nunca expuestos) ===
  kafka:
    image: confluentinc/cp-kafka

  postgres:
    image: postgres:16

  consumer-db:
    build: ./consumer

  consumer-alerts:
    build: ./consumer-alerts

  prometheus:
    image: prom/prometheus

  loki:
    image: grafana/loki

  promtail:
    image: grafana/promtail

  airflow:
    image: apache/airflow
    expose: ["8080"]
```
