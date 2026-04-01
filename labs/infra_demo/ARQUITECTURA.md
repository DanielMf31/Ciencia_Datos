# Arquitectura del Sistema Demo

## Vista General

```
┌─────────────────────────────────────────────────────────────────────────┐
│                          DOCKER COMPOSE                                 │
│                    (red interna: infra_demo_default)                     │
│                                                                         │
│  ┌──────────┐     ┌───────────────┐     ┌────────────┐                  │
│  │          │     │               │     │            │                  │
│  │ PRODUCER ├────>│     KAFKA     ├────>│  CONSUMER  ├──┐              │
│  │          │     │               │     │  (1 o mas) │  │              │
│  │ Envia    │     │ Topic:        │     │            │  │              │
│  │ mensaje  │     │ "eventos"     │     │ Procesa    │  │              │
│  │ cada 2s  │     │               │     │ y cuenta   │  │              │
│  └──────────┘     │ Retiene msgs  │     └─────┬──────┘  │              │
│                   │ aunque nadie  │           │         │              │
│                   │ los lea       │           │         │              │
│                   └───────┬───────┘           │         │              │
│                           │                   │         │              │
│                   ┌───────┴───────┐           │         │              │
│                   │   ZOOKEEPER   │           │         │              │
│                   │ (coordinador  │           │         │              │
│                   │  de Kafka)    │           │         │              │
│                   └───────────────┘           │         │              │
│                                              │         │              │
│       ┌──────────────────────────────────────┘         │              │
│       │                                                │              │
│       ▼                                                ▼              │
│  ┌──────────┐                                   ┌────────────┐        │
│  │          │                                   │            │        │
│  │ POSTGRES │                                   │ /metrics   │        │
│  │          │                                   │ (HTTP)     │        │
│  │ Tabla:   │                                   │            │        │
│  │ message_ │                                   │ Expone     │        │
│  │ counts   │                                   │ contadores │        │
│  │          │                                   │ para       │        │
│  └────┬─────┘                                   │ Prometheus │        │
│       │                                         └──────┬─────┘        │
│       │                                                │              │
│       ▼                                                ▼              │
│  ┌──────────┐                                   ┌────────────┐        │
│  │          │                                   │            │        │
│  │ AIRFLOW  │                                   │ PROMETHEUS │        │
│  │          │                                   │            │        │
│  │ DAG que  │                                   │ Scrape     │        │
│  │ consulta │                                   │ cada 5s    │        │
│  │ la BD    │                                   │            │        │
│  │ cada 1m  │                                   │ Almacena   │        │
│  │          │                                   │ historial  │        │
│  └──────────┘                                   └──────┬─────┘        │
│                                                        │              │
│                                                        ▼              │
│                                                 ┌────────────┐        │
│  ┌──────────┐     ┌───────────────┐             │            │        │
│  │          │     │               │             │  GRAFANA   │        │
│  │PROMTAIL  ├────>│     LOKI      ├────────────>│            │        │
│  │          │     │               │             │ Dashboards │        │
│  │ Recolecta│     │ Almacena      │             │ Metricas   │        │
│  │ logs de  │     │ logs          │             │ + Logs     │        │
│  │ Docker   │     │               │             │            │        │
│  └──────────┘     └───────────────┘             └────────────┘        │
│                                                                       │
└───────────────────────────────────────────────────────────────────────┘
```

---

## Flujo de Datos (paso a paso)

