# src/ui/clasificacion_deep_learning.py

import streamlit as st
from PIL import Image
import pydicom
from pydicom.pixel_data_handlers.util import apply_voi_lut
import numpy as np
import os
from transformers import pipeline, AutoImageProcessor, AutoConfig, AutoModelForImageClassification
import torch
import logging

# Configuración del logger
logging.basicConfig(level=logging.ERROR)
logger = logging.getLogger(__name__)

def cargar_modelo_primary(model_path):
    """
    Carga el modelo primario de clasificación de imágenes desde la ruta especificada.
    Este modelo clasifica la imagen en 'masas', 'calcificaciones' o 'no_encontrado'.

    :param model_path: Ruta al directorio del modelo primario.
    :return: Pipeline de clasificación de imágenes o None si falla la carga.
    """
    if not os.path.exists(model_path):
        st.error(f"La ruta del modelo primario especificada no existe: {model_path}")
        return None

    try:
        # Determinar dispositivo
        if torch.cuda.is_available():
            device = 0  # GPU CUDA
        elif torch.backends.mps.is_available():
            device = "mps"  # GPU Apple MPS
        else:
            device = -1  # CPU

        # Cargar el pipeline de clasificación de imágenes de manera simplificada
        classifier_primary = pipeline("image-classification", model=model_path, device=device)
        return classifier_primary
    except Exception as e:
        st.error(f"Ocurrió un error al cargar el modelo primario: {e}")
        return None


def cargar_modelo_secondary(model_path):
    """
    Carga el modelo secundario de clasificación de imágenes desde la ruta especificada.
    Este modelo clasifica la masa en 'benigna' o 'maligna'.

    :param model_path: Ruta al directorio del modelo secundario.
    :return: Pipeline de clasificación de imágenes o None si falla la carga.
    """
    if not os.path.exists(model_path):
        st.error(f"La ruta del modelo secundario especificada no existe: {model_path}")
        return None

    try:
        # Determinar dispositivo
        if torch.cuda.is_available():
            device = 0  # GPU CUDA
        elif torch.backends.mps.is_available():
            device = "mps"  # GPU Apple MPS
        else:
            device = -1  # CPU

        # Cargar el pipeline de clasificación de imágenes de manera simplificada
        classifier_secondary = pipeline("image-classification", model=model_path, device=device)
        return classifier_secondary
    except Exception as e:
        st.error(f"Ocurrió un error al cargar el modelo secundario: {e}")
        return None


def cargar_modelo_calci(model_path):
    """
    Carga el modelo CALCI para clasificar calcificaciones.
    Este modelo clasifica en 'benigna', 'sospechosa' o 'maligna'.

    :param model_path: Ruta al directorio del modelo CALCI.
    :return: Pipeline de clasificación de imágenes o None si falla la carga.
    """
    if not os.path.exists(model_path):
        st.error(f"La ruta del modelo CALCI especificada no existe: {model_path}")
        return None

    try:
        # Determinar dispositivo
        if torch.cuda.is_available():
            device = 0  # GPU CUDA
        elif torch.backends.mps.is_available():
            device = "mps"  # GPU Apple MPS
        else:
            device = -1  # CPU

        # Cargar el pipeline de clasificación de imágenes de manera simplificada
        classifier_calci = pipeline("image-classification", model=model_path, device=device)
        return classifier_calci
    except Exception as e:
        st.error(f"Ocurrió un error al cargar el modelo CALCI: {e}")
        return None


