# src/procesamiento/lectura_dicom.py

import pydicom
import io
import logging

logger = logging.getLogger(__name__)

def leer_imagen_dicom(dicom_file):
    """
    Lee un archivo DICOM y devuelve el dataset.

    :param dicom_file: Archivo DICOM a leer.
    :return: Dataset DICOM.
    """
    try:
        dicom_bytes = dicom_file.read()
        dicom_file.seek(0)  # Resetear el puntero del archivo
        ds = pydicom.dcmread(io.BytesIO(dicom_bytes))
        return ds
    except Exception as e:
        logger.error(f"Error al leer el archivo DICOM {dicom_file.name}: {e}")
        return None

def obtener_metadatos_relevantes(ds):
    """
    Extrae y devuelve los metadatos relevantes del dataset DICOM.

    :param ds: Dataset DICOM.
    :return: Diccionario de metadatos.
    """
    metadatos = {
        "Patient ID": getattr(ds, 'PatientID', 'Desconocido'),
        "Study Date": getattr(ds, 'StudyDate', 'Desconocido'),
        "Modality": getattr(ds, 'Modality', 'Desconocido'),
        "Photometric Interpretation": getattr(ds, 'PhotometricInterpretation', 'Desconocido'),
        "Rows": getattr(ds, 'Rows', 'Desconocido'),
        "Columns": getattr(ds, 'Columns', 'Desconocido'),
        # Puedes agregar más metadatos si lo deseas
    }
    return metadatos
