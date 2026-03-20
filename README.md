# Ciencia de Datos — Portfolio de Aprendizaje

Portfolio completo de proyectos de Ciencia de Datos y Machine Learning, desde fundamentos hasta modelos de producción. Incluye 67+ notebooks con datos reales, fórmulas estadísticas y modelos de clasificación médica.

---

## Proyectos

### 1. Telemetría Vehicular (Datos Simulados)
**31 notebooks** | `notebooks/telemetria_vehicular/`

Proyecto fundacional de DS con datos simulados de flotas vehiculares. Cubre todo el pipeline desde NumPy/Pandas hasta modelos de ML y series temporales.

| Fase | Tema | Notebooks |
|------|------|-----------|
| 1 | Fundamentos (NumPy, Pandas, simulación) | 5 |
| 2 | EDA y Visualización | 6 |
| 3 | Estadística Inferencial | 5 |
| 4 | ML Supervisado | 5 |
| 5 | No Supervisado + Series Temporales | 5 |
| 6 | Síntesis y Producción | 5 |

### 2. NYC Taxi Trips (BigQuery — Datos Reales)
**26 notebooks** | `notebooks/nyc_taxi/`

Análisis de ~146M viajes de taxi amarillo en NYC (2015) usando Google BigQuery. Incluye conexión directa a BigQuery con cache local y estimación de costos.

| Fase | Tema | Notebooks |
|------|------|-----------|
| 1 | Fundamentos + BigQuery | 3 |
| 2 | EDA y Visualización | 6 |
| 3 | Estadística Inferencial | 5 |
| 4 | ML Supervisado | 6 |
| 5 | No Supervisado + Series Temporales | 6 |
| 6 | Síntesis y Producción | 4 |

