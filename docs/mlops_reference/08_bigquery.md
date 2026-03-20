# BigQuery - Guia de Referencia

## Que es BigQuery

BigQuery es una **base de datos serverless** en la que no gestionas disco, RAM, CPU, ni servidores. Solo envias SQL y recibes resultados.

```
PostgreSQL (tradicional):
  Tu gestionas TODO:
  ┌─────────────────────────────┐
  │  Tu VM ($50/mes)            │
  │  ├── Ubuntu                 │
  │  ├── PostgreSQL instalado   │
  │  ├── Disco SSD 200 GB      │
  │  ├── RAM 16 GB              │
  │  ├── Backups (tu los haces) │
  │  └── Updates (tu los haces) │
  └─────────────────────────────┘
  Si el disco se llena → tu problema
  Si la RAM no alcanza → tu problema
  Si se cae → tu problema

BigQuery:
  Tu solo envias SQL:
  ┌─────────────────────────────┐
  │  Tu codigo                  │
  │  "SELECT AVG(speed) FROM ." │
  │           │                 │
  │           ▼                 │
  │  HTTPS → BigQuery API       │
  │           │                 │
  │           ▼                 │
  │  Google lo procesa en       │
  │  MILES de servidores        │
  │  internos que tu no ves     │
  │           │                 │
  │           ▼                 │
  │  Resultado en 3 segundos    │
  └─────────────────────────────┘
  No hay disco, no hay VM, no hay nada que gestionar
```

---

## Almacenamiento separado de computo

```
PostgreSQL:
  Almacenamiento y computo estan JUNTOS en la misma maquina
  Si necesitas mas disco → maquina mas grande → mas cara
  Si necesitas mas CPU para queries → maquina mas grande

BigQuery:
  Almacenamiento y computo estan SEPARADOS

  Almacenamiento: $0.02/GB/mes (pagas por datos guardados)
    1 TB guardado = $20/mes
    Siempre disponible, no se "apaga"

  Computo: $5/TB escaneado (pagas por query)
    Query que escanea 10 GB = $0.05
    Query que escanea 1 TB = $5
    Si no haces queries = $0 en computo
```

---

## Cuanto cuesta

```
Proyecto pequeno (50 vehiculos, 1 año):
  Datos: ~4 GB → $0.08/mes
  Queries: <1 TB/mes → GRATIS (primer TB gratis)
  Total: $0.08/mes

Empresa real (50,000 vehiculos, 1 año):
  Datos: ~4 TB → $80/mes
  Queries: ~50 TB/mes → $250/mes
  Total: $330/mes

Sandbox GRATUITO (para aprender):
  10 GB almacenamiento
  1 TB queries/mes
  Sin tarjeta de credito
  Para siempre (no expira)
```

---

## Como se usa

### Desde la web (Console)

```
1. Ve a https://console.cloud.google.com/bigquery
2. Escribes SQL directamente en el editor
3. Click "Run" → resultados en segundos

Ejemplo con datos publicos (gratis):

  SELECT
    pickup_datetime,
    passenger_count,
    trip_distance,
    total_amount
  FROM `bigquery-public-data.new_york_taxi_trips.tlc_yellow_trips_2015`
  WHERE trip_distance > 20
  LIMIT 100
```

### Desde terminal (bq CLI)

```bash
# Crear dataset
bq mk --dataset mi_proyecto:telemetria

# Subir datos
bq load \
  --source_format=PARQUET \
  telemetria.telemetry_day \
  gs://tu-bucket/raw/2026-03-14.parquet

# Hacer query
bq query --use_legacy_sql=false '
  SELECT vehicle_type, AVG(speed_kmh) as avg_speed
  FROM telemetria.telemetry_day
  GROUP BY vehicle_type
'

# Ver tablas
bq ls telemetria

# Ver esquema
bq show telemetria.raw_data
```

### Desde Python

```python
# pip install google-cloud-bigquery pandas-gbq
from google.cloud import bigquery
import pandas as pd

client = bigquery.Client()

# Subir DataFrame
df.to_gbq(
    destination_table="telemetria.fleet_profiles",
    project_id="tu-proyecto-id",
    if_exists="replace"
)

# Subir desde Cloud Storage
job_config = bigquery.LoadJobConfig(
    source_format=bigquery.SourceFormat.PARQUET,
)
uri = "gs://tu-bucket/raw/2026-03-14.parquet"
load_job = client.load_table_from_uri(uri, "telemetria.telemetry_raw", job_config=job_config)
load_job.result()

# Query
query = """
    SELECT vehicle_type, COUNT(*) as total, AVG(speed_kmh) as avg_speed
    FROM telemetria.telemetry_raw
    GROUP BY vehicle_type
"""
df_result = client.query(query).to_dataframe()

# Query con parametros
query = """
    SELECT * FROM telemetria.telemetry_raw
    WHERE vehicle_id = @vehicle_id
"""
job_config = bigquery.QueryJobConfig(
    query_parameters=[
        bigquery.ScalarQueryParameter("vehicle_id", "STRING", "V001"),
    ]
)
df_result = client.query(query, job_config=job_config).to_dataframe()
```

---

## BigQuery vs PostgreSQL: cuando usar cada uno

```
                    PostgreSQL              BigQuery
─────────────────   ──────────              ──────────
Latencia query      1-50 ms                 1-5 SEGUNDOS
Escritura           INSERT instantaneo      Batch (no real-time)
Datos en vivo       Si (consumers escriben) No (cargas en batch)
Coste fijo          $15-50/mes (VM)         $0 (sin datos)
Coste variable      $0 (ya pagaste VM)      $5/TB escaneado
Escala              ~500 GB maximo          Sin limite
Transacciones       Si (ACID)               No
Datos historicos    Caro mantener años      Barato ($0.02/GB/mes)
```

```
Arquitectura con ambos:

  Vehiculos → API → Kafka → Consumer → PostgreSQL
                                         │
                    (datos recientes,     │ dashboard_metrics
                     ultimos 7 dias)      │ → React (rapido, <100ms)
                                         │
                               Airflow cada noche:
                                         │
                          ┌──────────────┼──────────────┐
                          ▼              ▼              ▼
                    Cloud Storage    BigQuery      Borrar datos
                    (archivo)       (analisis)    viejos de PG
```

---

## En Airflow

```python
def cargar_a_bigquery(fecha: str):
    from google.cloud import bigquery

    client = bigquery.Client()
    uri = f"gs://tu-bucket/raw/{fecha}.parquet"
    table_ref = "tu-proyecto.telemetria.raw_data"

    job_config = bigquery.LoadJobConfig(
        source_format=bigquery.SourceFormat.PARQUET,
        write_disposition="WRITE_APPEND",
    )

    load_job = client.load_table_from_uri(uri, table_ref, job_config=job_config)
    load_job.result()
    print(f"Cargadas {load_job.output_rows} filas del {fecha}")
```
