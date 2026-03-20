# Airflow, Spark y Base de Datos: Estrategia de Procesamiento

## Quien ejecuta los calculos: Airflow vs Spark

Airflow **NO hace calculos**. Airflow es el **director de orquesta** que dice que ejecutar, cuando, y en que orden. Los calculos los hacen otros.

```
Analogia:

  Airflow = el director de cine
    "Primero graba la escena 1, luego la 2, si falla repite"
    No actua, no graba, solo dirige.

  Spark/Pandas/Python = los actores
    Hacen el trabajo real (procesar datos, entrenar modelos)

  El director no necesita saber actuar.
  Los actores no necesitan saber dirigir.
```

### Como funciona en la practica

```
Airflow NO ejecuta Spark dentro de si mismo.
Airflow LANZA Spark como un proceso/servicio separado.

┌─────────────────────────────────────────────────────────────┐
│  AIRFLOW (contenedor del orquestador)                       │
│                                                              │
│  DAG: pipeline_diario (3:00 AM)                             │
│                                                              │
│  Tarea 1: extraer_datos                                      │
│    → Ejecuta un script Python (Pandas)                       │
│    → Lo ejecuta DENTRO de Airflow                            │
│    → Porque es una tarea pequeña (query SQL + guardar)       │
│                                                              │
│  Tarea 2: procesar_pesado                                    │
│    → Opcion A: PythonOperator (Pandas dentro de Airflow)     │
│    → Opcion B: SparkSubmitOperator (lanza job en Spark)      │
│    → Opcion C: DataprocSubmitJobOperator (lanza en cloud)    │
│                                                              │
│  Tarea 3: entrenar_modelo                                    │
│    → Ejecuta script Python con sklearn                       │
│    → Dentro de Airflow si es pequeño                         │
│    → O lanza un contenedor dedicado con GPU                  │
│                                                              │
│  Tarea 4: archivar_en_cloud                                  │
│    → Ejecuta gsutil cp para subir a Cloud Storage            │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

### Opcion A: Todo dentro de Airflow (proyecto pequeño/mediano)

```
Cuando los datos caben en RAM de una maquina (< 32 GB):

┌──────────────────────────────────────┐
│  AIRFLOW (1 contenedor)              │
│                                      │
│  PythonOperator:                     │
│    import pandas as pd               │
│    df = pd.read_sql(query, conn)     │
│    result = df.groupby(...).mean()   │
│    result.to_sql("metrics", conn)    │
│                                      │
│  No necesitas Spark.                 │
│  Airflow ejecuta Pandas directamente.│
└──────────────────────────────────────┘

Cuando usar esto:
  - < 10 millones de filas por dia
  - Calculos simples (mean, std, groupby)
  - Tu servidor tiene 16-32 GB RAM
  - Es tu caso con 50 vehiculos
```

```python
# DAG de Airflow con Pandas (todo dentro de Airflow)
@task()
def procesar_dia(fecha: str):
    import pandas as pd
    from sqlalchemy import create_engine

    engine = create_engine("postgresql://user:pass@postgres/telemetria")

    # Leer datos del dia (cabe en RAM)
    df = pd.read_sql(f"""
        SELECT * FROM telemetry_raw
        WHERE DATE(timestamp) = '{fecha}'
    """, engine)

    # Procesar con Pandas
    metrics = df.groupby("vehicle_id").agg(
        avg_speed=("speed_kmh", "mean"),
        speed_std=("speed_kmh", "std"),
        avg_consumption=("fuel_consumption", "mean"),
        total_trips=("trip_id", "nunique"),
        harsh_braking=("acceleration", lambda x: (x < -3).sum()),
    ).reset_index()

    # Guardar resultado
    metrics.to_sql("dashboard_metrics", engine, if_exists="append", index=False)
```

### Opcion B: Airflow lanza Spark (proyecto grande)

```
Cuando los datos NO caben en RAM (> 32 GB):

