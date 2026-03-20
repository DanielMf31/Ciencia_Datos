# MLOps - Guia General de Conceptos

## Indice

1. [Que es MLOps](#1-que-es-mlops)
2. [El problema que resuelve](#2-el-problema-que-resuelve)
3. [Ciclo de vida de un modelo ML](#3-ciclo-de-vida)
4. [Niveles de madurez MLOps](#4-niveles-de-madurez)
5. [Componentes del stack MLOps](#5-componentes-del-stack)
6. [Feature Store](#6-feature-store)
7. [Experiment Tracking con MLflow](#7-experiment-tracking-mlflow)
8. [Model Registry](#8-model-registry)
9. [Model Serving: como servir predicciones](#9-model-serving)
10. [CI/CD para ML](#10-cicd-para-ml)
11. [Data Versioning con DVC](#11-data-versioning-dvc)
12. [Model Monitoring y Drift](#12-model-monitoring-drift)
13. [A/B Testing de modelos](#13-ab-testing)
14. [Infraestructura: contenedores y orquestacion](#14-infraestructura)
15. [Pipeline end-to-end completo](#15-pipeline-end-to-end)
16. [Stack recomendado para empezar](#16-stack-recomendado)

---

## 1. Que es MLOps

MLOps = Machine Learning + DevOps + Data Engineering

```
DevOps:     codigo   → build → test → deploy → monitorear → iterar
MLOps:      datos + codigo → entrenar → validar → deploy → monitorear → reentrenar
                 ↑                                              │
                 └──────────────────────────────────────────────┘
                              (ciclo continuo)
```

Es el conjunto de practicas para llevar modelos ML desde un notebook
hasta un sistema en produccion que funciona 24/7, se monitorea solo,
y se reentrena cuando es necesario.

---

## 2. El problema que resuelve

```
Sin MLOps:
  - Data scientist crea modelo en notebook
  - Lo pasa por email/Slack al equipo de ingenieria
  - Ingenieria tarda semanas en entender como integrarlo
  - Modelo funciona diferente en produccion (versiones, datos distintos)
  - Nadie sabe si el modelo sigue siendo bueno despues de 3 meses
  - Para actualizar el modelo hay que repetir todo manualmente

Con MLOps:
  - Pipeline automatizado: datos → entrenamiento → validacion → despliegue
  - Versionado de datos Y modelos (puedes volver atras)
  - Monitoreo continuo (alertas si el modelo se degrada)
  - Reentrenamiento automatico cuando se detecta drift
  - Reproducibilidad total (cualquiera puede recrear el modelo)
```

---

## 3. Ciclo de vida de un modelo ML

```
┌─────────────────────────────────────────────────────────────────┐
│                                                                 │
│   1. PROBLEMA          2. DATOS           3. EXPERIMENTACION    │
│   ┌─────────┐          ┌─────────┐        ┌─────────┐          │
│   │ Definir │────────> │Recopilar│──────> │ Probar  │          │
│   │ objetivo│          │ limpiar │        │ modelos │          │
│   │ metricas│          │ validar │        │ evaluar │          │
│   └─────────┘          └─────────┘        └────┬────┘          │
│                                                │               │
│   6. MONITOREO         5. DESPLIEGUE      4. REGISTRO          │
│   ┌─────────┐          ┌─────────┐        ┌────┴────┐          │
│   │ Drift?  │<──────── │  API    │<────── │ Guardar │          │
│   │ Errores?│          │ Docker  │        │ version │          │
│   │ Rendim? │          │ K8s     │        │ metricas│          │
│   └────┬────┘          └─────────┘        └─────────┘          │
│        │                                                       │
│        │  si hay degradacion                                   │
│        └──────────> Volver a paso 2 (REENTRENAR)               │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘

Roles involucrados:
  Pasos 1-3: Data Scientist
  Pasos 4-6: MLOps Engineer / ML Engineer
  Todo:      ML Engineer (hibrido, el perfil mas buscado)
```

---

## 4. Niveles de madurez MLOps

```
Nivel 0: Manual
  - Todo en notebooks
  - Despliegue manual
  - Sin monitoreo
  - Reentrenamiento manual
  → La mayoria de empresas estan aqui

Nivel 1: Pipeline automatizado
  - Pipeline de entrenamiento automatizado (Airflow)
  - Despliegue automatizado (CI/CD)
  - Monitoreo basico (Prometheus/Grafana)
  - Reentrenamiento triggered (cuando hay drift)
  → Empresas de datos medianas

Nivel 2: CI/CD para ML
  - Tests automaticos para datos, modelo y codigo
  - A/B testing de modelos
  - Feature store centralizado
  - Reentrenamiento continuo automatico
  → Google, Netflix, Uber, Tesla
```

---

## 5. Componentes del stack MLOps

```
┌──────────────────────────────────────────────────────────────┐
│                     STACK MLOps COMPLETO                      │
├──────────────────────────────────────────────────────────────┤
│                                                              │
│  DATOS                                                       │
│  ├── Ingestion:     Kafka, Airflow, APIs                     │
│  ├── Storage:       S3, PostgreSQL, Data Lake                │
│  ├── Processing:    Spark, Pandas, dbt                       │
│  ├── Versioning:    DVC, Delta Lake                          │
│  └── Feature Store: Feast, Tecton                            │
│                                                              │
│  EXPERIMENTACION                                             │
│  ├── Notebooks:     Jupyter, Colab                           │
│  ├── Tracking:      MLflow, Weights & Biases                 │
│  ├── Frameworks:    scikit-learn, XGBoost, PyTorch            │
│  └── Hyperparams:   Optuna, Ray Tune                         │
│                                                              │
│  PRODUCCION                                                  │
│  ├── Model Registry: MLflow, SageMaker                       │
│  ├── Serving:        FastAPI, TensorFlow Serving, Triton     │
│  ├── Containers:     Docker, Kubernetes                      │
│  ├── CI/CD:          GitHub Actions, GitLab CI               │
│  └── IaC:            Terraform, Pulumi                       │
│                                                              │
│  MONITOREO                                                   │
│  ├── Infra:          Prometheus, Grafana                     │
│  ├── Logs:           Loki, ELK                               │
│  ├── ML:             Evidently, Whylogs, NannyML             │
│  └── Alertas:        Alertmanager, PagerDuty, Slack          │
│                                                              │
└──────────────────────────────────────────────────────────────┘
```

---

## 6. Feature Store

Un **almacen centralizado de features** reutilizables.

```
Problema sin Feature Store:
  - Equipo A calcula "avg_speed_7d" de una forma
  - Equipo B calcula "avg_speed_7d" de otra forma
  - El modelo entrena con una version, produccion usa otra
  - Inconsistencia → predicciones erroneas

Solucion: Feature Store
  - Una sola definicion de cada feature
  - Misma feature en entrenamiento Y produccion
  - Versionada y documentada
```

```python
# Ejemplo con Feast (Feature Store open source)
# pip install feast

# --- Definir features (feature_store.yaml + definiciones) ---

from feast import Entity, Feature, FeatureView, FileSource
from feast.types import Float32, Int64
from datetime import timedelta

# Fuente de datos
telemetry_source = FileSource(
    path="data/processed/vehicle_features.parquet",
    timestamp_field="event_timestamp",
)

# Entidad (sobre que son las features)
vehicle = Entity(
    name="vehicle_id",
    description="Identificador de vehiculo",
)

# Feature View (grupo de features)
vehicle_features = FeatureView(
    name="vehicle_telemetry_features",
    entities=[vehicle],
    ttl=timedelta(days=7),  # features validas por 7 dias
    schema=[
        Feature(name="avg_speed_7d", dtype=Float32),
        Feature(name="avg_consumption_7d", dtype=Float32),
        Feature(name="harsh_braking_count", dtype=Int64),
        Feature(name="night_trip_ratio", dtype=Float32),
        Feature(name="max_battery_temp", dtype=Float32),
    ],
    source=telemetry_source,
)


# --- Usar en entrenamiento ---
from feast import FeatureStore

store = FeatureStore(repo_path=".")

# Obtener features historicas para entrenamiento
training_df = store.get_historical_features(
    entity_df=entity_df,  # DataFrame con vehicle_id + timestamp
    features=[
        "vehicle_telemetry_features:avg_speed_7d",
        "vehicle_telemetry_features:avg_consumption_7d",
        "vehicle_telemetry_features:harsh_braking_count",
    ],
).to_df()

model.fit(training_df[feature_cols], training_df["target"])


# --- Usar en produccion (mismas features, misma logica) ---
online_features = store.get_online_features(
    features=[
        "vehicle_telemetry_features:avg_speed_7d",
        "vehicle_telemetry_features:avg_consumption_7d",
    ],
    entity_rows=[{"vehicle_id": "V032"}],
).to_dict()

prediction = model.predict([list(online_features.values())])
```

---

## 7. Experiment Tracking con MLflow

MLflow registra **cada experimento** que haces: parametros, metricas, artefactos.

```python
# pip install mlflow

import mlflow
import mlflow.sklearn
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import r2_score, mean_squared_error
import numpy as np

# Configurar tracking server
mlflow.set_tracking_uri("http://localhost:5000")  # o local: "mlruns/"
mlflow.set_experiment("prediccion_consumo")

# --- Registrar un experimento ---
with mlflow.start_run(run_name="rf_v1_baseline"):

    # Parametros
    params = {
        "n_estimators": 200,
        "max_depth": 10,
        "min_samples_split": 5,
        "features_used": "speed,consumption,battery_temp,rpm",
        "train_size": len(X_train),
    }
    mlflow.log_params(params)

    # Entrenar
    model = RandomForestRegressor(**{k: v for k, v in params.items()
                                     if k in ['n_estimators', 'max_depth', 'min_samples_split']})
    model.fit(X_train, y_train)
    y_pred = model.predict(X_test)

    # Metricas
    metrics = {
        "r2": r2_score(y_test, y_pred),
        "rmse": np.sqrt(mean_squared_error(y_test, y_pred)),
        "mae": np.mean(np.abs(y_test - y_pred)),
    }
    mlflow.log_metrics(metrics)

    # Guardar modelo
    mlflow.sklearn.log_model(model, "model")

    # Guardar artefactos (graficas, datos, etc.)
    # mlflow.log_artifact("plots/feature_importance.png")
    # mlflow.log_artifact("data/test_predictions.csv")

    print(f"Run ID: {mlflow.active_run().info.run_id}")
    print(f"R2: {metrics['r2']:.4f}, RMSE: {metrics['rmse']:.4f}")


# --- Comparar experimentos ---
# En la UI de MLflow (http://localhost:5000):
#   - Ver todos los runs de un experimento
#   - Comparar metricas entre runs
#   - Ver parametros de cada run
#   - Descargar artefactos

# Desde codigo:
runs = mlflow.search_runs(experiment_names=["prediccion_consumo"])
print(runs[['run_id', 'params.n_estimators', 'metrics.r2', 'metrics.rmse']]
      .sort_values('metrics.r2', ascending=False))


# --- Iniciar MLflow UI ---
# En terminal: mlflow ui --port 5000
# Abrir: http://localhost:5000
```

---

## 8. Model Registry

Registro centralizado de modelos con **versionado y estados**.

```python
import mlflow

# --- Registrar modelo en el registry ---
# Despues de un run exitoso:
model_uri = f"runs:/{run_id}/model"
model_version = mlflow.register_model(model_uri, "consumption_predictor")
# Crea: consumption_predictor version 1

# --- Transiciones de estado ---
# Staging: listo para testear
client = mlflow.tracking.MlflowClient()
client.transition_model_version_stage(
    name="consumption_predictor",
    version=1,
    stage="Staging"
)

# Production: aprobado para produccion
client.transition_model_version_stage(
    name="consumption_predictor",
    version=1,
    stage="Production"
)

# Archived: retirado
client.transition_model_version_stage(
    name="consumption_predictor",
    version=1,
    stage="Archived"
)


# --- Cargar modelo de produccion ---
# En tu API:
model = mlflow.sklearn.load_model("models:/consumption_predictor/Production")
prediction = model.predict(features)

# Siempre carga la version que esta en "Production"
# Si promueves v2 a Production, el API automaticamente usa v2


# --- Flujo tipico ---
#
#  Entrenamiento → v3 creada (stage: None)
#       ↓
#  Tests pasan  → v3 → Staging
#       ↓
#  A/B test OK  → v3 → Production (v2 → Archived)
#       ↓
#  Problema?    → v3 → Archived, v2 → Production (rollback!)
```

```
Flujo visual:

  None ──> Staging ──> Production ──> Archived
              ↑             │
              └─────────────┘  (rollback si falla)

  Version 1:  [Archived]
  Version 2:  [Archived]
  Version 3:  [Production]  ← API carga esta
  Version 4:  [Staging]     ← en pruebas
```

---

## 9. Model Serving

Diferentes formas de servir predicciones:

```
1. API REST (FastAPI) - lo mas comun
   + Simple, flexible, cualquier framework
   + Perfecto para latencia media (10-100ms)
   - Tienes que gestionar escalado tu mismo

2. Batch Predictions (Airflow + Spark)
   + Para predicciones masivas (millones)
   + No necesitas API, se ejecuta periodicamente
   - No es tiempo real

3. Streaming (Kafka + modelo)
   + Tiempo real continuo
   + Cada evento se procesa inmediatamente
   - Mas complejo de implementar

4. Edge (modelo en el dispositivo)
   + Latencia minima (sin red)
   + Funciona offline
   - Modelo limitado por hardware del dispositivo
   - Dificil de actualizar
```

```python
# --- Opcion 1: API REST con FastAPI ---
from fastapi import FastAPI
import mlflow

app = FastAPI()
model = mlflow.sklearn.load_model("models:/consumption_predictor/Production")

@app.post("/predict")
def predict(features: dict):
    prediction = model.predict([list(features.values())])
    return {"prediction": float(prediction[0])}

# Escalar: Docker + Kubernetes + Load Balancer


# --- Opcion 2: Batch con Airflow ---
def batch_predict():
    """Se ejecuta diariamente a las 4 AM."""
    model = mlflow.sklearn.load_model("models:/consumption_predictor/Production")
    df = pd.read_sql("SELECT * FROM vehicles_to_predict", engine)

    predictions = model.predict(df[feature_columns])
    df['predicted_consumption'] = predictions

    df.to_sql("predictions_daily", engine, if_exists="append")
    print(f"Predicciones generadas para {len(df)} vehiculos")


# --- Opcion 3: Streaming con Kafka ---
from kafka import KafkaConsumer, KafkaProducer
import joblib

model = joblib.load("models/consumption_model.pkl")
consumer = KafkaConsumer('telemetria-raw', group_id='ml-predict')
producer = KafkaProducer(bootstrap_servers='localhost:9092')

for message in consumer:
    data = json.loads(message.value)
    features = [data['speed'], data['battery_temp'], data['rpm']]
    prediction = model.predict([features])[0]

    result = {**data, "predicted_consumption": prediction}
    producer.send('predicciones', value=json.dumps(result).encode())
```

---

## 10. CI/CD para ML

```yaml
# .github/workflows/ml_pipeline.yml
# GitHub Actions para CI/CD de modelos

name: ML Pipeline

on:
  push:
    paths:
      - 'src/models/**'
      - 'src/features/**'
      - 'tests/**'
  schedule:
    - cron: '0 4 * * 0'  # cada domingo a las 4 AM

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Setup Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.12'

      - name: Install dependencies
        run: pip install -r requirements.txt

      # Tests de codigo
      - name: Unit tests
        run: pytest tests/unit/

      # Tests de datos
      - name: Data validation
        run: python tests/validate_data.py
        # Verifica: esquema correcto, sin nulos inesperados,
        # rangos validos, no hay data leakage

      # Tests de modelo
      - name: Model tests
        run: pytest tests/model/
        # Verifica: modelo carga correctamente,
        # predicciones en rango esperado,
        # rendimiento minimo (R2 > 0.80)

  train:
    needs: test
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'
    steps:
      - uses: actions/checkout@v4

      - name: Train model
        run: python src/train.py
        env:
          MLFLOW_TRACKING_URI: ${{ secrets.MLFLOW_URI }}

      - name: Evaluate model
        run: python src/evaluate.py

      - name: Register model
        run: python src/register_model.py
        # Si metricas > umbral → registrar en MLflow

  deploy:
    needs: train
    runs-on: ubuntu-latest
    steps:
      - name: Build Docker image
        run: docker build -t api-prediccion:${{ github.sha }} .

      - name: Push to registry
        run: docker push registry.example.com/api-prediccion:${{ github.sha }}

      - name: Deploy to Kubernetes
        run: kubectl set image deployment/api-prediccion
             api=registry.example.com/api-prediccion:${{ github.sha }}
```

```python
# tests/model/test_model.py
"""Tests automaticos para el modelo ML."""
import pytest
import numpy as np
import joblib


@pytest.fixture
def model():
    return joblib.load("models/consumption_model.pkl")


@pytest.fixture
def sample_input():
    return np.array([[60.0, 12.5, 35.0, 1100, 0.3]])  # speed, consumption, temp, rpm, highway


def test_model_loads(model):
    """El modelo se carga sin errores."""
    assert model is not None


def test_prediction_shape(model, sample_input):
    """La prediccion devuelve un solo valor."""
    pred = model.predict(sample_input)
    assert pred.shape == (1,)


def test_prediction_range(model, sample_input):
    """La prediccion esta en un rango razonable."""
    pred = model.predict(sample_input)[0]
    assert 0 < pred < 50  # consumo entre 0 y 50 L/100km


def test_prediction_deterministic(model, sample_input):
    """Misma entrada = misma salida."""
    pred1 = model.predict(sample_input)[0]
    pred2 = model.predict(sample_input)[0]
    assert pred1 == pred2


def test_model_performance():
    """El modelo cumple metricas minimas en test set."""
    from sklearn.metrics import r2_score
    # X_test, y_test = load_test_data()
    # model = joblib.load("models/consumption_model.pkl")
    # y_pred = model.predict(X_test)
    # r2 = r2_score(y_test, y_pred)
    r2 = 0.87  # simulado
    assert r2 > 0.80, f"R2 = {r2} < 0.80 minimo"


def test_no_data_leakage():
    """Verificar que no hay leakage entre train y test."""
    # train_ids = set(train_df['vehicle_id'])
    # test_ids = set(test_df['vehicle_id'])
    # overlap = train_ids & test_ids
    # assert len(overlap) == 0, f"Data leakage: {overlap}"
    pass
```

---

## 11. Data Versioning con DVC

DVC = Git para datos. Versiona datasets grandes que no caben en Git.

```bash
# Instalar
pip install dvc dvc-s3  # o dvc-gdrive, dvc-azure

# Inicializar DVC en el repo
cd mi-proyecto
dvc init

# --- Trackear un dataset ---
dvc add data/raw/telemetria.parquet
# Crea: data/raw/telemetria.parquet.dvc (metadata, se guarda en Git)
# El archivo real se sube a remote storage

git add data/raw/telemetria.parquet.dvc .gitignore
git commit -m "Add telemetry dataset v1"

# --- Configurar remote storage ---
dvc remote add -d storage s3://mi-bucket/dvc-storage
# O: dvc remote add -d storage gdrive://folder_id
# O: dvc remote add -d storage /path/to/local/storage

# Subir datos al remote
dvc push

# --- Cambiar datos y versionar ---
# (actualizas el parquet con datos nuevos)
dvc add data/raw/telemetria.parquet
git add data/raw/telemetria.parquet.dvc
git commit -m "Update telemetry dataset - January data"
dvc push

# --- Volver a una version anterior ---
git checkout v1.0 -- data/raw/telemetria.parquet.dvc
dvc pull
# Ahora tienes los datos de la version v1.0

# --- Pipeline reproducible ---
# dvc.yaml define el pipeline
```

```yaml
# dvc.yaml
# Pipeline reproducible: DVC sabe que pasos ejecutar y en que orden

stages:
  prepare:
    cmd: python src/prepare_data.py
    deps:
      - src/prepare_data.py
      - data/raw/telemetria.parquet
    outs:
      - data/processed/clean.parquet

  train:
    cmd: python src/train.py
    deps:
      - src/train.py
      - data/processed/clean.parquet
    outs:
      - models/consumption_model.pkl
    metrics:
      - metrics/scores.json:
          cache: false  # trackear en Git (pequeno)

  evaluate:
    cmd: python src/evaluate.py
    deps:
      - src/evaluate.py
      - models/consumption_model.pkl
      - data/processed/clean.parquet
    plots:
      - plots/confusion_matrix.png
      - plots/roc_curve.png
```

```bash
# Ejecutar pipeline
dvc repro
# DVC solo re-ejecuta los pasos cuyos inputs cambiaron
# Si solo cambiaste train.py, no re-ejecuta prepare

# Comparar metricas entre versiones
dvc metrics diff
# main    current
# r2:     0.85    0.89  (+0.04)
# rmse:   2.3     1.8   (-0.5)
```

---

## 12. Model Monitoring y Drift

```python
"""
Monitoreo de drift con Evidently.
Compara datos de entrenamiento vs datos de produccion.
"""
# pip install evidently

from evidently.report import Report
from evidently.metric_preset import (
    DataDriftPreset,
    DataQualityPreset,
    TargetDriftPreset,
    RegressionPreset,
)
from evidently.test_suite import TestSuite
from evidently.tests import (
    TestNumberOfDriftedColumns,
    TestShareOfDriftedColumns,
    TestColumnDrift,
)
import pandas as pd


# --- Generar reporte de drift ---

reference_data = pd.read_parquet("data/reference/train_data.parquet")  # datos de entrenamiento
current_data = pd.read_parquet("data/production/this_week.parquet")    # datos recientes

# Reporte visual completo
report = Report(metrics=[
    DataDriftPreset(),       # drift en features
    DataQualityPreset(),     # calidad de datos (nulos, tipos)
    # TargetDriftPreset(),   # drift en target (si tienes ground truth)
    # RegressionPreset(),    # metricas de regresion (si tienes y_true)
])

report.run(reference_data=reference_data, current_data=current_data)

# Guardar como HTML (para revisar visualmente)
report.save_html("reports/drift_report.html")

# Obtener resultados como dict (para automatizar)
results = report.as_dict()
drift_detected = results['metrics'][0]['result']['dataset_drift']
print(f"Dataset drift detectado: {drift_detected}")

# Por columna:
for col_result in results['metrics'][0]['result']['drift_by_columns'].values():
    if col_result['drift_detected']:
        print(f"  DRIFT en {col_result['column_name']}: "
              f"p-value={col_result['drift_score']:.4f}")


# --- Tests automatizados (para CI/CD) ---

test_suite = TestSuite(tests=[
    TestNumberOfDriftedColumns(lt=3),     # menos de 3 columnas con drift
    TestShareOfDriftedColumns(lt=0.3),    # menos del 30% de columnas
    TestColumnDrift("speed_kmh"),          # esta columna especifica no debe tener drift
    TestColumnDrift("battery_temp"),
])

test_suite.run(reference_data=reference_data, current_data=current_data)

# Verificar resultados
test_results = test_suite.as_dict()
all_passed = all(
    test['status'] == 'SUCCESS'
    for test in test_results['tests']
)

if not all_passed:
    print("ALERTA: Tests de drift fallaron!")
    # Enviar alerta a Slack, disparar reentrenamiento, etc.
else:
    print("OK: Sin drift significativo")


# --- Monitoreo continuo (ejecutar periodicamente) ---

def monitor_model_weekly():
    """Se ejecuta via Airflow cada semana."""
    reference = pd.read_parquet("data/reference/train_data.parquet")

    # Obtener datos de la ultima semana
    # current = pd.read_sql("SELECT * FROM predictions WHERE date >= NOW() - 7", engine)

    report = Report(metrics=[DataDriftPreset()])
    report.run(reference_data=reference, current_data=current)

    results = report.as_dict()
    drift = results['metrics'][0]['result']['dataset_drift']

    if drift:
        # Opcion 1: Alertar
        # send_slack_alert("Data drift detectado!")

        # Opcion 2: Disparar reentrenamiento automatico
        # trigger_airflow_dag("reentrenamiento_modelo")

        # Opcion 3: Log para revision manual
        report.save_html(f"reports/drift_{datetime.now():%Y%m%d}.html")

    return {"drift_detected": drift}
```

---

## 13. A/B Testing de modelos

```python
"""
A/B Testing: comparar modelo actual vs candidato en produccion.
"""
from fastapi import FastAPI
import random
import mlflow
import time

app = FastAPI()

# Cargar ambos modelos
model_a = mlflow.sklearn.load_model("models:/consumption/Production")  # actual
model_b = mlflow.sklearn.load_model("models:/consumption/Staging")     # candidato

# Configuracion del test
AB_CONFIG = {
    "enabled": True,
    "traffic_split": 0.2,  # 20% al modelo B
    "start_date": "2025-01-15",
    "min_samples": 1000,   # minimo de muestras antes de decidir
}


@app.post("/predict")
def predict(data: dict):
    # Decidir que modelo usar
    if AB_CONFIG["enabled"] and random.random() < AB_CONFIG["traffic_split"]:
        model_name = "B"
        model = model_b
    else:
        model_name = "A"
        model = model_a

    # Predecir
    start = time.time()
    prediction = model.predict([list(data.values())])[0]
    latency = time.time() - start

    # Registrar metricas para el test
    # prometheus: ab_test_predictions{model="A"}.inc()
    # prometheus: ab_test_latency{model="A"}.observe(latency)
    # database:   INSERT INTO ab_results (model, prediction, features, timestamp)

    return {
        "prediction": float(prediction),
        "model": model_name,  # transparencia (opcional)
    }


# --- Evaluar resultados del A/B test ---

def evaluate_ab_test():
    """Ejecutar despues de suficientes muestras."""
    # results_a = pd.read_sql("SELECT * FROM ab_results WHERE model='A'", engine)
    # results_b = pd.read_sql("SELECT * FROM ab_results WHERE model='B'", engine)

    # Comparar metricas:
    #   - Precision (si tienes ground truth)
    #   - Latencia media
    #   - Tasa de errores
    #   - Metricas de negocio (satisfaccion, conversion, etc.)

    # Test estadistico para verificar que la diferencia es significativa
    from scipy.stats import mannwhitneyu

    # stat, p_value = mannwhitneyu(errors_a, errors_b)
    # if p_value < 0.05 and mean_error_b < mean_error_a:
    #     print("Modelo B es significativamente mejor → promover a Production")
    #     promote_model_b()
    # else:
    #     print("Sin diferencia significativa → mantener modelo A")
    pass
```

---

## 14. Infraestructura: contenedores y orquestacion

```dockerfile
# Dockerfile para API de prediccion
FROM python:3.12-slim

WORKDIR /app

# Instalar dependencias
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar codigo y modelo
COPY src/ ./src/
COPY models/ ./models/

# Exponer puerto
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=5s \
    CMD curl -f http://localhost:8000/health || exit 1

# Ejecutar
CMD ["uvicorn", "src.api:app", "--host", "0.0.0.0", "--port", "8000"]
```

```yaml
# kubernetes/deployment.yaml
# Despliegue en Kubernetes

apiVersion: apps/v1
kind: Deployment
metadata:
  name: api-prediccion
spec:
  replicas: 3  # 3 instancias para alta disponibilidad
  selector:
    matchLabels:
      app: api-prediccion
  template:
    metadata:
      labels:
        app: api-prediccion
      annotations:
        prometheus.io/scrape: "true"     # Prometheus descubre automaticamente
        prometheus.io/port: "8000"
        prometheus.io/path: "/metrics"
    spec:
      containers:
        - name: api
          image: registry.example.com/api-prediccion:v2.3
          ports:
            - containerPort: 8000
          resources:
            requests:
              memory: "512Mi"
              cpu: "250m"
            limits:
              memory: "1Gi"
              cpu: "500m"
          readinessProbe:
            httpGet:
              path: /health
              port: 8000
            initialDelaySeconds: 10
          env:
            - name: MODEL_PATH
              value: "/models/consumption_model.pkl"

---
# Servicio para exponer la API
apiVersion: v1
kind: Service
metadata:
  name: api-prediccion
spec:
  selector:
    app: api-prediccion
  ports:
    - port: 80
      targetPort: 8000
  type: LoadBalancer

---
# Autoescalado: escalar segun CPU/peticiones
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: api-prediccion
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: api-prediccion
  minReplicas: 2
  maxReplicas: 10
  metrics:
    - type: Resource
      resource:
        name: cpu
        target:
          type: Utilization
          averageUtilization: 70  # escalar si CPU > 70%
```

---

## 15. Pipeline end-to-end completo

```
Todo junto: como se conectan las piezas

DATOS:
  Sensores → Kafka → Spark ETL → PostgreSQL/S3
                                       ↓
                                  Feature Store (Feast)
                                       ↓
ENTRENAMIENTO:                    Features listas
  Airflow (semanal) → DVC pull datos → MLflow experiment
                                            ↓
                                       Model Registry
                                       (Staging → Production)
                                            ↓
SERVING:
  FastAPI + Docker → Kubernetes (3 replicas, autoescalado)
       ↑                    ↓
  Feature Store        Predicciones
  (online)                  ↓
                       Kafka (resultados)
                            ↓
MONITOREO:
  Prometheus (metricas infra) → Grafana (dashboards)
  Loki (logs)                 → Grafana (logs)
  Evidently (drift ML)        → Alertmanager → Slack
                                     ↓
                              Si drift → trigger Airflow → reentrenar
```

---

## 16. Stack recomendado para empezar

```
No necesitas todo desde el principio. Empieza simple y ve anadiendo:

NIVEL 1 (tu proyecto actual):
  ✅ Jupyter notebooks
  ✅ scikit-learn / XGBoost
  ✅ Pandas
  ✅ Git para codigo

NIVEL 2 (siguiente paso):
  → FastAPI para servir el modelo
  → Docker para empaquetar
  → MLflow para experiment tracking
  → pytest para tests del modelo

NIVEL 3 (proyecto real):
  → Airflow para pipelines
  → Prometheus + Grafana para monitoreo
  → DVC para versionar datos
  → Evidently para drift detection

NIVEL 4 (produccion seria):
  → Kafka para ingestion en tiempo real
  → Spark para procesamiento masivo
  → Kubernetes para orquestacion
  → Feature Store para consistencia
  → CI/CD completo con GitHub Actions

Tu plan:
  Ahora mismo estas en Nivel 1
  Tu IDEA.md (FastAPI + Celery + React) te lleva al Nivel 2-3
  Con tu carrera de electronica + estos conocimientos, llegaras al 4
```