def leer_dicom(dicom_file):
    """
    Lee un archivo DICOM y lo convierte a una imagen PIL Image.

    :param dicom_file: Archivo DICOM cargado por el usuario (Streamlit UploadedFile).
    :return: Imagen PIL Image en formato RGB o None si falla la conversión.
    """
    try:
        # Leer el archivo DICOM desde el objeto UploadedFile
        dicom = pydicom.dcmread(dicom_file)
        original_image = dicom.pixel_array

        # Aplicar VOI LUT con prefer_lut=True (priorizando LUT si está presente)
        img_windowed = apply_voi_lut(original_image, dicom, prefer_lut=True)

        # Manejar Photometric Interpretation si es MONOCHROME1 (invertir la imagen)
        photometric_interpretation = dicom.get('PhotometricInterpretation', 'UNKNOWN')
        if photometric_interpretation == 'MONOCHROME1':
            img_windowed = img_windowed.max() - img_windowed
            st.write(f"Imagen invertida debido a Photometric Interpretation: {photometric_interpretation}")
        else:
            st.write(f"Photometric Interpretation: {photometric_interpretation}")

        # Normalizar la imagen para que esté en el rango [0, 255]
        img_normalized = (img_windowed - img_windowed.min()) / (img_windowed.max() - img_windowed.min()) * 255
        img_normalized = img_normalized.astype(np.uint8)

        # Convertir a PIL Image
        image = Image.fromarray(img_normalized).convert('RGB')

        return image

    except Exception as e:
        logger.error(f"Error al procesar el archivo DICOM: {e}")
        st.error(f"Error al procesar el archivo DICOM: {e}")
        return None


def leer_imagen(imagen_file):
    """
    Lee una imagen PNG o JPG y la convierte a una imagen PIL Image.

    :param imagen_file: Archivo PNG o JPG cargado por el usuario (Streamlit UploadedFile).
    :return: Imagen PIL Image en formato RGB o None si falla la conversión.
    """
    try:
        # Leer la imagen usando PIL
        image = Image.open(imagen_file).convert('RGB')

        # Verificar el tamaño y redimensionar si es necesario
        if image.size != (224, 224):
            image = image.resize((224, 224))
            st.write(f"Imagen redimensionada a (224, 224)")
        else:
            st.write(f"Imagen ya tiene el tamaño (224, 224)")

        return image
    except Exception as e:
        logger.error(f"Error al procesar la imagen: {e}")
        st.error(f"Error al procesar la imagen: {e}")
        return None

def procesar_archivo(imagen_file):
    """
    Procesa un archivo de imagen en formato DICOM, PNG o JPG y lo convierte a una imagen PIL Image de 224x224 píxeles.

    :param imagen_file: Archivo cargado por el usuario (Streamlit UploadedFile).
    :return: Tupla (imagen PIL Image, tipo de archivo) o (None, None) si falla la conversión.
    """
    try:
        # Obtener el nombre del archivo y su extensión
        filename = imagen_file.name
        extension = os.path.splitext(filename)[1].lower()

        if extension in ['.dcm', '.dicom']:
            # Procesar archivo DICOM
            image = leer_dicom(imagen_file)
            return image, 'DICOM'

        elif extension in ['.png', '.jpg', '.jpeg']:
            # Procesar archivo PNG o JPG
            image = leer_imagen(imagen_file)
            return image, 'PNG_JPG'

        else:
            st.error("Formato de archivo no soportado. Por favor, carga una imagen en formato DICOM, PNG o JPG.")
            return None, None

    except Exception as e:
        logger.error(f"Error al procesar el archivo: {e}")
        st.error(f"Error al procesar el archivo: {e}")
        return None, None


def clasificar_imagen_primary(image, classifier_primary, prediction_mapping_primary):
    """
    Realiza la inferencia primaria sobre una imagen y mapea las etiquetas predichas.

    :param image: Imagen PIL Image a clasificar.
    :param classifier_primary: Pipeline de clasificación primaria de imágenes.
    :param prediction_mapping_primary: Diccionario para mapear etiquetas predichas a etiquetas legibles.
    :return: Diccionario con etiqueta mapeada y su respectiva puntuación.
    """
    try:
        resultado = classifier_primary(image)
        if len(resultado) == 0:
            st.error("No se obtuvieron resultados de la clasificación primaria.")
            return None
        top_result = resultado[0]
        mapped_result = {
            'label': prediction_mapping_primary.get(top_result['label'], top_result['label']),
            'score': top_result['score']
        }
        return mapped_result
    except Exception as e:
        st.error(f"Ocurrió un error durante la clasificación primaria: {e}")
        return None


