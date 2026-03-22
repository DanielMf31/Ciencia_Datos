# Ciencia de Datos — Portfolio de Aprendizaje

Portfolio completo de proyectos de Ciencia de Datos y Machine Learning. Incluye proyectos con datos reales, formulario estadistico completo, guias de ML/Deep Learning, y notebooks de ejercicios interactivos.

---

## Material de Estudio

### Formulario Estadistico Completo

Referencia con todas las formulas estadisticas: combinatoria, distribuciones, intervalos de confianza, tests de hipotesis, regresion, clustering y mas. Con visualizaciones y ejemplos numericos paso a paso.

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/DanielMf31/Ciencia_Datos/blob/main/docs/00_formulario_estadistico.ipynb) `docs/00_formulario_estadistico.ipynb`

### Notebooks de Ejercicios

| Tema | Notebook | Colab |
|------|----------|-------|
| Combinatoria y Probabilidad | `ejercicios-combinatoria.ipynb` | [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/DanielMf31/Ciencia_Datos/blob/main/docs/Learning/Estadistica/ejercicios-combinatoria.ipynb) |
| Esperanza y Varianza | `ejercicios-esperanza-varianza.ipynb` | [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/DanielMf31/Ciencia_Datos/blob/main/docs/Learning/Estadistica/ejercicios-esperanza-varianza.ipynb) |
| Distribuciones Discretas | `ejercicios-distribuciones-discretas.ipynb` | [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/DanielMf31/Ciencia_Datos/blob/main/docs/Learning/Estadistica/ejercicios-distribuciones-discretas.ipynb) |
| Distribuciones Continuas | `ejercicios-distribuciones-continuas.ipynb` | [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/DanielMf31/Ciencia_Datos/blob/main/docs/Learning/Estadistica/ejercicios-distribuciones-continuas.ipynb) |
| Intervalos de Confianza y Tests | `ejercicios-intervalos-hipotesis.ipynb` | [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/DanielMf31/Ciencia_Datos/blob/main/docs/Learning/Estadistica/ejercicios-intervalos-hipotesis.ipynb) |
| Prueba Chi-cuadrado | `prueba-chi-cuadrado.ipynb` | [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/DanielMf31/Ciencia_Datos/blob/main/docs/Learning/Estadistica/prueba-chi-cuadrado.ipynb) |

### Guias de ML y Deep Learning

| Tema | Notebook | Colab |
|------|----------|-------|
| Guia Completa de Algoritmos ML | `guia-completa-algoritmos-ml.ipynb` | [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/DanielMf31/Ciencia_Datos/blob/main/docs/Learning/Teoria-ML/guia-completa-algoritmos-ml.ipynb) |
| Regresion Multiple y Gradient Descent | `regresion-multiple-gradient-descent.ipynb` | [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/DanielMf31/Ciencia_Datos/blob/main/docs/Learning/Teoria-ML/regresion-multiple-gradient-descent.ipynb) |
| Bias, Varianza y Ruido | `bias-varianza-ruido-techo-rendimiento.ipynb` | [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/DanielMf31/Ciencia_Datos/blob/main/docs/Learning/Teoria-ML/bias-varianza-ruido-techo-rendimiento.ipynb) |
| Teoria de la Informacion | `teoria-informacion-entropia-cross-entropy.ipynb` | [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/DanielMf31/Ciencia_Datos/blob/main/docs/Learning/Teoria-ML/teoria-informacion-entropia-cross-entropy.ipynb) |
| LSTM: Como Funciona Por Dentro | `lstm-redes-recurrentes.ipynb` | [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/DanielMf31/Ciencia_Datos/blob/main/docs/Learning/Teoria-ML/lstm-redes-recurrentes.ipynb) |
| Transformers vs LSTM | `transformers-vs-lstm-attention.ipynb` | [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/DanielMf31/Ciencia_Datos/blob/main/docs/Learning/Teoria-ML/transformers-vs-lstm-attention.ipynb) |
| Estructuras de Datos para ML | `estructuras-datos-algoritmos-ml.ipynb` | [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/DanielMf31/Ciencia_Datos/blob/main/docs/Learning/Teoria-ML/estructuras-datos-algoritmos-ml.ipynb) |
| Escalado y Normalizacion | `escalado-normalizacion-datos.ipynb` | [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/DanielMf31/Ciencia_Datos/blob/main/docs/Learning/Preprocesamiento/escalado-normalizacion-datos.ipynb) |

---

## Proyectos

### 1. Mantenimiento Predictivo — NASA C-MAPSS FD001
**6 notebooks** | `notebooks/CMAP/FD001/`