```
Segundo 0:
  Producer genera: {"id": 1, "sensor": "temperatura", "value": 42.5}
       │
       ▼
Segundo 0.001:
  Kafka recibe el mensaje y lo guarda en el topic "eventos"
  (particion 0, offset 0)
  El mensaje queda almacenado aunque nadie lo lea.
       │
       ▼
Segundo 0.050:
  Consumer lee el mensaje de Kafka:
  1. Incrementa contador en memoria: messages_total = 1
  2. Incrementa contador por sensor: temperatura = 1
  3. Ejecuta UPDATE en PostgreSQL: count = count + 1
  4. Escribe log: "Procesado #1: temperatura=42.5 (total: 1)"
       │
       ├─── El log va a stdout del contenedor
       │         │
       │         ▼
       │    Promtail detecta el log del contenedor Docker
       │    y lo envia a Loki con labels {container="consumer"}
       │
       └─── /metrics se actualiza:
            messages_processed_total 1
            messages_by_sensor{sensor="temperatura"} 1
                  │
                  ▼
            Prometheus scrapeara /metrics en su proximo ciclo (cada 5s)
            y guardara el valor con timestamp

Segundo 2:
  Producer envia otro mensaje. El ciclo se repite.

Segundo 5:
  Prometheus hace scrape a consumer:8001/metrics
  Guarda: messages_processed_total = 3 (a las 12:00:05)

Segundo 10:
  Prometheus hace otro scrape:
  Guarda: messages_processed_total = 5 (a las 12:00:10)
  Ahora puede calcular: rate = (5-3) / 5s = 0.4 mensajes/segundo

Minuto 1:
  Airflow ejecuta el DAG "health_check":
  1. Conecta a PostgreSQL
  2. SELECT sensor, count FROM message_counts
  3. Imprime: "Total: 30 mensajes procesados"
  4. El log del DAG se puede ver en la UI de Airflow

En Grafana (cualquier momento):
  Panel 1 (Prometheus): grafico de messages_processed_total subiendo
  Panel 2 (Prometheus): rate(messages_processed_total[1m]) = ~0.5 msg/s
  Panel 3 (Loki): logs del consumer en tiempo real
```

---

## Que hace cada componente

### PRODUCER → KAFKA

```
Producer                              Kafka
┌─────────────┐                       ┌─────────────────────────┐
│ while True: │    send()             │ Topic: "eventos"        │
│   msg = {}  │ ─────────────────────>│                         │
│   sleep(2)  │                       │ Particion 0:            │
└─────────────┘                       │ [msg0][msg3][msg6]...   │
                                      │                         │
                                      │ Particion 1:            │
                                      │ [msg1][msg4][msg7]...   │
                                      │                         │
                                      │ Cada mensaje tiene:     │
                                      │  - offset (posicion)    │
                                      │  - key (sensor-X)       │
                                      │  - value (JSON)         │
                                      │  - timestamp            │
                                      └─────────────────────────┘

La KEY determina la particion:
  key="sensor-0" → siempre particion 0 (por hash)
  key="sensor-1" → siempre particion 1
  key="sensor-2" → siempre particion 2 (si hay 3 particiones)
```

### KAFKA → CONSUMER(S)

```
Con 1 consumer:
  Consumer 1 lee TODAS las particiones
  ┌─────────┐
  │Consumer1│ ← particion 0, 1 (lee todo)
  └─────────┘

Con 2 consumers (mismo group_id):
  Kafka REPARTE las particiones automaticamente
  ┌─────────┐
  │Consumer1│ ← particion 0 (solo la mitad)
  └─────────┘
  ┌─────────┐
  │Consumer2│ ← particion 1 (la otra mitad)
  └─────────┘

  → Cada mensaje se procesa UNA sola vez
  → Si Consumer1 se cae, Consumer2 asume su particion (rebalanceo)
```

### CONSUMER → PROMETHEUS

```
Consumer expone HTTP en :8001/metrics

  GET /metrics →

  # HELP messages_processed_total Total de mensajes
  # TYPE messages_processed_total counter
  messages_processed_total 847

  # HELP messages_by_sensor Mensajes por sensor
  # TYPE messages_by_sensor counter
  messages_by_sensor{sensor="temperatura"} 283
  messages_by_sensor{sensor="velocidad"} 280
  messages_by_sensor{sensor="presion"} 284

  consumer_up 1

Prometheus cada 5 segundos:
  1. HTTP GET → consumer:8001/metrics
  2. Parsea los valores
  3. Guarda: (timestamp=12:00:05, messages_total=847)
  4. Guarda: (timestamp=12:00:10, messages_total=850)
  5. Ahora puede calcular tasas, tendencias, alertas
```

### PROMETHEUS → GRAFANA

