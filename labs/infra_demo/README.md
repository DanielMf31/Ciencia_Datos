# Infra Demo: Kafka + Airflow + Prometheus + Grafana + Loki

Sistema minimo para entender como se conectan las herramientas MLOps.

## Arquitectura

```
                         CADA MINUTO (Airflow)
                               ↓
Producer ──> KAFKA ──> Consumer ──> PostgreSQL (contador)
(cada 2s)   (cola)   (procesa)         ↓
                         ↓          /metrics
                    Logs (stdout)      ↓
                         ↓        Prometheus (scrape cada 15s)
                      Promtail         ↓
                         ↓         Grafana (dashboards)
                       Loki ──────→ Grafana (logs)
```

## Que hace cada pieza

| Servicio | Que hace | Puerto |
|----------|----------|--------|
| **producer** | Envia un mensaje a Kafka cada 2 segundos | - |
| **kafka** | Cola de mensajes (almacena y distribuye) | 9092 |
| **consumer** | Lee de Kafka, cuenta mensajes, expone metricas | 8001 |
| **postgres** | Guarda el conteo de mensajes procesados | 5432 |
| **airflow** | Cada minuto ejecuta un DAG que consulta el conteo | 8080 |
| **prometheus** | Recolecta metricas del consumer cada 15s | 9090 |
| **grafana** | Dashboards de metricas + logs | 3000 |
| **loki** | Almacena logs de todos los contenedores | 3100 |
| **promtail** | Recolecta logs de Docker y los envia a Loki | - |
| **kafka-ui** | UI web para ver topics y mensajes de Kafka | 8180 |

## Como levantar

```bash
cd labs/infra_demo

# Levantar todo
docker compose up -d

# Ver logs en tiempo real
docker compose logs -f producer consumer

# Esperar ~1 minuto para que todo arranque
```

## Que mirar

1. **Kafka UI**: http://localhost:8180
   → Ver el topic "eventos", los mensajes llegando

2. **Prometheus**: http://localhost:9090
   → Buscar: `messages_processed_total`
   → Buscar: `rate(messages_processed_total[1m])`

3. **Grafana**: http://localhost:3000 (admin/admin)
   → Data sources ya configurados (Prometheus + Loki)
   → Importar el dashboard o crear paneles manualmente

4. **Airflow**: http://localhost:8080 (admin/admin)
   → DAG "health_check" ejecutandose cada minuto

## Como parar

```bash
docker compose down        # parar todo
docker compose down -v     # parar y borrar datos
```
