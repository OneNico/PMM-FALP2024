# src/procesamiento/procesar.py

import numpy as np
from src.procesamiento.lectura_dicom import leer_imagen_dicom
from src.procesamiento.transformaciones import aplicar_transformaciones
import logging
import streamlit as st
import io
from PIL import Image

logger = logging.getLogger(__name__)



@st.cache_data(show_spinner=False, ttl=3600)
def procesar_imagen_dicom_cached(dicom_file_bytes, opciones):
    """
    Procesa una imagen DICOM según las opciones seleccionadas y devuelve la imagen y el dataset.
    Esta función está cacheada para evitar reprocesar imágenes ya procesadas.

    :param dicom_file_bytes: Bytes del archivo DICOM.
    :param opciones: Diccionario de opciones de procesamiento.
    :return: Imagen procesada y dataset.
    """
    try:
        # Leer el dataset DICOM
        ds = leer_imagen_dicom(io.BytesIO(dicom_file_bytes))

        # Verificar si ds es None
        if ds is None:
            logger.warning("Dataset DICOM no pudo ser leído.")
            return None, None

        # Obtener los datos de píxeles
        data = ds.pixel_array

        # Aplicar VOI LUT si está seleccionado
        if opciones.get("aplicar_voilut", True):
            from pydicom.pixel_data_handlers.util import apply_voi_lut
            data = apply_voi_lut(data, ds)

        # Si la interpretación es MONOCHROME1, invertimos la imagen y cambiamos a MONOCHROME2
        if ds.PhotometricInterpretation == 'MONOCHROME1':
            data = np.amax(data) - data
            ds.PhotometricInterpretation = 'MONOCHROME2'

        # Invertir interpretación si el usuario lo seleccionó
        if opciones.get('invertir_interpretacion', False):
            data = np.amax(data) - data

        # Normalizar la imagen
        data = data - np.min(data)
        if np.max(data) != 0:
            data = data / np.max(data)
        else:
            data = np.zeros(data.shape)

        # Aplicar transformaciones si está seleccionado
        if opciones.get("aplicar_transformaciones", False):
            transformaciones_seleccionadas = opciones.get('transformaciones_seleccionadas', {})
            data = aplicar_transformaciones(data, transformaciones_seleccionadas)

        # Convertir a uint8
        image = (data * 255).astype(np.uint8)

        return image, ds

    except Exception as e:
        logger.error(f"Error al procesar el archivo DICOM: {e}")
        return None, None