Prediccion de Vida Util Restante (RUL) de motores de avion con el dataset NASA C-MAPSS. Pipeline completo: ingesta, EDA, feature engineering, modelos clasicos (RF, XGBoost, SVR) y LSTM con GPU.

| Notebook | Mision | Mejor RMSE |
|----------|--------|------------|
| 01 | Ingesta y calculo del RUL (piecewise linear, cap=130) | — |
| 02 | EDA de sensores: cuales capturan degradacion | — |
| 03 | Feature engineering: rolling stats, tendencias, normalizacion | — |
| 04 | Modelos clasicos: LR, RF, XGBoost, SVR | 18.70 (RF) |
| 05 | LSTM con GPU (TensorFlow) | 14.06 |
| 06 | Evaluacion: NASA Score, sistema de alertas verde/amarillo/rojo | — |

### 2. Stroke Prediction (ML con Desbalance Extremo)
**5 notebooks** | `notebooks/stroke_prediction/`

Prediccion de ictus cerebral con desbalance severo (95% negativo, 5% positivo). SMOTE, optimizacion de umbral y modelo de costes para contexto medico. Recall final: 98%.

### 3. Telemetria Vehicular (Datos Simulados)
**31 notebooks** | `notebooks/telemetria_vehicular/`

Proyecto fundacional de DS con datos simulados de flotas vehiculares. Cubre desde NumPy/Pandas hasta ML y series temporales.

### 4. NYC Taxi Trips (BigQuery — Datos Reales)
**26 notebooks** | `notebooks/nyc_taxi/`

Analisis de ~146M viajes de taxi en NYC (2015) usando Google BigQuery.

### 5. Breast Cancer Classification (ML Medico)
**5 notebooks** | `notebooks/breast_cancer/`

Clasificacion binaria de tumores mamarios (maligno/benigno) con el dataset Wisconsin.

---

## Estructura del Proyecto

```
Ciencia_Datos/
├── notebooks/
│   ├── CMAP/FD001/                # Mantenimiento predictivo NASA (6 notebooks)
│   ├── stroke_prediction/         # Prediccion de ictus (5 notebooks)
│   ├── telemetria_vehicular/      # Telemetria vehicular (31 notebooks)
│   ├── nyc_taxi/                  # NYC Taxi BigQuery (26 notebooks)
│   └── breast_cancer/             # Cancer de mama (5 notebooks)
├── docs/
│   ├── 00_formulario_estadistico.ipynb  # Formulario completo
│   ├── essential_commands.ipynb         # Referencia de comandos
│   └── Learning/
│       ├── Teoria-ML/             # Guias de ML/DL (8 notebooks)
│       ├── Estadistica/           # Ejercicios de estadistica (6 notebooks)
│       ├── Preprocesamiento/      # Escalado y normalizacion
│       └── MLOps/                 # Referencia MLOps (9 notebooks)
├── data/                          # Datasets
├── models/                        # Modelos entrenados
├── requirements.txt
└── setup_nvidia_system.sh         # Setup CUDA/GPU
```

---

## Instalacion

```bash
git clone https://github.com/DanielMf31/Ciencia_Datos.git
cd Ciencia_Datos
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
jupyter lab
```

### GPU (opcional, para LSTM)

```bash
sudo bash setup_nvidia_system.sh        # Instala driver + CUDA + cuDNN
sudo reboot
bash setup_nvidia_system.sh --post-reboot  # Configura TensorFlow
```

---

## Tecnologias

| Categoria | Herramientas |
|-----------|-------------|
| Lenguaje | Python 3.12 |
| Data | NumPy, Pandas, PyArrow |
| Visualizacion | Matplotlib, Seaborn, Plotly |
| Estadistica | SciPy, Statsmodels |
| ML | Scikit-learn, XGBoost |
| Deep Learning | TensorFlow, Keras |
| Cloud | Google BigQuery |
| GPU | CUDA 12, cuDNN, NVIDIA RTX |

---

## Licencia

Uso educativo. Datasets publicos:
- [NASA C-MAPSS](https://data.nasa.gov/dataset/C-MAPSS-Aircraft-Engine-Simulator-Data/xaut-bemq) (NASA Open Data)
- [NYC Taxi Trips](https://console.cloud.google.com/bigquery?p=bigquery-public-data&d=new_york_taxi_trips) (BigQuery)
- [Wisconsin Breast Cancer](https://archive.ics.uci.edu/dataset/17/breast+cancer+wisconsin+diagnostic) (UCI)
- [Stroke Prediction](https://www.kaggle.com/datasets/fedesoriano/stroke-prediction-dataset) (Kaggle)
