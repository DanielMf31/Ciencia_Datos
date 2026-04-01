# Guia Practica: Comandos y Experimentos

## URLs de acceso

| Servicio | URL | Credenciales |
|----------|-----|-------------|
| Kafka UI | http://localhost:8180 | - |
| Prometheus | http://localhost:9090 | - |
| Grafana | http://localhost:3001 | admin / admin |
| Airflow | http://localhost:8080 | admin / admin |
| Consumer metrics | http://localhost:8001/metrics | - |

---

## 1. Arrancar y parar

```bash
# Levantar todo
docker compose up -d

# Parar todo (mantiene datos)
docker compose down

# Parar y BORRAR todos los datos
docker compose down -v

# Reconstruir despues de cambiar codigo
docker compose up -d --build
```

---

## 2. Ver logs en tiempo real

```bash
# Ver TODO
docker compose logs -f

# Solo producer (mensajes enviados)
docker compose logs -f producer

# Solo consumer (mensajes procesados)
docker compose logs -f consumer

# Ambos lado a lado
docker compose logs -f producer consumer

# Solo errores
docker compose logs -f consumer 2>&1 | grep -i error

# Ultimas 20 lineas de airflow
docker compose logs --tail 20 airflow

# Ver estado de todos los contenedores
docker compose ps
```

---

## 3. Kafka: ver mensajes

### Desde Kafka UI (http://localhost:8180)
1. Click en **Topics** → **eventos**
2. Pestaña **Messages** → ves cada mensaje JSON
3. Puedes filtrar por key, partition, offset

### Desde terminal
```bash
# Listar topics existentes
docker compose exec kafka kafka-topics --bootstrap-server localhost:9092 --list

# Ver mensajes en tiempo real (como un consumer manual)
docker compose exec kafka kafka-console-consumer \
  --bootstrap-server localhost:9092 \
  --topic eventos \
  --from-beginning

# Ver solo los ultimos 5 mensajes
docker compose exec kafka kafka-console-consumer \
  --bootstrap-server localhost:9092 \
  --topic eventos \
  --max-messages 5 \
  --from-beginning

# Ver detalles del topic (particiones, replicas)
docker compose exec kafka kafka-topics \
  --bootstrap-server localhost:9092 \
  --describe \
  --topic eventos

# Cuantos mensajes hay en el topic
docker compose exec kafka kafka-run-class kafka.tools.GetOffsetShell \
  --broker-list localhost:9092 \
  --topic eventos
```

---

## 4. PostgreSQL: consultar la base de datos

```bash
# Ver conteo de mensajes por sensor
docker compose exec postgres psql -U demo -d demo \
  -c "SELECT sensor, count, last_updated FROM message_counts ORDER BY count DESC;"

# Ver total
docker compose exec postgres psql -U demo -d demo \
  -c "SELECT SUM(count) as total FROM message_counts;"

# Shell interactivo de PostgreSQL
docker compose exec postgres psql -U demo -d demo
# Dentro puedes ejecutar:
#   \dt                          → listar tablas
#   SELECT * FROM message_counts; → ver datos
#   \q                           → salir
```

---

## 5. Prometheus: queries de metricas

### Desde la UI (http://localhost:9090)

Escribe en la barra de busqueda y click en **Execute** → **Graph**:

```promql
# Contador total de mensajes
messages_processed_total

# Mensajes por tipo de sensor
messages_by_sensor

# Solo un sensor
messages_by_sensor{sensor="temperatura"}

# Tasa: mensajes procesados por segundo (ultimo minuto)
rate(messages_processed_total[1m])

# Tasa por sensor
rate(messages_by_sensor[1m])

# Errores
consumer_errors_total

# Consumer esta vivo?
consumer_up
```

### Desde terminal (API de Prometheus)
```bash
# Query instantanea
curl -s 'http://localhost:9090/api/v1/query?query=messages_processed_total' | python3 -m json.tool

# Valor de un sensor
curl -s 'http://localhost:9090/api/v1/query?query=messages_by_sensor{sensor="temperatura"}' | python3 -m json.tool
```

---

## 6. Grafana: crear dashboards

### Acceder: http://localhost:3001 (admin/admin)

### Crear panel de metricas (Prometheus)
1. **+** → **New dashboard** → **Add visualization**
2. Datasource: **Prometheus**
3. Query: `messages_processed_total`
4. Click **Run queries** → ves la linea subiendo
5. **Apply**

### Crear panel de tasa (mensajes/segundo)
1. **Add visualization** → Prometheus
2. Query: `rate(messages_processed_total[1m])`
3. Title: "Mensajes por segundo"
4. **Apply**

### Crear panel por sensor
1. **Add visualization** → Prometheus
2. Query: `messages_by_sensor`
3. Legend: `{{sensor}}`
4. Ves una linea por cada sensor (temperatura, velocidad, presion)

### Crear panel de logs (Loki)
1. **Add visualization** → Datasource: **Loki**
2. Query: `{container=~".*consumer.*"}`
3. Cambiar tipo de panel: arriba a la derecha, seleccionar **Logs**
4. Ves los logs del consumer en tiempo real
5. **Apply**

### Queries utiles para paneles Grafana

