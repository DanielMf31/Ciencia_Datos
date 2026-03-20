#!/bin/bash
# ============================================
# Setup Script — Ciencia de Datos Portfolio
# ============================================

set -e

echo "========================================"
echo "  Ciencia de Datos — Setup Automático"
echo "========================================"
echo ""

# Check Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 no encontrado. Instálalo primero:"
    echo "   sudo apt install python3 python3-venv python3-pip"
    exit 1
fi

PYTHON_VERSION=$(python3 --version 2>&1)
echo "✓ $PYTHON_VERSION detectado"

# Create virtual environment
if [ ! -d ".venv" ]; then
    echo ""
    echo "📦 Creando entorno virtual..."
    python3 -m venv .venv
    echo "✓ Entorno virtual creado en .venv/"
else
    echo "✓ Entorno virtual ya existe"
fi

# Activate
source .venv/bin/activate
echo "✓ Entorno virtual activado"

# Install dependencies
echo ""
echo "📥 Instalando dependencias..."
pip install --upgrade pip -q
pip install -r requirements.txt -q
echo "✓ Dependencias instaladas"

# Install optional dependencies
echo ""
echo "📥 Instalando dependencias opcionales..."
pip install imbalanced-learn -q 2>/dev/null && echo "✓ imbalanced-learn (SMOTE)" || echo "⚠ imbalanced-learn no instalado"
pip install google-cloud-bigquery-storage -q 2>/dev/null && echo "✓ BigQuery Storage API" || echo "⚠ BigQuery Storage no instalado (opcional)"

# Create necessary directories
echo ""
echo "📁 Verificando estructura de directorios..."
mkdir -p data/breast_cancer/processed
mkdir -p data/heart_attack/processed
mkdir -p data/nyc_taxi/cache
mkdir -p models
echo "✓ Directorios verificados"

# Download datasets if not present
echo ""
echo "📊 Verificando datasets..."
if [ ! -f "data/breast_cancer/wdbc.data" ]; then
    echo "⚠ Dataset Breast Cancer no encontrado."
    echo "  Descárgalo de: https://archive.ics.uci.edu/dataset/17/breast+cancer+wisconsin+diagnostic"
    echo "  Extrae wdbc.data en data/breast_cancer/"
else
    echo "✓ Breast Cancer dataset presente"
fi

if [ ! -f "data/heart_attack/healthcare-dataset-stroke-data.csv" ]; then
    echo "⚠ Dataset Stroke no encontrado."
    echo "  Descárgalo de: https://www.kaggle.com/datasets/fedesoriano/stroke-prediction-dataset"
    echo "  Extrae el CSV en data/heart_attack/"
else
    echo "✓ Stroke dataset presente"
fi

# BigQuery setup info
echo ""
echo "========================================"
echo "  ✅ Setup completado"
echo "========================================"
echo ""
echo "Para empezar:"
echo "  source .venv/bin/activate"
echo "  jupyter lab"
echo ""
echo "Proyectos disponibles:"
echo "  📓 notebooks/breast_cancer/       — Clasificación de tumores (5 notebooks)"
echo "  📓 notebooks/stroke_prediction/   — Predicción de ictus (5 notebooks)"
echo "  📓 notebooks/nyc_taxi/            — NYC Taxi + BigQuery (26 notebooks)"
echo "  📓 notebooks/telemetria_vehicular/ — Telemetría vehicular (31 notebooks)"
echo ""
echo "Para NYC Taxi (BigQuery), configura primero:"
echo "  gcloud auth login"
echo "  gcloud auth application-default login"
echo ""