def clasificar_imagen_secondary(image, classifier_secondary, prediction_mapping_secondary):
    """
    Realiza la inferencia secundaria sobre una imagen y mapea las etiquetas predichas.

    :param image: Imagen PIL Image a clasificar.
    :param classifier_secondary: Pipeline de clasificación secundaria de imágenes.
    :param prediction_mapping_secondary: Diccionario para mapear etiquetas predichas a etiquetas legibles.
    :return: Diccionario con etiqueta mapeada y su respectiva puntuación.
    """
    try:
        resultado = classifier_secondary(image)
        if len(resultado) == 0:
            st.error("No se obtuvieron resultados de la clasificación secundaria.")
            return None
        top_result = resultado[0]
        mapped_result = {
            'label': prediction_mapping_secondary.get(top_result['label'], top_result['label']),
            'score': top_result['score']
        }
        return mapped_result
    except Exception as e:
        st.error(f"Ocurrió un error durante la clasificación secundaria: {e}")
        return None


def clasificar_imagen_calci(image, classifier_calci, prediction_mapping_calci):
    """
    Realiza la inferencia para calcificaciones sobre una imagen y mapea las etiquetas predichas.

    :param image: Imagen PIL Image a clasificar.
    :param classifier_calci: Pipeline de clasificación CALCI de imágenes.
    :param prediction_mapping_calci: Diccionario para mapear etiquetas predichas a etiquetas legibles.
    :return: Diccionario con etiqueta mapeada y su respectiva puntuación.
    """
    try:
        resultado = classifier_calci(image)
        if len(resultado) == 0:
            st.error("No se obtuvieron resultados de la clasificación de calcificaciones.")
            return None
        top_result = resultado[0]
        mapped_result = {
            'label': prediction_mapping_calci.get(top_result['label'], top_result['label']),
            'score': top_result['score']
        }
        return mapped_result
    except Exception as e:
        st.error(f"Ocurrió un error durante la clasificación de calcificaciones: {e}")
        return None


def mostrar_resultados_primary(mapped_result_primary):
    """
    Muestra los resultados de la clasificación primaria en la interfaz de Streamlit.

    :param mapped_result_primary: Diccionario con etiqueta mapeada y su respectiva puntuación.
    """
    if mapped_result_primary:
        st.write("### Resultado de la Clasificación Primaria")
        st.write(f"**{mapped_result_primary['label'].capitalize()}**: {mapped_result_primary['score'] * 100:.2f}%")
    else:
        st.write("No se pudieron obtener resultados de la clasificación primaria.")


def mostrar_resultados_secondary(mapped_result_secondary):
    """
    Muestra los resultados de la clasificación secundaria en la interfaz de Streamlit.

    :param mapped_result_secondary: Diccionario con etiqueta mapeada y su respectiva puntuación.
    """
    if mapped_result_secondary:
        st.write("### Resultado de la Clasificación Secundaria")
        st.write(f"**{mapped_result_secondary['label'].capitalize()}**: {mapped_result_secondary['score'] * 100:.2f}%")
    else:
        st.write("No se pudieron obtener resultados de la clasificación secundaria.")


def mostrar_resultados_calci(mapped_result_calci):
    """
    Muestra los resultados de la clasificación CALCI en la interfaz de Streamlit.

    :param mapped_result_calci: Diccionario con etiqueta mapeada y su respectiva puntuación.
    """
    if mapped_result_calci:
        st.write("### Resultado de la Clasificación de Calcificaciones")
        st.write(f"**{mapped_result_calci['label'].capitalize()}**: {mapped_result_calci['score'] * 100:.2f}%")
    else:
        st.write("No se pudieron obtener resultados de la clasificación de calcificaciones.")
