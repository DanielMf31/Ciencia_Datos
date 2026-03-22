#!/bin/bash
# =============================================================================
# Script de instalacion de NVIDIA CUDA a nivel de sistema
# Para: Ubuntu 24.04+ con GPU NVIDIA
# Objetivo: Driver 550 + CUDA 12.4 + cuDNN 9 a nivel de sistema
# =============================================================================
#
# INSTRUCCIONES:
# 1. Leer el script completo antes de ejecutar
# 2. Ejecutar con: sudo bash setup_nvidia_system.sh
# 3. Reiniciar el PC al finalizar
# 4. Despues del reboot, ejecutar: bash setup_nvidia_system.sh --post-reboot
#
# =============================================================================

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

VENV_DIR="$HOME/Documentos/Documentos_Trabajo/Ingenieria/Programacion/VSCode/Proyectos_personales/Ciencia_Datos/.venv"

# --- Funciones auxiliares ---
info()  { echo -e "${GREEN}[INFO]${NC} $1"; }
warn()  { echo -e "${YELLOW}[WARN]${NC} $1"; }
error() { echo -e "${RED}[ERROR]${NC} $1"; }

check_gpu() {
    if ! lspci | grep -qi nvidia; then
        error "No se detecto GPU NVIDIA"
        exit 1
    fi
    info "GPU detectada: $(lspci | grep -i nvidia | head -1 | cut -d: -f3)"
}

# =============================================================================
# FASE 1: Pre-reboot (requiere sudo)
# =============================================================================
phase1_install() {
    info "=== FASE 1: Instalacion de Driver + CUDA + cuDNN ==="

    check_gpu

    # 1. Mostrar estado actual
    info "Estado actual:"
    if nvidia-smi &>/dev/null; then
        CURRENT_DRIVER=$(nvidia-smi --query-gpu=driver_version --format=csv,noheader 2>/dev/null || echo "desconocido")
        info "  Driver actual: $CURRENT_DRIVER"
    else
        warn "  No hay driver NVIDIA instalado"
    fi

    # 2. Agregar repositorio CUDA de NVIDIA
    info "Agregando repositorio CUDA de NVIDIA..."

    # Detectar arquitectura y version de Ubuntu
    ARCH=$(dpkg --print-architecture)
    DISTRO=$(. /etc/os-release && echo "${ID}${VERSION_ID}" | tr -d '.')

    # Descargar e instalar keyring
    KEYRING_URL="https://developer.download.nvidia.com/compute/cuda/repos/${DISTRO}/${ARCH}/cuda-keyring_1.1-1_all.deb"
    info "Descargando keyring desde: $KEYRING_URL"
    wget -q "$KEYRING_URL" -O /tmp/cuda-keyring.deb 2>/dev/null || {
        # Fallback para Ubuntu 24.04
        KEYRING_URL="https://developer.download.nvidia.com/compute/cuda/repos/ubuntu2404/${ARCH}/cuda-keyring_1.1-1_all.deb"
        wget -q "$KEYRING_URL" -O /tmp/cuda-keyring.deb
    }
    dpkg -i /tmp/cuda-keyring.deb
    apt-get update -qq

    # 3. Instalar driver 550
    info "Instalando driver NVIDIA 550..."
    apt-get install -y nvidia-driver-550

    # 4. Instalar CUDA Toolkit 12.4
    info "Instalando CUDA Toolkit 12.4..."
    apt-get install -y cuda-toolkit-12-4

    # 5. Instalar cuDNN 9 para CUDA 12
    info "Instalando cuDNN 9..."
    apt-get install -y libcudnn9-cuda-12 libcudnn9-dev-cuda-12

    info "=== Instalacion completada ==="
    info ""
    info "Ahora debes:"
    info "  1. Reiniciar el PC: sudo reboot"
    info "  2. Despues del reboot ejecutar:"
    info "     bash ~/Documentos/Documentos_Trabajo/Ingenieria/Programacion/VSCode/Proyectos_personales/Ciencia_Datos/setup_nvidia_system.sh --post-reboot"
}