┌────────────────────┐         ┌──────────────────────────┐
│  AIRFLOW            │         │  SPARK CLUSTER            │
│  (orquestador)      │         │  (procesamiento)          │
│                     │  lanza  │                           │
│  SparkSubmitOperator├────────>│  Master                   │
│                     │         │    ├── Worker 1 (8 CPU)   │
│  "ejecuta este      │         │    ├── Worker 2 (8 CPU)   │
│   script PySpark    │         │    └── Worker 3 (8 CPU)   │
│   en el cluster"    │         │                           │
│                     │  result │  Procesan 500 GB en       │
│  Siguiente tarea   <├─────────│  paralelo (20 min)        │
│                     │         │                           │
└────────────────────┘         └──────────────────────────┘

Airflow solo ESPERA a que Spark termine.
No usa RAM ni CPU de Airflow para el procesamiento.
```

```python
# DAG de Airflow que lanza Spark
from airflow.providers.apache.spark.operators.spark_submit import SparkSubmitOperator

procesar = SparkSubmitOperator(
    task_id="procesar_telemetria",
    application="/scripts/etl_spark.py",   # script PySpark
    conn_id="spark_default",               # conexion al cluster
    conf={
        "spark.executor.memory": "4g",
        "spark.executor.cores": "4",
    },
    dag=dag,
)
```

### Opcion C: Airflow lanza Spark en cloud (Google Dataproc)

```
┌────────────────────┐         ┌──────────────────────────┐
│  AIRFLOW            │         │  GOOGLE CLOUD             │
│                     │  1.crea │                           │
│  DataprocCreate    ├────────>│  Dataproc Cluster          │
│  Operator           │         │  (10 workers)             │
│                     │  2.lanza│                           │
│  DataprocSubmit    ├────────>│  Ejecuta PySpark           │
│  JobOperator        │         │  (procesa 1 TB)           │
│                     │  3.borra│                           │
│  DataprocDelete    ├────────>│  Cluster destruido         │
│  Operator           │         │  ($0 a partir de aqui)    │
│                     │         │                           │
└────────────────────┘         └──────────────────────────┘

Solo pagas por las 2 horas que el cluster existio.
```

```python
# DAG de Airflow que crea cluster Spark en Google Cloud
from airflow.providers.google.cloud.operators.dataproc import (
    DataprocCreateClusterOperator,
    DataprocSubmitPySparkJobOperator,
    DataprocDeleteClusterOperator,
)

# 1. Crear cluster
crear = DataprocCreateClusterOperator(
    task_id="crear_cluster",
    cluster_name="etl-cluster",
    num_workers=5,
    region="europe-west1",
)

# 2. Ejecutar procesamiento
procesar = DataprocSubmitPySparkJobOperator(
    task_id="procesar",
    main="gs://mi-bucket/scripts/etl.py",
    cluster_name="etl-cluster",
    region="europe-west1",
)

# 3. Borrar cluster (dejar de pagar)
borrar = DataprocDeleteClusterOperator(
    task_id="borrar_cluster",
    cluster_name="etl-cluster",
    region="europe-west1",
)

crear >> procesar >> borrar
```

### Cuando usar cada opcion

```
Opcion A (Pandas en Airflow):
  Datos: < 32 GB / dia
  Equipo: 1-5 personas
  Infra: 1 servidor
  Tu caso: 50 vehiculos = ~200 MB/dia → Pandas sobra

Opcion B (Spark propio):
  Datos: 32 GB - 1 TB / dia
  Equipo: 5-20 personas con equipo de infra
  Infra: cluster de 3-10 servidores propios

Opcion C (Spark en cloud):
  Datos: > 100 GB / dia o procesamiento esporadico
  Equipo: cualquier tamaño
  Infra: no tienes servidores propios
  Ventaja: pagas por uso, no mantienes nada
```

---

## Estrategia de Base de Datos

### El error comun: meter TODO en la BD

```
MAL: guardar todo para siempre en PostgreSQL

  Dia 1:     1M filas  → PostgreSQL rapido
  Dia 30:   30M filas  → PostgreSQL un poco lento
  Dia 180: 180M filas  → queries tardan 30 segundos
  Dia 365: 365M filas  → el dashboard no carga

  PostgreSQL no esta diseñado para almacenar billones de filas
  de telemetria. Funciona, pero se vuelve lento.