```
Grafana consulta a Prometheus con PromQL:

  "Dame messages_processed_total de las ultimas 2 horas"

  Prometheus responde:
    12:00:00 → 0
    12:00:05 → 3
    12:00:10 → 5
    12:00:15 → 8
    ...
    14:00:00 → 3600

  Grafana dibuja una linea que sube continuamente.

  "Dame rate(messages_processed_total[1m])"

  Prometheus calcula la derivada:
    12:01 → 0.5 msg/s
    12:02 → 0.5 msg/s
    12:03 → 0.0 msg/s  ← ¡consumer caido!
    12:04 → 1.2 msg/s  ← volvio y proceso los acumulados

  Grafana dibuja una linea que muestra la velocidad de procesamiento.
```

### LOGS: Contenedores → Promtail → Loki → Grafana

```
Contenedor Docker
  │  stdout: {"time":"...", "level":"INFO", "message":"Procesado #42"}
  │
  ▼
/var/lib/docker/containers/<id>/<id>-json.log  ← Docker guarda aqui
  │
  ▼
Promtail (montado con acceso a /var/run/docker.sock)
  1. Detecta contenedores automaticamente
  2. Lee sus logs
  3. Anade labels: {container="infra_demo-consumer-1"}
  4. Envia a Loki via HTTP POST
  │
  ▼
Loki
  1. Indexa solo las labels (container, stream)
  2. Comprime y guarda el texto del log
  3. Responde queries LogQL
  │
  ▼
Grafana
  Query: {container=~".*consumer.*"}
  → Muestra los logs en tiempo real como un terminal

  Query: {container=~".*consumer.*"} |= "ERROR"
  → Solo errores

  Query: rate({container=~".*consumer.*"}[5m])
  → Lineas de log por segundo (detecta si algo empieza a loguear mucho)
```

### AIRFLOW → POSTGRESQL

```
Cada minuto, Airflow:

  ┌─────────────────────────┐
  │   DAG: health_check     │
  │                         │
  │  ┌──────────────────┐   │
  │  │check_message_    │   │    ┌──────────┐
  │  │counts            │───────>│POSTGRESQL│
  │  │                  │   │    │          │
  │  │ SELECT sensor,   │<───────│ tabla:   │
  │  │ count FROM ...   │   │    │ message_ │
  │  └────────┬─────────┘   │    │ counts   │
  │           │              │    └──────────┘
  │           ▼              │
  │  ┌──────────────────┐   │
  │  │evaluate_health   │   │
  │  │                  │   │
  │  │ if total > 0:    │   │
  │  │   "OK"           │   │
  │  │ else:            │   │
  │  │   "WARNING"      │   │
  │  └──────────────────┘   │
  └─────────────────────────┘

  El resultado se ve en la UI de Airflow → click en tarea → Logs
```

---

## Puertos y acceso

```
Tu navegador (host)                    Red interna Docker
────────────────────                   ────────────────────

localhost:8180 ──────────────────────> kafka-ui:8080
localhost:9090 ──────────────────────> prometheus:9090
localhost:3001 ──────────────────────> grafana:3000
localhost:8080 ──────────────────────> airflow:8080
localhost:3101 ──────────────────────> loki:3100
localhost:5432 ──────────────────────> postgres:5432

NO accesible directamente desde host (solo red interna):
  consumer:8001  ← Prometheus lo alcanza por red interna
  kafka:9092     ← Producer/Consumer lo alcanzan por red interna
  zookeeper:2181 ← Solo Kafka lo necesita
```

---

## Analogia con un sistema real

```
Este demo                          Produccion real
──────────                         ───────────────
Producer (script Python)        →  50.000 coches enviando telemetria
Kafka (1 broker, 1 topic)       →  Kafka cluster (3+ brokers, muchos topics)
Consumer (1 proceso Python)     →  Microservicios (3+ instancias, Kubernetes)
PostgreSQL (1 tabla)            →  TimescaleDB / ClickHouse (millones de filas)
Airflow (1 DAG simple)          →  Airflow (50+ DAGs: ETL, ML, reportes)
Prometheus (1 target)           →  Prometheus (100+ targets, alertas)
Loki (logs basicos)             →  Loki cluster (TB de logs/dia)
Grafana (dashboards manuales)   →  Grafana (dashboards predefinidos, alertas)

Los CONCEPTOS son identicos.
Solo cambia la ESCALA.
```
