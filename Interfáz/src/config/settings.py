# src/config/settings.py

import os

# Configuraciones generales
APP_NAME = "Visualizador de Imágenes DICOM"
VERSION = "1.0.0"

# Directorio base
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Definir el directorio de datos procesados
DATA_PROCESSED_DIR = os.path.join(os.getcwd(), 'data', 'processed')

# Directorio de logs
LOG_DIR = os.path.join(BASE_DIR, 'logs')

# Asegurarse de que el directorio de logs existe
os.makedirs(LOG_DIR, exist_ok=True)