# =============================================================================
# FASE 2: Post-reboot (sin sudo)
# =============================================================================
phase2_configure() {
    info "=== FASE 2: Configuracion post-reboot ==="

    # 1. Verificar driver
    if ! nvidia-smi &>/dev/null; then
        error "nvidia-smi no funciona. El driver no se instalo correctamente."
        exit 1
    fi

    info "Driver instalado:"
    nvidia-smi --query-gpu=driver_version,name,memory.total --format=csv,noheader

    # 2. Verificar CUDA
    if [ -d "/usr/local/cuda-12.4" ]; then
        info "CUDA 12.4 encontrado en /usr/local/cuda-12.4"
    elif [ -d "/usr/local/cuda" ]; then
        info "CUDA encontrado en /usr/local/cuda"
    else
        error "CUDA no encontrado en /usr/local/"
        exit 1
    fi

    # 3. Configurar PATH y LD_LIBRARY_PATH en .bashrc
    CUDA_HOME="/usr/local/cuda-12.4"
    if [ ! -d "$CUDA_HOME" ]; then
        CUDA_HOME="/usr/local/cuda"
    fi

    # Verificar si ya esta configurado
    if grep -q "CUDA_HOME" ~/.bashrc; then
        warn "CUDA ya esta configurado en .bashrc. Actualizando..."
        sed -i '/# NVIDIA CUDA/,/# END NVIDIA CUDA/d' ~/.bashrc
    fi

    info "Agregando CUDA a .bashrc..."
    cat >> ~/.bashrc << EOF

# NVIDIA CUDA
export CUDA_HOME=$CUDA_HOME
export PATH=\$CUDA_HOME/bin:\$PATH
export LD_LIBRARY_PATH=\$CUDA_HOME/lib64:\$LD_LIBRARY_PATH
# END NVIDIA CUDA
EOF

    # Aplicar inmediatamente
    export CUDA_HOME=$CUDA_HOME
    export PATH=$CUDA_HOME/bin:$PATH
    export LD_LIBRARY_PATH=$CUDA_HOME/lib64:$LD_LIBRARY_PATH

    # 4. Limpiar paquetes nvidia del venv
    if [ -d "$VENV_DIR" ]; then
        info "Desinstalando paquetes NVIDIA del venv..."
        source "$VENV_DIR/bin/activate"

        pip uninstall -y \
            nvidia-cudnn-cu12 \
            nvidia-cublas-cu12 \
            nvidia-cuda-runtime-cu12 \
            nvidia-cuda-nvcc-cu12 \
            nvidia-cuda-nvrtc-cu12 \
            nvidia-cufft-cu12 \
            nvidia-curand-cu12 \
            nvidia-cusolver-cu12 \
            nvidia-cusparse-cu12 \
            nvidia-nvjitlink-cu12 \
            nvidia-nccl-cu12 \
            2>/dev/null || true

        info "Paquetes NVIDIA eliminados del venv"

        # 5. Actualizar TensorFlow
        info "Instalando TensorFlow compatible..."
        pip install tensorflow==2.18.0

        deactivate
    fi

    # 6. Limpiar kernel.json (quitar LD_LIBRARY_PATH y XLA_FLAGS)
    KERNEL_JSON="$HOME/.local/share/jupyter/kernels/python3/kernel.json"
    if [ -f "$KERNEL_JSON" ]; then
        info "Limpiando kernel.json..."
        python3 -c "
import json
with open('$KERNEL_JSON') as f:
    kj = json.load(f)
if 'env' in kj:
    del kj['env']
with open('$KERNEL_JSON', 'w') as f:
    json.dump(kj, f, indent=1)
print('kernel.json limpiado')
"
    fi

    KERNEL_JSON2="$HOME/.local/share/jupyter/kernels/ciencia_datos/kernel.json"
    if [ -f "$KERNEL_JSON2" ]; then
        python3 -c "
import json
with open('$KERNEL_JSON2') as f:
    kj = json.load(f)
if 'env' in kj:
    del kj['env']
with open('$KERNEL_JSON2', 'w') as f:
    json.dump(kj, f, indent=1)
print('kernel ciencia_datos limpiado')
"
    fi

    # 7. Verificacion final
    info ""
    info "=== VERIFICACION FINAL ==="
    info "Driver:  $(nvidia-smi --query-gpu=driver_version --format=csv,noheader)"
    info "CUDA:    $(nvcc --version 2>/dev/null | grep release | awk '{print $6}' | tr -d ',')"

    if [ -d "$VENV_DIR" ]; then
        source "$VENV_DIR/bin/activate"
        info "TF:      $(python3 -c 'import tensorflow as tf; print(tf.__version__)' 2>/dev/null)"

        GPU_COUNT=$(python3 -c "
import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
import tensorflow as tf
gpus = tf.config.list_physical_devices('GPU')
print(len(gpus))
" 2>/dev/null)

        if [ "$GPU_COUNT" -gt 0 ]; then
            info "GPU:     Detectada ($GPU_COUNT GPU(s))"
        else
            error "GPU:     NO detectada por TensorFlow"
            warn "Puede que necesites reiniciar la sesion o el kernel de Jupyter"
        fi
        deactivate
    fi

    info ""
    info "=== COMPLETADO ==="
    info "Ya no necesitas:"
    info "  - source setup_cuda.sh"
    info "  - LD_LIBRARY_PATH manual"
    info "  - XLA_FLAGS"
    info "  - Paquetes nvidia-* en el venv"
    info ""
    info "Todo funciona desde /usr/local/cuda-12.4 a nivel de sistema."
}

# =============================================================================
# Main
# =============================================================================
case "${1:-}" in
    --post-reboot)
        phase2_configure
        ;;
    --help|-h)
        echo "Uso:"
        echo "  sudo bash $0           # FASE 1: Instalar driver + CUDA + cuDNN (requiere sudo)"
        echo "  bash $0 --post-reboot  # FASE 2: Configurar despues de reiniciar"
        echo "  bash $0 --check        # Solo verificar estado actual"
        ;;
    --check)
        check_gpu
        echo ""
        echo "Driver: $(nvidia-smi --query-gpu=driver_version --format=csv,noheader 2>/dev/null || echo 'no instalado')"
        echo "CUDA:   $(nvcc --version 2>/dev/null | grep release | awk '{print $6}' | tr -d ',' || echo 'no instalado')"
        echo ""
        echo "Paquetes nvidia en venv:"
        $VENV_DIR/bin/pip list 2>/dev/null | grep nvidia || echo "  (ninguno)"
        ;;
    *)
        if [ "$EUID" -ne 0 ]; then
            error "FASE 1 requiere sudo. Ejecuta: sudo bash $0"
            echo "  O usa --post-reboot para la fase 2 (sin sudo)"
            echo "  O usa --check para verificar estado actual"
            exit 1
        fi
        phase1_install
        ;;
esac