# src/utilidades/guardar_resultados.py

import os
from PIL import Image
from src.config.settings import DATA_PROCESSED_DIR
import logging

def guardar_resultados(resultados):
    """
    Guarda las imágenes procesadas en el directorio especificado.

    Parameters:
        resultados (list): Lista de imágenes procesadas en formato PIL.Image.Image.

    Returns:
        None
    """
    try:
        os.makedirs(DATA_PROCESSED_DIR, exist_ok=True)
        for idx, imagen in enumerate(resultados):
            if imagen is not None:
                nombre_archivo = f"imagen_procesada_{idx + 1}.png"
                path = os.path.join(DATA_PROCESSED_DIR, nombre_archivo)
                imagen.save(path)
                logging.info(f"Imagen guardada en {path}")
    except Exception as e:
        logging.error(f"Error al guardar imágenes: {e}")
        raise e  # Corregido de 'raise dime ok' a 'raise e'
