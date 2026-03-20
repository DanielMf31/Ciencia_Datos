# Apache Spark con PySpark - Guia de Referencia

## Indice

1. [Que es Spark y cuando usarlo](#1-que-es-spark)
2. [Conceptos clave](#2-conceptos-clave)
3. [Instalacion](#3-instalacion)
4. [SparkSession: punto de entrada](#4-sparksession)
5. [DataFrame API (similar a Pandas)](#5-dataframe-api)
6. [Transformaciones y acciones](#6-transformaciones-y-acciones)
7. [SQL en Spark](#7-sql-en-spark)
8. [Leer y escribir datos](#8-leer-y-escribir-datos)
9. [Window functions](#9-window-functions)
10. [UDFs: funciones personalizadas](#10-udfs)
11. [Ejemplo real: ETL de telemetria](#11-ejemplo-real-etl-telemetria)
12. [Spark vs Pandas: comparativa](#12-spark-vs-pandas)

---

## 1. Que es Spark

Spark procesa datos **distribuidos en un cluster de maquinas**.

```
Pandas:                          Spark:
  1 maquina                        100 maquinas
  10 GB RAM max                    sin limite practico
  procesamiento secuencial         procesamiento paralelo

Cuando usar cada uno:
  Datos < 10 GB     → Pandas (mas rapido de desarrollar)
  Datos 10-100 GB   → Spark en 1 maquina (modo local)
  Datos > 100 GB    → Spark en cluster
  Datos en streaming → Spark Structured Streaming
```

---

## 2. Conceptos clave

| Concepto | Que es |
|----------|--------|
| **Driver** | Tu programa Python que controla todo |
| **Executor** | Proceso worker que ejecuta tareas en paralelo |
| **Partition** | Trozo de datos que un executor procesa |
| **Transformation** | Operacion lazy (no se ejecuta hasta que la necesitas) |
| **Action** | Operacion que dispara la ejecucion (collect, count, show) |
| **DAG** | Plan de ejecucion que Spark optimiza automaticamente |

```
Tu codigo Python (Driver)
    ↓
Spark crea un plan (DAG) de transformaciones
    ↓
Cuando haces una "action" (show, count, write):
    ↓
Spark optimiza el plan y lo reparte entre Executors
    ↓
Cada Executor procesa su particion en paralelo
    ↓
Resultado se devuelve al Driver
```

---

## 3. Instalacion

```bash
# PySpark (incluye Spark)
pip install pyspark

# Para desarrollo local no necesitas nada mas
# Para cluster: Spark ya instalado en los nodos
```

---

## 4. SparkSession

```python
from pyspark.sql import SparkSession

# Crear sesion (punto de entrada a Spark)
spark = SparkSession.builder \
    .appName("TelemetriaVehicular") \
    .master("local[*]") \
    .config("spark.sql.shuffle.partitions", "8") \
    .config("spark.driver.memory", "4g") \
    .getOrCreate()

# master options:
#   "local"      → 1 thread
#   "local[4]"   → 4 threads
#   "local[*]"   → todos los cores
#   "spark://cluster:7077" → cluster real

# Al terminar
spark.stop()
```

---

## 5. DataFrame API

```python
from pyspark.sql import functions as F
from pyspark.sql.types import StructType, StructField, StringType, FloatType

# --- Crear DataFrame desde datos ---
data = [
    ("V001", "electrico", 85.3, 42.1),
    ("V002", "gasolina", 60.0, 31.5),
    ("V003", "deportivo", 110.2, 38.7),
]
columns = ["vehicle_id", "vehicle_type", "speed_kmh", "battery_temp"]

df = spark.createDataFrame(data, columns)
df.show()
# +----------+------------+---------+------------+
# |vehicle_id|vehicle_type|speed_kmh|battery_temp|
# +----------+------------+---------+------------+
# |      V001|   electrico|     85.3|        42.1|
# |      V002|    gasolina|     60.0|        31.5|
# |      V003|   deportivo|    110.2|        38.7|
# +----------+------------+---------+------------+

# --- Operaciones basicas (como Pandas pero distribuidas) ---

# Seleccionar columnas
df.select("vehicle_id", "speed_kmh").show()

# Filtrar
df.filter(F.col("speed_kmh") > 80).show()
df.filter((F.col("speed_kmh") > 80) & (F.col("vehicle_type") == "electrico")).show()

# Nueva columna
df = df.withColumn("speed_ms", F.col("speed_kmh") / 3.6)

# Renombrar
df = df.withColumnRenamed("speed_kmh", "velocidad")

# Eliminar columna
df = df.drop("battery_temp")

# Ordenar
df.orderBy(F.col("speed_kmh").desc()).show()

# Valores unicos
df.select("vehicle_type").distinct().show()

# Estadisticas
df.describe().show()
df.select(
    F.mean("speed_kmh").alias("speed_mean"),
    F.stddev("speed_kmh").alias("speed_std"),
    F.min("speed_kmh").alias("speed_min"),
    F.max("speed_kmh").alias("speed_max"),
).show()
```

---

## 6. Transformaciones y acciones

```python
# TRANSFORMACIONES (lazy - no se ejecutan inmediatamente)
# Spark solo construye el plan, no procesa datos
df_filtered = df.filter(F.col("speed_kmh") > 80)     # no ejecuta
df_grouped = df_filtered.groupBy("vehicle_type")       # no ejecuta
df_result = df_grouped.agg(F.mean("speed_kmh"))       # no ejecuta

# ACCIONES (disparan la ejecucion de todo el plan)
df_result.show()         # ejecuta todo y muestra resultado
df_result.count()        # ejecuta y cuenta filas
df_result.collect()      # ejecuta y trae todo al driver (cuidado con datos grandes)
df_result.first()        # ejecuta y trae la primera fila
df_result.take(5)        # ejecuta y trae 5 filas
df_result.write.csv(...)  # ejecuta y escribe a disco

# Esto es EFICIENTE porque Spark optimiza el plan completo
# antes de ejecutar. Por ejemplo, si filtras y luego agrupas,
# Spark aplica el filtro ANTES de agrupar (pushdown).

# Ver el plan de ejecucion
df_result.explain()
# == Physical Plan ==
# HashAggregate(keys=[vehicle_type], functions=[avg(speed_kmh)])
# +- Filter (speed_kmh > 80)
#    +- Scan csv [vehicle_id, vehicle_type, speed_kmh, ...]
```

---

## 7. SQL en Spark

```python
# Spark soporta SQL completo sobre DataFrames

# Registrar DataFrame como tabla temporal
df.createOrReplaceTempView("telemetria")

# Consultar con SQL
result = spark.sql("""
    SELECT vehicle_type,
           COUNT(*) as total_registros,
           AVG(speed_kmh) as speed_mean,
           MAX(battery_temp) as temp_max
    FROM telemetria
    WHERE speed_kmh > 0
    GROUP BY vehicle_type
    ORDER BY speed_mean DESC
""")
result.show()

# Consultas complejas
anomalias = spark.sql("""
    SELECT vehicle_id,
           AVG(battery_temp) as avg_temp,
           MAX(battery_temp) as max_temp,
           COUNT(*) as readings
    FROM telemetria
    WHERE battery_temp > 45
    GROUP BY vehicle_id
    HAVING COUNT(*) > 10
    ORDER BY max_temp DESC
""")

# Window functions en SQL
ranking = spark.sql("""
    SELECT vehicle_id,
           speed_kmh,
           vehicle_type,
           ROW_NUMBER() OVER (PARTITION BY vehicle_type ORDER BY speed_kmh DESC) as rank
    FROM telemetria
""")
```

---

## 8. Leer y escribir datos

```python
# --- Leer CSV ---
df = spark.read \
    .option("header", "true") \
    .option("inferSchema", "true") \
    .csv("data/raw/telemetry/*.csv")  # lee TODOS los CSV con glob

# --- Leer Parquet (formato recomendado para big data) ---
df = spark.read.parquet("data/processed/telemetria/")

# --- Leer JSON ---
df = spark.read.json("data/events/*.json")

# --- Leer desde base de datos ---
df = spark.read \
    .format("jdbc") \
    .option("url", "jdbc:postgresql://db:5432/telemetria") \
    .option("dbtable", "telemetry_raw") \
    .option("user", "admin") \
    .option("password", "secret") \
    .load()


# --- Escribir ---

# Parquet (recomendado: comprimido, columnar, rapido)
df.write \
    .mode("overwrite") \
    .partitionBy("vehicle_type") \
    .parquet("data/processed/telemetria_clean/")
# Crea: data/processed/telemetria_clean/vehicle_type=electrico/part-00000.parquet
#        data/processed/telemetria_clean/vehicle_type=gasolina/part-00000.parquet

# CSV
df.write.mode("overwrite").option("header", "true").csv("output/csv/")

# Una sola particion (un solo archivo)
df.coalesce(1).write.mode("overwrite").csv("output/single_file/")

# Modos de escritura:
#   "overwrite"      → reemplazar si existe
#   "append"         → anadir al final
#   "ignore"         → no hacer nada si existe
#   "errorifexists"  → error si existe (default)
```

---

## 9. Window functions

```python
from pyspark.sql.window import Window

# Ventana por vehiculo, ordenada por timestamp
window_vehicle = Window.partitionBy("vehicle_id").orderBy("timestamp")

# Rolling average (ultimos 10 registros)
window_rolling = Window.partitionBy("vehicle_id") \
    .orderBy("timestamp") \
    .rowsBetween(-9, 0)  # 10 filas: actual + 9 anteriores

df = df.withColumn("speed_rolling_avg",
                   F.avg("speed_kmh").over(window_rolling))

df = df.withColumn("speed_rolling_std",
                   F.stddev("speed_kmh").over(window_rolling))

# Diferencia con registro anterior (delta)
df = df.withColumn("speed_prev", F.lag("speed_kmh", 1).over(window_vehicle))
df = df.withColumn("speed_delta", F.col("speed_kmh") - F.col("speed_prev"))

# Acumulado
df = df.withColumn("consumption_cumsum",
                   F.sum("fuel_consumption").over(
                       Window.partitionBy("vehicle_id", "trip_id")
                       .orderBy("timestamp")
                       .rowsBetween(Window.unboundedPreceding, 0)
                   ))

# Ranking
window_rank = Window.partitionBy("vehicle_type").orderBy(F.col("speed_kmh").desc())
df = df.withColumn("speed_rank", F.rank().over(window_rank))
```

---

## 10. UDFs

```python
from pyspark.sql.functions import udf
from pyspark.sql.types import StringType, FloatType

# UDF: User Defined Function
# Cuando necesitas logica Python custom que Spark no tiene built-in

# --- UDF basica ---
@udf(returnType=StringType())
def clasificar_velocidad(speed):
    if speed is None:
        return "desconocido"
    elif speed < 30:
        return "lento"
    elif speed < 80:
        return "normal"
    elif speed < 110:
        return "rapido"
    else:
        return "muy_rapido"

df = df.withColumn("speed_category", clasificar_velocidad(F.col("speed_kmh")))


# --- UDF con modelo ML ---
import joblib
from pyspark.sql.types import FloatType

# Cargar modelo en el driver
model = joblib.load("models/consumption_model.pkl")

# Broadcast: enviar modelo a todos los executors (una sola vez)
model_broadcast = spark.sparkContext.broadcast(model)

@udf(returnType=FloatType())
def predict_consumption(speed, battery_temp, rpm):
    model = model_broadcast.value
    features = [[speed, battery_temp, rpm]]
    return float(model.predict(features)[0])

df = df.withColumn("predicted_consumption",
                   predict_consumption(
                       F.col("speed_kmh"),
                       F.col("battery_temp"),
                       F.col("motor_rpm")
                   ))

# NOTA: UDFs son lentas (serializacion Python).
# Prefiere funciones built-in de Spark cuando sea posible.
# Para ML a escala, usa Spark MLlib en lugar de UDFs con sklearn.
```

---

## 11. Ejemplo real: ETL de telemetria

```python
"""
Pipeline ETL completo con PySpark para telemetria vehicular.
Procesa millones de registros en paralelo.
"""
from pyspark.sql import SparkSession, functions as F
from pyspark.sql.window import Window

spark = SparkSession.builder \
    .appName("ETL_Telemetria") \
    .master("local[*]") \
    .config("spark.driver.memory", "4g") \
    .getOrCreate()


# =============================================
# 1. EXTRAER: Leer todos los CSV de telemetria
# =============================================

telemetria = spark.read \
    .option("header", "true") \
    .option("inferSchema", "true") \
    .csv("data/raw/telemetry/telemetry_*.csv")

fleet = spark.read \
    .option("header", "true") \
    .option("inferSchema", "true") \
    .csv("data/raw/fleet_profiles.csv")

print(f"Registros telemetria: {telemetria.count():,}")
print(f"Vehiculos en flota: {fleet.count()}")


# =============================================
# 2. LIMPIAR: Validar y corregir datos
# =============================================

# Eliminar registros con valores imposibles
clean = telemetria \
    .filter(F.col("speed_kmh").between(0, 250)) \
    .filter(F.col("battery_temp").between(-10, 80)) \
    .filter(F.col("fuel_consumption_rate") > 0) \
    .filter(F.col("motor_rpm").between(0, 10000))

# Parsear timestamp
clean = clean.withColumn("timestamp", F.to_timestamp("timestamp"))
clean = clean.withColumn("date", F.to_date("timestamp"))
clean = clean.withColumn("hour", F.hour("timestamp"))
clean = clean.withColumn("day_of_week", F.dayofweek("timestamp"))

# Merge con fleet
clean = clean.join(
    fleet.select("vehicle_id", "vehicle_type", "fuel_type"),
    on="vehicle_id",
    how="left"
)

eliminados = telemetria.count() - clean.count()
print(f"Registros eliminados: {eliminados:,}")


# =============================================
# 3. TRANSFORMAR: Agregar metricas por vehiculo/dia
# =============================================

# Metricas diarias por vehiculo
daily_metrics = clean.groupBy("vehicle_id", "vehicle_type", "date").agg(
    F.count("*").alias("readings"),
    F.countDistinct("trip_id").alias("total_trips"),

    # Velocidad
    F.mean("speed_kmh").alias("avg_speed"),
    F.stddev("speed_kmh").alias("speed_std"),
    F.max("speed_kmh").alias("max_speed"),

    # Consumo
    F.mean("fuel_consumption_rate").alias("avg_consumption"),
    F.stddev("fuel_consumption_rate").alias("consumption_std"),

    # Bateria
    F.mean("battery_temp").alias("avg_battery_temp"),
    F.max("battery_temp").alias("max_battery_temp"),

    # Conduccion agresiva
    F.sum(F.when(F.col("acceleration_ms2") < -3, 1).otherwise(0)).alias("harsh_braking"),
    F.sum(F.when(F.col("acceleration_ms2") > 3, 1).otherwise(0)).alias("harsh_accel"),

    # Patrones temporales
    F.sum(F.when(F.col("hour").between(22, 23) | F.col("hour").between(0, 5), 1)
          .otherwise(0)).alias("night_readings"),
)

# Ratios
daily_metrics = daily_metrics \
    .withColumn("night_ratio",
                F.col("night_readings") / F.col("readings")) \
    .withColumn("harsh_events_per_trip",
                (F.col("harsh_braking") + F.col("harsh_accel")) / F.col("total_trips"))


# =============================================
# 4. ENRIQUECER: Tendencias con window functions
# =============================================

# Rolling average de 7 dias
window_7d = Window.partitionBy("vehicle_id") \
    .orderBy("date") \
    .rowsBetween(-6, 0)

daily_metrics = daily_metrics \
    .withColumn("consumption_7d_avg", F.avg("avg_consumption").over(window_7d)) \
    .withColumn("battery_temp_7d_avg", F.avg("avg_battery_temp").over(window_7d))

# Tendencia: diferencia con semana anterior
daily_metrics = daily_metrics.withColumn(
    "consumption_trend",
    F.col("avg_consumption") - F.lag("avg_consumption", 7).over(
        Window.partitionBy("vehicle_id").orderBy("date")
    )
)


# =============================================
# 5. DETECTAR ANOMALIAS
# =============================================

# Calcular media y std por tipo de vehiculo
stats = daily_metrics.groupBy("vehicle_type").agg(
    F.mean("avg_consumption").alias("type_consumption_mean"),
    F.stddev("avg_consumption").alias("type_consumption_std"),
    F.mean("avg_battery_temp").alias("type_temp_mean"),
    F.stddev("avg_battery_temp").alias("type_temp_std"),
)

daily_metrics = daily_metrics.join(stats, on="vehicle_type", how="left")

# Z-score anomalies
daily_metrics = daily_metrics \
    .withColumn("consumption_zscore",
                (F.col("avg_consumption") - F.col("type_consumption_mean"))
                / F.col("type_consumption_std")) \
    .withColumn("temp_zscore",
                (F.col("avg_battery_temp") - F.col("type_temp_mean"))
                / F.col("type_temp_std")) \
    .withColumn("is_anomaly",
                (F.abs(F.col("consumption_zscore")) > 3)
                | (F.abs(F.col("temp_zscore")) > 3))


# =============================================
# 6. GUARDAR: Parquet particionado
# =============================================

# Guardar metricas diarias
daily_metrics.write \
    .mode("overwrite") \
    .partitionBy("vehicle_type", "date") \
    .parquet("data/processed/daily_metrics/")

# Guardar anomalias por separado
anomalies = daily_metrics.filter(F.col("is_anomaly") == True)
anomalies.write \
    .mode("overwrite") \
    .parquet("data/processed/anomalies/")

# Resumen
print(f"Dias procesados: {daily_metrics.select('date').distinct().count()}")
print(f"Anomalias detectadas: {anomalies.count()}")

spark.stop()
```

---

## 12. Spark vs Pandas: comparativa de sintaxis

```python
# PANDAS                              # SPARK
import pandas as pd                    from pyspark.sql import functions as F

df = pd.read_csv("data.csv")          df = spark.read.csv("data.csv", header=True)

df.head()                              df.show(5)
df.shape                               df.count(), len(df.columns)
df.dtypes                              df.dtypes  # o df.printSchema()
df.describe()                          df.describe().show()

df['col']                              df.select("col")
df[['a', 'b']]                        df.select("a", "b")

df[df['x'] > 5]                       df.filter(F.col("x") > 5)
df[df['x'].isin([1,2])]               df.filter(F.col("x").isin([1,2]))

df['new'] = df['a'] + df['b']         df = df.withColumn("new", F.col("a") + F.col("b"))

df.groupby('type').mean()              df.groupBy("type").agg(F.mean("*"))
df.groupby('type')['x'].agg(['mean']) df.groupBy("type").agg(F.mean("x"))

df.sort_values('x', ascending=False)   df.orderBy(F.col("x").desc())

df.drop_duplicates()                   df.dropDuplicates()
df.fillna(0)                           df.fillna(0)
df.dropna()                            df.dropna()

pd.merge(df1, df2, on='id')           df1.join(df2, on="id", how="inner")

df.to_csv("output.csv")               df.write.csv("output/")
df.to_parquet("output.parquet")        df.write.parquet("output/")
```