**Requiere:** Cuenta de Google Cloud (ver [Setup BigQuery](#setup-bigquery))

### 3. Breast Cancer Classification (ML Médico)
**5 notebooks** | `notebooks/breast_cancer/`

Clasificación binaria de tumores mamarios (maligno/benigno) usando el dataset Wisconsin Breast Cancer (569 muestras, 30 features).

| Notebook | Misión |
|----------|--------|
| 01 | EDA: distribuciones, correlaciones, features redundantes |
| 02 | Preprocesamiento: scaling, selección de features |
| 03 | Baseline: Logistic Regression, Random Forest, XGBoost |
| 04 | Autopsia: análisis de Falsos Negativos |
| 05 | Optimización: umbral, ROC, costo médico FN vs FP |

### 4. Stroke Prediction (ML con Desbalance Extremo)
**5 notebooks** | `notebooks/stroke_prediction/`

Predicción de ictus cerebral con desbalance severo (95% negativo, 5% positivo). Incluye SMOTE, encoding categórico y optimización de umbral para contexto médico.

| Notebook | Misión |
|----------|--------|
| 01 | EDA: factores de riesgo, desbalance de clases |
| 02 | Preprocesamiento: imputación BMI, encoding categóricas |
| 03 | Baseline: SMOTE, class_weight, comparación 6 modelos |
| 04 | Autopsia: perfil de FN, error por edad/hipertensión |
| 05 | Optimización: umbral, costo FN=200×, modelo final |

### 5. Formulario Estadístico
**1 notebook** | `notebooks/nyc_taxi/00_formulario_estadistico.ipynb`

Referencia completa con todas las fórmulas estadísticas: tabla maestra, teoría detallada con origen histórico, visualizaciones y ejemplos numéricos paso a paso.

---

## Estructura del Proyecto

```
Ciencia_Datos/
├── notebooks/
│   ├── telemetria_vehicular/     # 31 notebooks (datos simulados)
│   │   └── phase1-6/
│   ├── nyc_taxi/                 # 26 notebooks + formulario (BigQuery)
│   │   ├── 00_formulario_estadistico.ipynb
│   │   └── phase1-6/
│   ├── breast_cancer/            # 5 notebooks (clasificación binaria)
│   └── stroke_prediction/        # 5 notebooks (desbalance + SMOTE)
├── src/
│   └── bigquery/
│       └── bq_helper.py          # Helper BigQuery con cache
├── data/
│   ├── breast_cancer/            # Dataset Wisconsin + procesados
│   ├── heart_attack/             # Dataset Stroke + procesados
│   └── nyc_taxi/cache/           # Cache de queries BigQuery
├── models/                       # Modelos entrenados (.pkl)
├── docs/
│   ├── concept_index.md          # Índice de todos los conceptos
│   └── mlops_reference/          # Referencia MLOps
├── requirements.txt
└── setup.sh                      # Script de instalación
```

---

## Instalación Rápida

### Opción 1: Script automático

```bash
git clone https://github.com/DanielMf31/Ciencia_Datos.git
cd Ciencia_Datos
chmod +x setup.sh
./setup.sh
```

### Opción 2: Manual

```bash
# 1. Clonar el repositorio
git clone https://github.com/DanielMf31/Ciencia_Datos.git
cd Ciencia_Datos

# 2. Crear entorno virtual
python3 -m venv .venv
source .venv/bin/activate

# 3. Instalar dependencias
pip install -r requirements.txt

# 4. Abrir JupyterLab
jupyter lab
```

### Setup BigQuery (solo para NYC Taxi)

Los notebooks de NYC Taxi requieren acceso a Google BigQuery (tier gratuito: 1TB/mes):

```bash
# 1. Instalar Google Cloud CLI
# https://cloud.google.com/sdk/docs/install

# 2. Autenticarse
gcloud auth login
gcloud auth application-default login

# 3. Habilitar la API de BigQuery en tu proyecto
# https://console.cloud.google.com/apis/api/bigquery.googleapis.com
```

---

## Tecnologías Utilizadas

| Categoría | Herramientas |
|-----------|-------------|
| **Lenguaje** | Python 3.12 |
| **Data** | NumPy, Pandas, PyArrow |
| **Visualización** | Matplotlib, Seaborn, Plotly, Folium |
| **Estadística** | SciPy, Statsmodels |
| **Machine Learning** | Scikit-learn, XGBoost, imbalanced-learn |
| **Series Temporales** | Prophet, ARIMA/SARIMA |
| **Cloud** | Google BigQuery |
| **Notebooks** | JupyterLab |

---

## Conceptos Cubiertos

- **Fundamentos:** NumPy, Pandas, SQL, BigQuery, limpieza de datos
- **Visualización:** matplotlib, seaborn, Plotly, Folium, dashboards interactivos
- **Estadística:** distribuciones, tests de hipótesis, intervalos de confianza, correlaciones
- **ML Supervisado:** regresión, clasificación, feature engineering, GridSearchCV
- **ML No Supervisado:** K-Means, DBSCAN, PCA, t-SNE
- **Series Temporales:** descomposición, ARIMA, SARIMA, Prophet
- **Detección de Anomalías:** z-score, IQR, Isolation Forest
- **ML Médico:** desbalance de clases, SMOTE, optimización de umbral, análisis de costo FN/FP
- **MLOps:** pipelines, monitoreo, despliegue en GCP

Ver el índice completo en [`docs/concept_index.md`](docs/concept_index.md).

---

## Licencia

Este proyecto es de uso educativo. Los datasets utilizados son públicos:
- [NYC Taxi Trips](https://console.cloud.google.com/bigquery?p=bigquery-public-data&d=new_york_taxi_trips) (BigQuery Public Datasets)
- [Wisconsin Breast Cancer](https://archive.ics.uci.edu/dataset/17/breast+cancer+wisconsin+diagnostic) (UCI ML Repository)
- [Stroke Prediction](https://www.kaggle.com/datasets/fedesoriano/stroke-prediction-dataset) (Kaggle)
