# src/procesamiento/convertir_png.py

import pydicom
import numpy as np
import cv2
import io
from pydicom.pixel_data_handlers.util import apply_voi_lut
import logging

logger = logging.getLogger(__name__)

def convertir_dicom_a_imagen(dicom_path, output_size=(224, 224)):
    """
    Convierte un archivo DICOM a una imagen numpy array con el tamaño especificado.

    :param dicom_path: Ruta al archivo DICOM.
    :param output_size: Tupla (ancho, alto) para redimensionar la imagen.
    :return: Imagen como numpy array en formato uint8 o None si falla la conversión.
    """
    try:
        # Leer el dataset DICOM
        dicom = pydicom.dcmread(dicom_path)
        original_image = dicom.pixel_array

        # Aplicar VOI LUT con prefer_lut=True (priorizando LUT si está presente)
        img_windowed = apply_voi_lut(original_image, dicom, prefer_lut=True)

        # Manejar Photometric Interpretation si es MONOCHROME1 (invertir la imagen)
        photometric_interpretation = dicom.get('PhotometricInterpretation', 'UNKNOWN')
        if photometric_interpretation == 'MONOCHROME1':
            img_windowed = img_windowed.max() - img_windowed
            print(f"Imagen '{dicom_path}' invertida debido a Photometric Interpretation: {photometric_interpretation}")
        else:
            print(f"Imagen '{dicom_path}' Photometric Interpretation: {photometric_interpretation}")

        # Normalizar la imagen para que esté en el rango [0, 255]
        img_normalized = (img_windowed - img_windowed.min()) / (img_windowed.max() - img_windowed.min()) * 255
        img_normalized = img_normalized.astype(np.uint8)

        # Redimensionar la imagen al tamaño especificado
        img_resized = cv2.resize(img_normalized, output_size, interpolation=cv2.INTER_AREA)

        return img_resized

    except Exception as e:
        logger.error(f"Error al procesar {dicom_path}: {e}")
        return None