| Panel | Datasource | Query | Tipo panel |
|-------|-----------|-------|-----------|
| Total mensajes | Prometheus | `messages_processed_total` | Stat |
| Mensajes/segundo | Prometheus | `rate(messages_processed_total[1m])` | Time series |
| Por sensor | Prometheus | `messages_by_sensor` | Time series |
| Errores | Prometheus | `consumer_errors_total` | Stat |
| Logs consumer | Loki | `{container=~".*consumer.*"}` | Logs |
| Logs producer | Loki | `{container=~".*producer.*"}` | Logs |
| Logs con filtro | Loki | `{container=~".*consumer.*"} \|= "temperatura"` | Logs |
| Solo errores | Loki | `{container=~".*consumer.*"} \|= "ERROR"` | Logs |

---

## 7. Airflow: ver el DAG

### Desde la UI (http://localhost:8080, admin/admin)
1. Ves el DAG **health_check** en la lista
2. Click en el DAG → pestaña **Graph** (ves las tareas)
3. Click en una ejecucion (cuadrado verde) → **Logs**
4. Ves el resultado del health check:
   ```
   === HEALTH CHECK ===
   Total mensajes procesados: 847
     temperatura: 283
     velocidad: 280
     presion: 284
   Estado: OK
   ```

### Desde terminal
```bash
# Listar DAGs
docker compose exec airflow airflow dags list

# Ejecutar el DAG manualmente (sin esperar al schedule)
docker compose exec airflow airflow dags trigger health_check

# Ver ultimas ejecuciones
docker compose exec airflow airflow dags list-runs -d health_check
```

---

## 8. Consumer: ver metricas raw

```bash
# Ver las metricas que Prometheus scrapeara
curl -s http://localhost:8001/metrics

# Health check del consumer
curl -s http://localhost:8001/health
```

---

## 9. EXPERIMENTOS: entender los conceptos

### Experimento 1: Kafka retiene mensajes
```bash
# 1. Parar el consumer
docker compose stop consumer

# 2. Esperar 30 segundos (producer sigue enviando a Kafka)
sleep 30

# 3. Ver que Kafka tiene mensajes acumulados
docker compose exec kafka kafka-console-consumer \
  --bootstrap-server localhost:9092 \
  --topic eventos \
  --from-beginning \
  --max-messages 5

# 4. Arrancar el consumer de nuevo
docker compose start consumer

# 5. Ver como procesa todos los mensajes acumulados de golpe
docker compose logs -f consumer
# → Veras un burst de mensajes procesados rapidamente
# → Kafka NO perdio nada mientras el consumer estaba parado
```

### Experimento 2: Prometheus detecta caida
```bash
# 1. Abre Grafana con un panel de rate(messages_processed_total[1m])
# 2. Parar el consumer
docker compose stop consumer

# 3. En Prometheus: consumer_up ahora es 0
# 4. En Grafana: la tasa baja a 0

# 5. Arrancar de nuevo
docker compose start consumer

# 6. En Grafana: la tasa vuelve a subir
# → Asi detectas caidas en produccion
```

### Experimento 3: Escalar consumers
```bash
# Lanzar 2 consumers en paralelo
docker compose up -d --scale consumer=2

# Ver los logs de ambos
docker compose logs -f consumer

# Cada consumer recibe DIFERENTES mensajes (Kafka los reparte)
# → Esto es un consumer group en accion

# Volver a 1 consumer
docker compose up -d --scale consumer=1
```

### Experimento 4: Producer rapido vs lento
```bash
# Parar producer actual
docker compose stop producer

# Enviar mensajes manualmente desde terminal (uno por uno)
docker compose exec kafka kafka-console-producer \
  --bootstrap-server localhost:9092 \
  --topic eventos
# Escribe JSON y pulsa Enter:
# {"id":999,"sensor":"manual","value":42.0,"timestamp":"ahora"}
# Ctrl+C para salir

# Ver que el consumer lo proceso
docker compose logs --tail 5 consumer

# Arrancar producer automatico de nuevo
docker compose start producer
```

### Experimento 5: Consultar Loki desde terminal
```bash
# Ver logs del consumer en Loki (via API)
curl -s 'http://localhost:3101/loki/api/v1/query_range' \
  --data-urlencode 'query={container=~".*consumer.*"}' \
  --data-urlencode 'limit=5' | python3 -m json.tool

# Buscar un texto especifico
curl -s 'http://localhost:3101/loki/api/v1/query_range' \
  --data-urlencode 'query={container=~".*consumer.*"} |= "temperatura"' \
  --data-urlencode 'limit=3' | python3 -m json.tool
```

### Experimento 6: Ver que pasa en Airflow cuando no hay datos
```bash
# Parar todo excepto Airflow y Postgres
docker compose stop producer consumer kafka zookeeper

# Esperar a la siguiente ejecucion del DAG en Airflow
# → health_check seguira funcionando pero mostrara los mismos conteos
# → No hay mensajes nuevos pero la BD sigue accesible

# Arrancar todo de nuevo
docker compose start zookeeper
sleep 10
docker compose start kafka
sleep 15
docker compose start producer consumer
```

---

## 10. Limpiar todo

```bash
# Parar contenedores
docker compose down

# Parar y borrar volumenes (datos de PostgreSQL)
docker compose down -v

# Borrar imagenes construidas (producer/consumer)
docker compose down -v --rmi local

# Borrar TODO (imagenes descargadas tambien)
docker compose down -v --rmi all
```
