# Apache Airflow - Guia de Referencia con Python

## Indice

1. [Que es Airflow](#1-que-es-airflow)
2. [Conceptos clave](#2-conceptos-clave)
3. [Instalacion y setup](#3-instalacion-y-setup)
4. [DAG basico](#4-dag-basico)
5. [PythonOperator: ejecutar funciones](#5-pythonoperator)
6. [Pasar datos entre tareas (XCom)](#6-pasar-datos-entre-tareas-xcom)
7. [BashOperator: ejecutar comandos](#7-bashoperator)
8. [Dependencias entre tareas](#8-dependencias-entre-tareas)
9. [Scheduling: programacion temporal](#9-scheduling)
10. [Branching: logica condicional](#10-branching)
11. [Reintentos y manejo de errores](#11-reintentos-y-manejo-de-errores)
12. [Sensores: esperar eventos externos](#12-sensores)
13. [TaskFlow API (moderna, Python nativo)](#13-taskflow-api)
14. [Ejemplo real: pipeline de telemetria](#14-ejemplo-real-pipeline-de-telemetria)
15. [Ejemplo real: reentrenamiento de modelo](#15-ejemplo-real-reentrenamiento-de-modelo)
16. [Docker Compose para desarrollo](#16-docker-compose-para-desarrollo)

---

## 1. Que es Airflow

Airflow es un **orquestador de workflows**. Define tareas, sus dependencias, y las ejecuta en el orden correcto con scheduling, reintentos y monitoreo.

```
No es:
  - Un procesador de datos (no reemplaza Spark/Pandas)
  - Una cola de mensajes (no reemplaza Kafka/Redis)
  - Un cron (aunque puede hacer lo mismo, es mucho mas potente)

Es:
  - El "director de orquesta" que dice: primero extraer datos,
    luego limpiarlos, luego entrenar el modelo, luego desplegar
  - Con reintentos, alertas, logs, UI web, y dependencias complejas
```

```
Airflow UI (web):

 DAG: pipeline_telemetria_diario     [Ultima ejecucion: 03:00 OK]

 ┌──────────┐    ┌──────────┐    ┌──────────┐    ┌──────────┐
 │ Extraer  │───>│ Limpiar  │───>│ Agregar  │───>│ Reportar │
 │   (OK)   │    │   (OK)   │    │   (OK)   │    │   (OK)   │
 └──────────┘    └──────────┘    └──────────┘    └──────────┘

 Historial: Hoy OK | Ayer OK | Anteayer FALLO (reintento 2: OK) | ...
```

---

## 2. Conceptos clave

| Concepto | Que es | Analogia |
|----------|--------|----------|
| **DAG** | Directed Acyclic Graph: el workflow completo | Un Makefile o pipeline CI/CD |
| **Task** | Una unidad de trabajo individual | Un step en GitHub Actions |
| **Operator** | Tipo de tarea (Python, Bash, SQL, etc.) | La "accion" del step |
| **Schedule** | Cuando se ejecuta el DAG | El cron expression |
| **XCom** | Datos compartidos entre tareas | Variables de entorno entre steps |
| **Sensor** | Tarea que espera a que algo ocurra | Un polling/wait |
| **Pool** | Limite de tareas concurrentes | Thread pool |
| **Connection** | Credenciales a servicios externos | Secrets/env vars |
| **Variable** | Configuracion global reutilizable | Settings/config |

---

## 3. Instalacion y setup

```bash
# Instalar Airflow (version standalone para desarrollo)
pip install apache-airflow

# Inicializar base de datos y crear usuario admin
airflow db init
airflow users create \
    --username admin \
    --firstname Admin \
    --lastname User \
    --role Admin \
    --email admin@example.com \
    --password admin

# Lanzar (en dos terminales separadas)
airflow webserver --port 8080   # UI web
airflow scheduler               # ejecutor de tareas

# Abrir en navegador: http://localhost:8080
# Los DAGs se colocan en ~/airflow/dags/
```

---

## 4. DAG basico

```python
# ~/airflow/dags/mi_primer_dag.py

from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator

# Configuracion por defecto para todas las tareas del DAG
default_args = {
    'owner': 'data-team',
    'depends_on_past': False,       # no depender de ejecuciones anteriores
    'email': ['equipo@empresa.com'],
    'email_on_failure': True,       # email si falla
    'email_on_retry': False,
    'retries': 2,                   # reintentar 2 veces
    'retry_delay': timedelta(minutes=5),  # esperar 5 min entre reintentos
}

# Definir el DAG
dag = DAG(
    dag_id='mi_primer_dag',
    default_args=default_args,
    description='Mi primer DAG de ejemplo',
    schedule_interval='0 3 * * *',  # ejecutar a las 3:00 AM todos los dias
    start_date=datetime(2025, 1, 1),
    catchup=False,                  # no ejecutar fechas pasadas
    tags=['ejemplo', 'tutorial'],
)

# Definir funciones (la logica real)
def extraer_datos():
    print("Extrayendo datos del API...")
    # requests.get("https://api.vehiculos.com/telemetria")
    return "datos extraidos"

def procesar_datos():
    print("Limpiando y transformando...")
    # pandas, limpieza, transformaciones

def guardar_resultados():
    print("Guardando en base de datos...")
    # INSERT INTO resultados ...

# Crear tareas
tarea_extraer = PythonOperator(
    task_id='extraer_datos',
    python_callable=extraer_datos,
    dag=dag,
)

tarea_procesar = PythonOperator(
    task_id='procesar_datos',
    python_callable=procesar_datos,
    dag=dag,
)

tarea_guardar = PythonOperator(
    task_id='guardar_resultados',
    python_callable=guardar_resultados,
    dag=dag,
)

# Definir orden de ejecucion
tarea_extraer >> tarea_procesar >> tarea_guardar
# Equivalente: tarea_extraer.set_downstream(tarea_procesar)
```

---

## 5. PythonOperator

```python
from airflow.operators.python import PythonOperator

# --- Funcion simple ---
def saludar():
    print("Hola desde Airflow!")

tarea = PythonOperator(
    task_id='saludar',
    python_callable=saludar,
    dag=dag,
)


# --- Funcion con argumentos ---
def procesar_vehiculo(vehicle_id, fecha):
    print(f"Procesando {vehicle_id} para {fecha}")
    # logica...

tarea = PythonOperator(
    task_id='procesar_v001',
    python_callable=procesar_vehiculo,
    op_kwargs={                    # argumentos como dict
        'vehicle_id': 'V001',
        'fecha': '2025-01-15',
    },
    dag=dag,
)


# --- Usando la fecha de ejecucion del DAG ---
def procesar_dia(**context):
    # Airflow inyecta contexto automaticamente
    fecha_ejecucion = context['ds']           # '2025-01-15' (string)
    fecha_logica = context['logical_date']    # datetime object
    run_id = context['run_id']

    print(f"Procesando datos del dia: {fecha_ejecucion}")
    # Cargar datos de ESE dia especifico
    # df = pd.read_csv(f"data/telemetria_{fecha_ejecucion}.csv")

tarea = PythonOperator(
    task_id='procesar_dia',
    python_callable=procesar_dia,
    provide_context=True,          # inyectar context como **kwargs
    dag=dag,
)
```

---

## 6. Pasar datos entre tareas (XCom)

```python
# XCom = "cross-communication" entre tareas
# Para datos PEQUENOS (< 48KB). Para datos grandes usa archivos/S3/DB.

def extraer(**context):
    datos = {"total_registros": 15000, "vehiculos_activos": 48}
    # Guardar en XCom (via return o push)
    return datos  # el return automaticamente hace xcom_push

def transformar(**context):
    # Leer el XCom de la tarea anterior
    ti = context['ti']  # task instance
    datos = ti.xcom_pull(task_ids='extraer')
    print(f"Registros a procesar: {datos['total_registros']}")

    registros_limpios = datos['total_registros'] - 200  # quitar invalidos
    return {"registros_limpios": registros_limpios}

def reportar(**context):
    ti = context['ti']
    datos_raw = ti.xcom_pull(task_ids='extraer')
    datos_clean = ti.xcom_pull(task_ids='transformar')

    print(f"Raw: {datos_raw['total_registros']}")
    print(f"Clean: {datos_clean['registros_limpios']}")
    print(f"Eliminados: {datos_raw['total_registros'] - datos_clean['registros_limpios']}")

t1 = PythonOperator(task_id='extraer', python_callable=extraer, dag=dag)
t2 = PythonOperator(task_id='transformar', python_callable=transformar, dag=dag)
t3 = PythonOperator(task_id='reportar', python_callable=reportar, dag=dag)

t1 >> t2 >> t3
```

---

## 7. BashOperator

```python
from airflow.operators.bash import BashOperator

# Ejecutar comandos de shell
tarea_bash = BashOperator(
    task_id='listar_archivos',
    bash_command='ls -la /data/telemetria/ | wc -l',
    dag=dag,
)

# Con templates (Airflow sustituye variables)
tarea_descargar = BashOperator(
    task_id='descargar_datos',
    bash_command='curl -o /data/raw/{{ ds }}.json https://api.example.com/data?date={{ ds }}',
    # {{ ds }} se reemplaza por la fecha de ejecucion: 2025-01-15
    dag=dag,
)

# Ejecutar un script Python externo
tarea_script = BashOperator(
    task_id='ejecutar_etl',
    bash_command='cd /opt/proyecto && python scripts/etl.py --date {{ ds }}',
    dag=dag,
)
```

---

## 8. Dependencias entre tareas

```python
# --- Secuencial ---
t1 >> t2 >> t3
# t1 primero, luego t2, luego t3


# --- Paralelo ---
t1 >> [t2, t3] >> t4
# t1 primero
# luego t2 y t3 en paralelo
# cuando AMBOS terminen, t4

#   t1 ──┬──> t2 ──┬──> t4
#        └──> t3 ──┘


# --- Fan-out / Fan-in ---
[t1, t2] >> t3 >> [t4, t5]
#   t1 ──┐        ┌──> t4
#        ├──> t3 ──┤
#   t2 ──┘        └──> t5


# --- Dependencias complejas ---
t1 >> t2
t1 >> t3
t2 >> t4
t3 >> t4
t4 >> t5

#   t1 ──┬──> t2 ──┐
#        │         ├──> t4 ──> t5
#        └──> t3 ──┘


# --- Cross-dependencies (todos con todos) ---
from airflow.models.baseoperator import cross_downstream

cross_downstream([t1, t2], [t3, t4])
# t1 >> t3, t1 >> t4, t2 >> t3, t2 >> t4
```

---

## 9. Scheduling

```python
# Expresiones cron estandar
DAG(schedule_interval='0 3 * * *')       # 3:00 AM todos los dias
DAG(schedule_interval='0 */6 * * *')     # cada 6 horas
DAG(schedule_interval='0 3 * * 1')       # lunes a las 3:00 AM
DAG(schedule_interval='0 3 1 * *')       # primer dia de cada mes
DAG(schedule_interval='0 0 * * 5')       # viernes a medianoche

# Presets de Airflow
DAG(schedule_interval='@daily')          # una vez al dia (medianoche)
DAG(schedule_interval='@hourly')         # cada hora
DAG(schedule_interval='@weekly')         # cada domingo medianoche
DAG(schedule_interval='@monthly')        # primer dia del mes
DAG(schedule_interval='@yearly')         # 1 de enero

# Sin schedule (ejecucion manual o por trigger)
DAG(schedule_interval=None)

# Con timedelta
from datetime import timedelta
DAG(schedule_interval=timedelta(hours=2))  # cada 2 horas


# --- Catchup ---
# Si el DAG empezo el 1 de enero y hoy es 15 de enero:
DAG(
    start_date=datetime(2025, 1, 1),
    catchup=True,   # ejecutar los 14 dias que se "perdio"
    catchup=False,   # solo ejecutar de hoy en adelante
)
```

---

## 10. Branching

```python
from airflow.operators.python import BranchPythonOperator
from airflow.operators.empty import EmptyOperator

def decidir_accion(**context):
    """Decide que rama ejecutar basandose en condiciones."""
    ti = context['ti']
    metricas = ti.xcom_pull(task_ids='evaluar_modelo')

    if metricas['r2'] < 0.80:
        return 'reentrenar_modelo'    # ejecutar esta tarea
    elif metricas['drift_detectado']:
        return 'alerta_drift'         # o esta
    else:
        return 'todo_ok'              # o esta

evaluar = PythonOperator(task_id='evaluar_modelo', ...)

# BranchPythonOperator elige que camino seguir
decidir = BranchPythonOperator(
    task_id='decidir',
    python_callable=decidir_accion,
    dag=dag,
)

reentrenar = PythonOperator(task_id='reentrenar_modelo', ...)
alerta = PythonOperator(task_id='alerta_drift', ...)
ok = EmptyOperator(task_id='todo_ok')
notificar = PythonOperator(
    task_id='notificar',
    trigger_rule='none_failed_min_one_success',  # ejecutar si alguna rama llego
)

evaluar >> decidir >> [reentrenar, alerta, ok] >> notificar

# Visualizacion:
#                        ┌──> reentrenar ──┐
#  evaluar ──> decidir ──┼──> alerta ──────┼──> notificar
#                        └──> todo_ok ─────┘
#
# Solo UNA rama se ejecuta segun la condicion
```

---

## 11. Reintentos y manejo de errores

```python
from airflow.operators.python import PythonOperator
from datetime import timedelta

# --- Configuracion por tarea ---
tarea_fragil = PythonOperator(
    task_id='llamar_api_externa',
    python_callable=llamar_api,
    retries=5,                              # reintentar 5 veces
    retry_delay=timedelta(minutes=2),       # esperar 2 min entre reintentos
    retry_exponential_backoff=True,         # 2min, 4min, 8min, 16min, 32min
    max_retry_delay=timedelta(minutes=30),  # maximo 30 min entre reintentos
    execution_timeout=timedelta(minutes=10), # timeout de 10 min por ejecucion
    dag=dag,
)


# --- Callbacks en caso de fallo/exito ---
def alerta_fallo(context):
    """Se ejecuta cuando una tarea falla definitivamente."""
    task_id = context['task_instance'].task_id
    error = context['exception']
    fecha = context['ds']

    # Enviar alerta a Slack
    print(f"FALLO: {task_id} el {fecha}: {error}")
    # requests.post(SLACK_WEBHOOK, json={"text": f"..."})

def confirmar_exito(context):
    """Se ejecuta cuando una tarea se completa."""
    print(f"OK: {context['task_instance'].task_id}")

tarea = PythonOperator(
    task_id='tarea_importante',
    python_callable=mi_funcion,
    on_failure_callback=alerta_fallo,
    on_success_callback=confirmar_exito,
    dag=dag,
)


# --- Callback a nivel de DAG (cuando todo el DAG falla) ---
dag = DAG(
    dag_id='pipeline_critico',
    on_failure_callback=alerta_fallo,  # si CUALQUIER tarea falla
    # ...
)


# --- Trigger rules (cuando ejecutar basado en estado de dependencias) ---
from airflow.utils.trigger_rule import TriggerRule

limpieza = PythonOperator(
    task_id='limpieza_final',
    python_callable=limpiar_archivos_temporales,
    trigger_rule=TriggerRule.ALL_DONE,  # ejecutar SIEMPRE, aunque otras fallen
    # Otras opciones:
    #   ALL_SUCCESS    (default) - solo si todas las dependencias exitosas
    #   ALL_FAILED     - solo si todas fallaron
    #   ONE_SUCCESS    - si al menos una exitosa
    #   ONE_FAILED     - si al menos una fallo
    #   NONE_FAILED    - si ninguna fallo (incluye skipped)
    #   ALL_DONE       - cuando todas terminaron (exito o fallo)
    dag=dag,
)
```

---

## 12. Sensores

```python
from airflow.sensors.filesystem import FileSensor
from airflow.sensors.external_task import ExternalTaskSensor
from airflow.sensors.python import PythonSensor

# --- Esperar a que un archivo exista ---
esperar_archivo = FileSensor(
    task_id='esperar_datos_diarios',
    filepath='/data/raw/telemetria_{{ ds }}.csv',
    poke_interval=60,       # verificar cada 60 segundos
    timeout=3600,           # timeout despues de 1 hora
    mode='poke',            # 'poke' = bloquea un worker
                            # 'reschedule' = libera el worker entre checks
    dag=dag,
)


# --- Esperar a que otro DAG termine ---
esperar_otro_dag = ExternalTaskSensor(
    task_id='esperar_ingestion',
    external_dag_id='pipeline_ingestion',
    external_task_id='tarea_final',  # esperar a esta tarea especifica
    timeout=7200,
    dag=dag,
)


# --- Sensor custom con Python ---
def verificar_api_disponible():
    """Devuelve True si la API responde, False si no."""
    try:
        response = requests.get("https://api.vehiculos.com/health", timeout=5)
        return response.status_code == 200
    except Exception:
        return False

esperar_api = PythonSensor(
    task_id='esperar_api',
    python_callable=verificar_api_disponible,
    poke_interval=30,
    timeout=600,
    dag=dag,
)

# Orden: esperar condiciones -> ejecutar procesamiento
[esperar_archivo, esperar_api] >> procesar_datos
```

---

## 13. TaskFlow API

```python
# Forma MODERNA de escribir DAGs (Airflow 2.x)
# Mas limpia, usa decoradores Python nativos

from airflow.decorators import dag, task
from datetime import datetime

@dag(
    dag_id='pipeline_moderno',
    schedule='0 3 * * *',
    start_date=datetime(2025, 1, 1),
    catchup=False,
    tags=['telemetria', 'ml'],
)
def pipeline_telemetria():

    @task()
    def extraer(fecha: str) -> dict:
        """Extraer datos del dia."""
        # df = pd.read_csv(f"data/telemetria_{fecha}.csv")
        n_registros = 15000  # simulado
        return {"fecha": fecha, "registros": n_registros}

    @task()
    def limpiar(datos: dict) -> dict:
        """Limpiar datos."""
        registros_limpios = datos["registros"] - 200
        return {**datos, "registros_limpios": registros_limpios}

    @task()
    def agregar(datos: dict) -> dict:
        """Agregar metricas por vehiculo."""
        return {**datos, "vehiculos_procesados": 48}

    @task()
    def evaluar_modelo(datos: dict) -> dict:
        """Evaluar rendimiento del modelo con datos nuevos."""
        # model = joblib.load("models/consumption.pkl")
        # predictions = model.predict(X_new)
        r2 = 0.87  # simulado
        return {"r2": r2, "drift": r2 < 0.80}

    @task.branch()
    def decidir(metricas: dict) -> str:
        """Decidir si reentrenar."""
        if metricas["drift"]:
            return "reentrenar"
        return "reportar"

    @task()
    def reentrenar():
        print("Reentrenando modelo...")
        # model.fit(X_train, y_train)
        # joblib.dump(model, "models/consumption_v2.pkl")

    @task()
    def reportar():
        print("Todo OK, generando reporte...")
        # enviar email/slack con metricas

    # Definir el flujo (las dependencias se infieren del paso de datos)
    datos_raw = extraer(fecha="{{ ds }}")
    datos_limpios = limpiar(datos_raw)
    datos_agregados = agregar(datos_limpios)
    metricas = evaluar_modelo(datos_agregados)
    decision = decidir(metricas)
    decision >> [reentrenar(), reportar()]


# Instanciar el DAG
pipeline_telemetria()
```

---

## 14. Ejemplo real: pipeline de telemetria

```python
"""
Pipeline diario que procesa telemetria de la flota vehicular.

Flujo:
  1. Verificar que los datos del dia existen
  2. Extraer de la base de datos
  3. Limpiar (nulos, outliers, formatos)
  4. Agregar metricas por vehiculo
  5. Detectar anomalias
  6. Actualizar dashboard
  7. Enviar alertas si hay anomalias criticas
"""
from airflow.decorators import dag, task
from datetime import datetime, timedelta
import json


@dag(
    dag_id='telemetria_flota_diario',
    schedule='0 3 * * *',
    start_date=datetime(2025, 1, 1),
    catchup=False,
    tags=['telemetria', 'produccion'],
    default_args={
        'owner': 'data-team',
        'retries': 3,
        'retry_delay': timedelta(minutes=5),
    },
)
def telemetria_flota():

    @task()
    def extraer_telemetria(fecha: str) -> str:
        """Extraer telemetria del dia desde PostgreSQL/TimescaleDB."""
        import pandas as pd
        # from sqlalchemy import create_engine

        # engine = create_engine("postgresql://user:pass@db:5432/telemetria")
        # query = f"""
        #     SELECT * FROM telemetry_raw
        #     WHERE DATE(timestamp) = '{fecha}'
        # """
        # df = pd.read_sql(query, engine)

        output_path = f"/data/staging/telemetria_{fecha}.parquet"
        # df.to_parquet(output_path)

        print(f"Extraidos registros del {fecha} -> {output_path}")
        return output_path

    @task()
    def limpiar_datos(input_path: str) -> str:
        """Limpiar: eliminar nulos, corregir rangos, interpolar."""
        import pandas as pd

        # df = pd.read_parquet(input_path)

        # Eliminar registros con valores imposibles
        # df = df[df['speed_kmh'].between(0, 250)]
        # df = df[df['battery_temp'].between(-10, 80)]

        # Interpolar valores faltantes (maximo 3 consecutivos)
        # for col in ['speed_kmh', 'battery_temp', 'fuel_consumption']:
        #     df[col] = df[col].interpolate(limit=3)

        # Eliminar filas que siguen con nulos
        # df = df.dropna(subset=['vehicle_id', 'timestamp'])

        output_path = input_path.replace('staging', 'clean')
        # df.to_parquet(output_path)

        print(f"Limpiados -> {output_path}")
        return output_path

    @task()
    def agregar_por_vehiculo(input_path: str) -> dict:
        """Calcular metricas diarias por vehiculo."""
        import pandas as pd

        # df = pd.read_parquet(input_path)
        #
        # agg = df.groupby('vehicle_id').agg(
        #     avg_speed=('speed_kmh', 'mean'),
        #     max_speed=('speed_kmh', 'max'),
        #     avg_consumption=('fuel_consumption', 'mean'),
        #     total_trips=('trip_id', 'nunique'),
        #     avg_battery_temp=('battery_temp', 'mean'),
        #     max_battery_temp=('battery_temp', 'max'),
        #     harsh_braking=('acceleration_ms2', lambda x: (x < -3).sum()),
        # ).reset_index()
        #
        # agg.to_parquet("/data/aggregated/vehiculos_dia.parquet")

        # Retornar resumen para XCom
        return {
            "vehiculos_procesados": 48,
            "total_trips": 312,
            "avg_fleet_speed": 52.3,
        }

    @task()
    def detectar_anomalias(input_path: str) -> list:
        """Ejecutar modelo de anomalias sobre datos del dia."""
        import pandas as pd
        # import joblib

        # df = pd.read_parquet(input_path)
        # model = joblib.load("/models/anomaly_detector.pkl")
        #
        # features = ['speed_kmh', 'fuel_consumption', 'battery_temp', 'motor_rpm']
        # predictions = model.predict(df[features])
        # anomalias = df[predictions == -1]  # Isolation Forest: -1 = anomalia

        # Simulacion
        anomalias = [
            {"vehicle_id": "V032", "tipo": "TEMP_ALTA", "valor": 48.5, "severidad": "HIGH"},
            {"vehicle_id": "V017", "tipo": "CONSUMO_ALTO", "valor": 18.2, "severidad": "MEDIUM"},
        ]

        print(f"Anomalias detectadas: {len(anomalias)}")
        return anomalias

    @task()
    def actualizar_dashboard(metricas: dict):
        """Actualizar metricas en Prometheus/Grafana."""
        # from prometheus_client import CollectorRegistry, Gauge, push_to_gateway
        #
        # registry = CollectorRegistry()
        # g = Gauge('fleet_avg_speed', 'Velocidad media flota', registry=registry)
        # g.set(metricas['avg_fleet_speed'])
        # push_to_gateway('prometheus:9091', job='airflow_telemetria', registry=registry)

        print(f"Dashboard actualizado: {metricas}")

    @task()
    def enviar_alertas(anomalias: list):
        """Enviar alertas a Slack/Email si hay anomalias criticas."""
        criticas = [a for a in anomalias if a['severidad'] == 'HIGH']

        if criticas:
            # Enviar a Slack
            # mensaje = f":rotating_light: {len(criticas)} anomalias criticas detectadas:\n"
            # for a in criticas:
            #     mensaje += f"  - {a['vehicle_id']}: {a['tipo']} ({a['valor']})\n"
            # requests.post(SLACK_WEBHOOK, json={"text": mensaje})

            print(f"ALERTA: {len(criticas)} anomalias criticas enviadas a Slack")
        else:
            print("Sin anomalias criticas hoy")

    # --- Flujo de ejecucion ---
    fecha = "{{ ds }}"

    raw_path = extraer_telemetria(fecha)
    clean_path = limpiar_datos(raw_path)

    # Agregar y detectar en paralelo (ambos usan datos limpios)
    metricas = agregar_por_vehiculo(clean_path)
    anomalias = detectar_anomalias(clean_path)

    # Actualizar dashboard y alertas (pueden ser paralelos)
    actualizar_dashboard(metricas)
    enviar_alertas(anomalias)


telemetria_flota()
```

---

## 15. Ejemplo real: reentrenamiento de modelo

```python
"""
Pipeline semanal que reevalua y potencialmente reentrena
el modelo de prediccion de consumo.

Flujo:
  1. Cargar datos de la ultima semana
  2. Evaluar modelo actual con datos nuevos
  3. Si el rendimiento baja -> reentrenar
  4. Validar nuevo modelo
  5. Si es mejor -> desplegar
  6. Notificar resultado
"""
from airflow.decorators import dag, task
from datetime import datetime, timedelta


@dag(
    dag_id='reentrenamiento_modelo_consumo',
    schedule='0 4 * * 0',  # domingos a las 4:00 AM
    start_date=datetime(2025, 1, 1),
    catchup=False,
    tags=['ml', 'reentrenamiento'],
)
def reentrenamiento_consumo():

    @task()
    def cargar_datos_recientes() -> str:
        """Cargar datos de las ultimas 4 semanas para reentrenar."""
        # import pandas as pd
        # from sqlalchemy import create_engine
        #
        # engine = create_engine(DB_URL)
        # df = pd.read_sql("""
        #     SELECT * FROM telemetry_aggregated
        #     WHERE date >= NOW() - INTERVAL '28 days'
        # """, engine)
        # df.to_parquet("/data/ml/training_data.parquet")

        return "/data/ml/training_data.parquet"

    @task()
    def evaluar_modelo_actual(data_path: str) -> dict:
        """Evaluar el modelo en produccion con datos recientes."""
        # import joblib
        # import pandas as pd
        # from sklearn.metrics import mean_squared_error, r2_score
        #
        # model = joblib.load("/models/production/consumption_model.pkl")
        # df = pd.read_parquet(data_path)
        # X = df[feature_columns]
        # y = df['consumption_mean']
        #
        # y_pred = model.predict(X)
        # r2 = r2_score(y, y_pred)
        # rmse = mean_squared_error(y, y_pred, squared=False)

        # Simulacion
        r2_actual = 0.82
        rmse_actual = 2.1

        return {
            "r2": r2_actual,
            "rmse": rmse_actual,
            "necesita_reentrenamiento": r2_actual < 0.85,  # umbral
        }

    @task.branch()
    def decidir_reentrenamiento(metricas: dict) -> str:
        if metricas["necesita_reentrenamiento"]:
            print(f"R2={metricas['r2']:.3f} < 0.85 -> REENTRENAR")
            return "reentrenar_modelo"
        print(f"R2={metricas['r2']:.3f} >= 0.85 -> modelo OK")
        return "modelo_ok"

    @task()
    def reentrenar_modelo(data_path: str) -> dict:
        """Reentrenar con datos recientes."""
        # import pandas as pd
        # from sklearn.ensemble import GradientBoostingRegressor
        # from sklearn.model_selection import cross_val_score
        # import joblib
        #
        # df = pd.read_parquet(data_path)
        # X = df[feature_columns]
        # y = df['consumption_mean']
        #
        # model = GradientBoostingRegressor(n_estimators=200, max_depth=5)
        # scores = cross_val_score(model, X, y, cv=5, scoring='r2')
        # model.fit(X, y)
        #
        # model_path = f"/models/candidates/consumption_{datetime.now():%Y%m%d}.pkl"
        # joblib.dump(model, model_path)

        return {
            "model_path": "/models/candidates/consumption_20250115.pkl",
            "cv_r2_mean": 0.89,
            "cv_r2_std": 0.02,
        }

    @task()
    def validar_y_desplegar(resultado_entrenamiento: dict, metricas_actual: dict):
        """Comparar nuevo modelo con el actual. Desplegar si es mejor."""
        nuevo_r2 = resultado_entrenamiento["cv_r2_mean"]
        actual_r2 = metricas_actual["r2"]

        if nuevo_r2 > actual_r2:
            # Desplegar: copiar modelo candidato a produccion
            # shutil.copy(resultado["model_path"], "/models/production/consumption_model.pkl")
            print(f"DESPLEGADO: R2 {actual_r2:.3f} -> {nuevo_r2:.3f}")

            # Registrar en MLflow
            # mlflow.log_metric("r2", nuevo_r2)
            # mlflow.sklearn.log_model(model, "consumption_model")
        else:
            print(f"Nuevo modelo NO es mejor: {nuevo_r2:.3f} <= {actual_r2:.3f}")

    @task()
    def modelo_ok():
        print("Modelo en produccion sigue siendo adecuado")

    @task(trigger_rule="none_failed_min_one_success")
    def notificar_resultado():
        """Siempre notificar, haya o no reentrenamiento."""
        # requests.post(SLACK_WEBHOOK, json={
        #     "text": "Pipeline de reentrenamiento completado. Ver Airflow para detalles."
        # })
        print("Notificacion enviada")

    # --- Flujo ---
    data_path = cargar_datos_recientes()
    metricas = evaluar_modelo_actual(data_path)
    decision = decidir_reentrenamiento(metricas)

    # Rama: reentrenar
    resultado = reentrenar_modelo(data_path)
    validar_y_desplegar(resultado, metricas)

    # Rama: modelo OK
    modelo_ok()

    # Siempre notificar
    [validar_y_desplegar, modelo_ok] >> notificar_resultado()


reentrenamiento_consumo()
```

---

## 16. Docker Compose para desarrollo

```yaml
# docker-compose.yml
# Airflow local con CeleryExecutor (produccion-like)

version: '3.8'

x-airflow-common: &airflow-common
  image: apache/airflow:2.8.0
  environment:
    AIRFLOW__CORE__EXECUTOR: LocalExecutor
    AIRFLOW__DATABASE__SQL_ALCHEMY_CONN: postgresql+psycopg2://airflow:airflow@postgres/airflow
    AIRFLOW__CORE__FERNET_KEY: ''
    AIRFLOW__CORE__DAGS_ARE_PAUSED_AT_CREATION: 'true'
    AIRFLOW__CORE__LOAD_EXAMPLES: 'false'
  volumes:
    - ./dags:/opt/airflow/dags          # tus DAGs
    - ./logs:/opt/airflow/logs          # logs
    - ./plugins:/opt/airflow/plugins    # plugins custom
    - ./data:/data                      # datos compartidos
    - ./models:/models                  # modelos ML
  depends_on:
    postgres:
      condition: service_healthy

services:
  postgres:
    image: postgres:15
    environment:
      POSTGRES_USER: airflow
      POSTGRES_PASSWORD: airflow
      POSTGRES_DB: airflow
    healthcheck:
      test: ["CMD", "pg_isready", "-U", "airflow"]
      interval: 5s
      retries: 5
    ports:
      - "5432:5432"

  airflow-init:
    <<: *airflow-common
    entrypoint: /bin/bash
    command: >
      -c "
      airflow db init &&
      airflow users create
        --username admin
        --password admin
        --firstname Admin
        --lastname User
        --role Admin
        --email admin@example.com
      "

  airflow-webserver:
    <<: *airflow-common
    command: webserver
    ports:
      - "8080:8080"   # UI web
    healthcheck:
      test: ["CMD", "curl", "--fail", "http://localhost:8080/health"]
      interval: 10s
      timeout: 10s
      retries: 5

  airflow-scheduler:
    <<: *airflow-common
    command: scheduler

# Uso:
#   docker-compose up airflow-init   # solo la primera vez
#   docker-compose up -d             # levantar todo
#   http://localhost:8080             # UI (admin/admin)
#   Colocar DAGs en ./dags/          # se detectan automaticamente
```