```

### La estrategia correcta: capas de datos

```
CAPA 1: Hot Data (PostgreSQL) — datos que se usan AHORA

  telemetry_raw:
    Solo ultimos 1-7 dias de datos crudos
    El consumer de Kafka escribe aqui
    Airflow lee de aqui para procesar
    Despues de procesar → se archiva y se borra

  dashboard_metrics:
    Datos AGREGADOS (avg, std, count por vehiculo/dia)
    Siempre pequena (50 vehiculos × 365 dias = 18,250 filas)
    El dashboard React lee de aqui (rapido)

  predictions:
    Resultados del modelo ML
    Pequena (50 vehiculos × predicciones recientes)

  alerts:
    Historial de alertas
    Relativamente pequena


CAPA 2: Warm Data (Cloud Storage Standard) — ultimo mes

  gs://bucket/raw/2026-03-14.parquet
  gs://bucket/raw/2026-03-13.parquet
  ...

  Si necesitas investigar algo del mes pasado:
    df = pd.read_parquet("gs://bucket/raw/2026-03-01.parquet")

  Acceso en segundos, coste $0.02/GB/mes


CAPA 3: Cold Data (Cloud Storage Nearline/Coldline) — historico

  gs://bucket/archive/2025/*.parquet

  Si necesitas reentrenar el modelo con datos de hace 6 meses:
    Los lees de aqui con Spark

  Acceso en segundos pero coste de lectura mas alto
  Almacenamiento: $0.004-0.01/GB/mes (muy barato)
```

### Que calculos hace la BD vs Spark vs Pandas

```
PostgreSQL (SQL) — calculos SIMPLES sobre datos recientes:

  -- Media de velocidad por tipo de vehiculo HOY
  SELECT vehicle_type, AVG(speed_kmh), STDDEV(speed_kmh)
  FROM telemetry_raw
  WHERE DATE(timestamp) = CURRENT_DATE
  GROUP BY vehicle_type;

  -- Vehiculos con temperatura anormalmente alta AHORA
  SELECT vehicle_id, MAX(battery_temp) as max_temp
  FROM telemetry_raw
  WHERE timestamp >= NOW() - INTERVAL '1 hour'
  GROUP BY vehicle_id
  HAVING MAX(battery_temp) > 45;

  -- Metricas para el dashboard (ya pre-calculadas)
  SELECT * FROM dashboard_metrics
  WHERE date >= CURRENT_DATE - INTERVAL '30 days';

  PostgreSQL hace esto en MILISEGUNDOS.
  No necesitas Pandas ni Spark para esto.
  El dashboard React puede llamar directamente a estos queries.


Pandas (Python) — calculos COMPLEJOS sobre datos de 1 dia:

  # Feature engineering (no se puede hacer bien en SQL)
  df['harsh_braking'] = (df['acceleration'] < -3).astype(int)
  df['night_trip'] = df['hour'].isin(range(22, 24)) | df['hour'].isin(range(0, 6))
  df['speed_consumption_ratio'] = df['speed_kmh'] / df['fuel_consumption']

  # Rolling windows
  df['consumption_7d_avg'] = df.groupby('vehicle_id')['consumption'].transform(
      lambda x: x.rolling(7).mean()
  )

  # Modelo ML
  model = RandomForestRegressor()
  model.fit(X_train, y_train)
  predictions = model.predict(X_new)

  Pandas hace esto en SEGUNDOS para datos de 1 dia.
  Corre dentro de Airflow (PythonOperator).


Spark — calculos sobre MESES/AÑOS de datos:

  # Reentrenar modelo con 1 año de datos (365 GB)
  df = spark.read.parquet("gs://bucket/raw/2025/*.parquet")

  # Agregar metricas mensuales para reporte anual
  monthly = df.groupBy("vehicle_id", F.month("timestamp")).agg(...)

  # Detectar tendencias a largo plazo
  # No cabe en RAM de 1 maquina → Spark distribuye

  Spark lo hace en MINUTOS con un cluster.
  Se lanza desde Airflow (SparkSubmitOperator).
```

### Flujo completo hora a hora

```
14:23:01  Coche V001 envia dato → API → Kafka → Consumer → PostgreSQL (telemetry_raw)
14:23:01  Consumer alertas: battery_temp=42 < 45 → OK, no alerta
14:23:01  Consumer metricas: messages_total++ → Prometheus → Grafana

