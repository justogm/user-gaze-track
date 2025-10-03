#!/usr/bin/env bash

set -e

ENV_NAME="user-gaze-track"
VENV_DIR=".venv"

# --------- Detectar gestor de entornos disponible ---------------
# Verificar si se pasa el argumento --venv para forzar el uso de venv
if [ "$1" = "--venv" ]; then
    echo "🔧 Forzando el uso de Python venv..."
    USE_CONDA=false
elif command -v conda &> /dev/null; then
    echo "🐍 Conda detectado. Usando conda para gestión de entornos..."
    USE_CONDA=true
else
    echo "⚠️  Conda no disponible. Usando Python venv como fallback..."
    USE_CONDA=false
fi
# ----------------------------------------------------------------

if [ "$USE_CONDA" = true ]; then
    # --------- Gestión con Conda ---------------
    if conda env list | grep -q "^${ENV_NAME}\s"; then
        echo "✅ El entorno conda '$ENV_NAME' ya existe."
    else
        echo "⚙️  Creando el entorno conda '$ENV_NAME' desde environment.yml..."
        conda env create -n "$ENV_NAME" -f environment.yml
        echo "✅ Entorno conda '$ENV_NAME' creado."
    fi
    
    # Activar entorno conda
    echo "🔄 Activando el entorno conda '$ENV_NAME'..."
    eval "$(conda shell.bash hook)"
    conda activate "$ENV_NAME"
    # ------------------------------------------
else
    # --------- Gestión con Python venv -------
    if [ -d "$VENV_DIR" ]; then
        echo "✅ El entorno virtual '$VENV_DIR' ya existe."
        VENV_EXISTS=true
    else
        echo "⚙️  Creando entorno virtual Python '$VENV_DIR'..."
        python3 -m venv "$VENV_DIR"
        echo "✅ Entorno virtual '$VENV_DIR' creado."
        VENV_EXISTS=false
    fi
    
    # Activar entorno virtual
    echo "🔄 Activando el entorno virtual '$VENV_DIR'..."
    source "$VENV_DIR/bin/activate"
    
    # Solo instalar dependencias si el entorno es nuevo o faltan paquetes críticos
    if [ "$VENV_EXISTS" = false ] || ! python -c "import flask" &> /dev/null; then
        echo "📦 Instalando dependencias..."
        if [ -f "requirements.txt" ] && [ -s "requirements.txt" ]; then
            echo "   Desde requirements.txt..."
            pip install -r requirements.txt
        else
            echo "   Dependencias básicas..."
            pip install flask==3.1.0 flask-sqlalchemy==3.1.1 flasgger==0.9.7.1 numpy==1.26.4 ttkbootstrap==1.10.1
        fi
        echo "✅ Dependencias instaladas."
    else
        echo "✅ Dependencias ya instaladas, omitiendo instalación."
    fi
    # ------------------------------------------
fi

# -------- Configuración opcional --------
echo ""
read -p "¿Desea modificar las configuraciones antes de ejecutar la aplicación? (s/n): " config_choice
if [[ $config_choice =~ ^[Ss]$ ]]; then
    echo "⚙️  Abriendo configurador..."
    python src/config.py
    echo "✅ Configuración completada."
fi
# ----------------------------------------

# ----- Ejecución de la aplicación -----
echo "🚀 Ejecutando la aplicación..."
python src/app.py
# -------------------------------------