14:25:00  Cron job (cada 5 min):
          SELECT vehicle_id, AVG(speed), AVG(consumption)
          FROM telemetry_raw
          WHERE timestamp >= NOW() - INTERVAL '5 min'
          → INSERT INTO dashboard_metrics
          → React Dashboard muestra datos actualizados

03:00:00  Airflow DAG "pipeline_diario":

          Tarea 1: extraer
            SELECT * FROM telemetry_raw WHERE DATE(timestamp) = '2026-03-14'
            → Guardar como DataFrame

          Tarea 2: archivar
            df.to_parquet("gs://bucket/raw/2026-03-14.parquet")
            → Subir a Cloud Storage

          Tarea 3: limpiar_bd
            DELETE FROM telemetry_raw WHERE DATE(timestamp) < '2026-03-08'
            → Solo mantener ultimos 7 dias en PostgreSQL

          Tarea 4: feature_engineering
            → Pandas: crear features (harsh_braking, night_ratio, etc.)

          Tarea 5: predecir
            model = joblib.load("models/consumption_v2.pkl")
            predictions = model.predict(features)
            → INSERT INTO predictions

          Tarea 6: detectar_anomalias
            → Isolation Forest sobre features
            → INSERT INTO alerts WHERE severity = 'HIGH'

          Tarea 7: notificar
            → Slack: "5 vehiculos necesitan revision"
            → Email: resumen ejecutivo diario

03:45:00  Pipeline completado. Todo listo para el dia siguiente.


SEMANAL (domingo 4:00 AM):
  Airflow DAG "reentrenamiento":

          Tarea 1: cargar_datos_recientes
            → Lee ultimas 4 semanas de Cloud Storage
            → Si > 32 GB: usar Spark
            → Si < 32 GB: Pandas suficiente

          Tarea 2: evaluar_modelo_actual
            → R2 del modelo en produccion con datos nuevos
            → Si R2 < 0.85: trigger reentrenamiento

          Tarea 3: reentrenar (si necesario)
            → Train/test split
            → GridSearchCV
            → Nuevo modelo

          Tarea 4: validar
            → Si nuevo modelo es mejor → guardar
            → Si no → mantener el actual

          Tarea 5: desplegar
            → Copiar modelo a /models/consumption_v3.pkl
            → Reiniciar API para cargar nuevo modelo
```

### Dimensionamiento de PostgreSQL

```
50 vehiculos × 1 msg/segundo × 86,400 s/dia = 4.3M filas/dia

Tamano por fila: ~200 bytes (15 columnas numericas)
Tamano por dia: 4.3M × 200B = ~860 MB/dia

Retencion 7 dias: 860 MB × 7 = ~6 GB en telemetry_raw
Retencion 30 dias: 860 MB × 30 = ~26 GB

Con indices: multiplicar por 2-3x
Total PostgreSQL: 15-80 GB segun retencion

Esto cabe sobradamente en un servidor con disco de 200 GB.
Un disco SSD de 200 GB en cloud cuesta ~$30/mes.

dashboard_metrics: 50 vehiculos × 365 dias × 200B = ~3.6 MB
  → Insignificante, siempre rapido


Para 50,000 vehiculos (empresa real):
  4.3M × 1000 = 4.3 BILLONES de filas/dia
  860 MB × 1000 = 860 GB/dia
  → PostgreSQL NO sirve para esto
  → Necesitas TimescaleDB (extension de PostgreSQL para time series)
     o ClickHouse o BigQuery
  → Y Spark para procesamiento batch
```

### Resumen: quien hace que

```
                        PostgreSQL    Pandas       Spark
                        (SQL)         (Python)     (distribuido)
────────────────────    ──────────    ──────────   ──────────
Guardar datos crudos    ✓ (consumer)
Queries simples (AVG)   ✓ (rapido)
Dashboard metrics       ✓ (pre-calc)
Feature engineering                   ✓
Entrenar modelo ML                    ✓
Procesar 1 dia                        ✓
Procesar 1 año                                     ✓
Reentrenar con 1 TB                                ✓

Orquestacion de todo: AIRFLOW
Airflow decide que usar en cada paso.
```
