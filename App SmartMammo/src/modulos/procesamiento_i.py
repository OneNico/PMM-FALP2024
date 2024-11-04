# src/modulos/procesamiento_i.py

import streamlit as st
from PIL import Image
import os
from transformers import pipeline
import torch
import logging
import pydicom
import numpy as np

logger = logging.getLogger(__name__)

def procesamiento_individual(opciones):
    uploaded_image = opciones.get('uploaded_image')

    if uploaded_image is not None:
        # Procesar la imagen
        image_display, image_classification, tipo_archivo = procesar_archivo(uploaded_image)

        if image_classification:
            # Nombres de los modelos en Hugging Face
            model_name_primary = "nc7777/clasificador_primario"
            model_name_secondary_masas = "nc7777/clasificador_masas"
            model_name_secondary_calcifi = "nc7777/clasificador_calcificaciones"

            # Cargar los modelos desde Hugging Face
            classifier_primary = cargar_modelo(model_name_primary)
            classifier_secondary_masas = cargar_modelo(model_name_secondary_masas)
            classifier_secondary_calcifi = cargar_modelo(model_name_secondary_calcifi)

            if classifier_primary:
                # Definir mapeo de etiquetas para el modelo primario
                prediction_mapping_primary = {
                    '0': 'calcificaciones',
                    '1': 'masas',
                    '2': 'no_encontrado'
                }

                # Realizar la inferencia primaria
                mapped_result_primary = clasificar_imagen(image_classification, classifier_primary, prediction_mapping_primary)

                # Mostrar los resultados de la clasificación primaria en tarjeta
                mostrar_resultados_tarjeta(mapped_result_primary, "Clasificación Primaria", image_display)

                # Variables para los resultados secundarios
                mapped_result_secondary_masas = None
                mapped_result_secondary_calcifi = None

                # Lógica para clasificación secundaria según la clasificación primaria
                if mapped_result_primary:
                    if mapped_result_primary['label'] == 'masas':
                        if classifier_secondary_masas:
                            # Definir mapeo de etiquetas para el modelo secundario de masas
                            prediction_mapping_secondary_masas = {
                                '0': 'benigno',
                                '1': 'maligno',
                                '2': 'sospechoso'
                            }

                            # Realizar la inferencia secundaria para masas
                            mapped_result_secondary_masas = clasificar_imagen(image_classification, classifier_secondary_masas, prediction_mapping_secondary_masas)

                            # Mostrar los resultados de la clasificación secundaria para masas en tarjeta
                            mostrar_resultados_tarjeta(mapped_result_secondary_masas, "Clasificación Secundaria para Masas")

                        else:
                            st.error("No se pudo cargar el modelo secundario para la clasificación de masas.")

                    elif mapped_result_primary['label'] == 'calcificaciones':
                        if classifier_secondary_calcifi:
                            # Definir mapeo de etiquetas para el modelo secundario de calcificaciones
                            prediction_mapping_secondary_calcifi = {
                                '0': 'benigno',
                                '1': 'maligno',
                                '2': 'sospechoso'
                            }

                            # Realizar la inferencia secundaria para calcificaciones
                            mapped_result_secondary_calcifi = clasificar_imagen(image_classification, classifier_secondary_calcifi, prediction_mapping_secondary_calcifi)

                            # Mostrar los resultados de la clasificación secundaria para calcificaciones en tarjeta
                            mostrar_resultados_tarjeta(mapped_result_secondary_calcifi, "Clasificación Secundaria para Calcificaciones")
                        else:
                            st.error("No se pudo cargar el modelo secundario para la clasificación de calcificaciones.")
            else:
                st.error("No se pudo cargar el modelo primario para la clasificación.")
        else:
            st.error("No se pudo procesar la imagen cargada.")
    else:
        st.info("Por favor, carga una imagen DICOM, PNG o JPG para realizar la clasificación.")

# Funciones auxiliares

def cargar_modelo(model_name):
    """
    Carga un modelo de clasificación de imágenes desde Hugging Face.
    """
    try:
        # Determinar dispositivo
        if torch.cuda.is_available():
            device = 0  # GPU CUDA
        elif torch.backends.mps.is_available():
            device = "mps"  # GPU Apple MPS
        else:
            device = -1  # CPU

        # Cargar el pipeline de clasificación de imágenes
        classifier = pipeline("image-classification", model=model_name, device=device)
        return classifier
    except Exception as e:
        st.error(f"Ocurrió un error al cargar el modelo {model_name}: {e}")
        return None

def procesar_archivo(imagen_file):
    """
    Procesa un archivo de imagen en formato DICOM, PNG o JPG.
    Devuelve la imagen para mostrar y la imagen procesada para clasificación.
    """
    try:
        # Obtener el nombre del archivo y su extensión
        filename = imagen_file.name
        extension = os.path.splitext(filename)[1].lower()

        if extension in ['.dcm', '.dicom']:
            # Procesar archivo DICOM
            image_display, image_classification = leer_dicom(imagen_file)
            return image_display, image_classification, 'DICOM'

        elif extension in ['.png', '.jpg', '.jpeg']:
            # Procesar archivo PNG o JPG
            image_display, image_classification = leer_imagen(imagen_file)
            return image_display, image_classification, 'PNG_JPG'

        else:
            st.error("Formato de archivo no soportado. Por favor, carga una imagen en formato DICOM, PNG o JPG.")
            return None, None, None

    except Exception as e:
        logger.error(f"Error al procesar el archivo: {e}")
        st.error(f"Error al procesar el archivo: {e}")
        return None, None, None

def leer_dicom(dicom_file):
    """
    Lee un archivo DICOM y devuelve la imagen para mostrar y para clasificación.
    """
    try:
        # Leer el archivo DICOM desde el objeto UploadedFile
        dicom = pydicom.dcmread(dicom_file)
        original_image = dicom.pixel_array

        # Aplicar VOI LUT si está disponible
        if hasattr(pydicom.pixel_data_handlers, 'apply_voi_lut'):
            img_windowed = pydicom.pixel_data_handlers.apply_voi_lut(original_image, dicom)
        else:
            img_windowed = original_image

        # Manejar Photometric Interpretation
        photometric_interpretation = dicom.get('PhotometricInterpretation', 'UNKNOWN')
        if photometric_interpretation == 'MONOCHROME1':
            img_windowed = np.max(img_windowed) - img_windowed

        # Normalizar la imagen para mostrar
        img_normalized_display = (img_windowed - np.min(img_windowed)) / (np.max(img_windowed) - np.min(img_windowed))
        img_normalized_display = (img_normalized_display * 255).astype(np.uint8)

        # Crear imagen para mostrar sin redimensionar
        image_display = Image.fromarray(img_normalized_display).convert('L')

        # Imagen para clasificación (redimensionada a 224x224)
        image_classification = image_display.resize((224, 224)).convert('RGB')

        return image_display, image_classification

    except Exception as e:
        logger.error(f"Error al procesar el archivo DICOM: {e}")
        st.error(f"Error al procesar el archivo DICOM: {e}")
        return None, None

def leer_imagen(imagen_file):
    """
    Lee una imagen PNG o JPG y devuelve la imagen para mostrar y para clasificación.
    """
    try:
        # Leer la imagen usando PIL
        image_display = Image.open(imagen_file).convert('RGB')

        # Imagen para clasificación (redimensionada a 224x224)
        image_classification = image_display.resize((224, 224))

        return image_display, image_classification
    except Exception as e:
        logger.error(f"Error al procesar la imagen: {e}")
        st.error(f"Error al procesar la imagen: {e}")
        return None, None

def clasificar_imagen(image, classifier, prediction_mapping):
    """
    Realiza la inferencia sobre una imagen y mapea las etiquetas predichas.
    """
    try:
        resultado = classifier(image)
        if len(resultado) == 0:
            st.error("No se obtuvieron resultados de la clasificación.")
            return None
        top_result = resultado[0]
        pred_label_normalized = top_result['label'].lower()
        mapped_label = prediction_mapping.get(pred_label_normalized, pred_label_normalized)
        return {
            'label': mapped_label,
            'score': top_result['score']
        }
    except Exception as e:
        logger.error(f"Error durante la clasificación: {e}")
        st.error(f"Error durante la clasificación: {e}")
        return None

def mostrar_resultados_tarjeta(mapped_result, titulo, image_display=None):
    """
    Muestra los resultados de la clasificación en una tarjeta estilizada en Streamlit.
    """
    if mapped_result:
        label = mapped_result['label'].capitalize()
        score = mapped_result['score'] * 100
        # Definir colores basados en la clasificación
        if label.lower() == 'benigno':
            color = "#d4edda"  # Verde claro
            text_color = "#155724"  # Verde oscuro
        elif label.lower() == 'maligno':
            color = "#f8d7da"  # Rojo claro
            text_color = "#721c24"  # Rojo oscuro
        elif label.lower() == 'sospechoso':
            color = "#fff3cd"  # Amarillo claro
            text_color = "#856404"  # Amarillo oscuro
        elif label.lower() == 'no_encontrado':
            color = "#d1ecf1"  # Azul claro
            text_color = "#0c5460"  # Azul oscuro
        else:
            color = "#e2e3e5"  # Gris claro
            text_color = "#41464b"  # Gris oscuro

        # Crear la tarjeta utilizando HTML y CSS
        tarjeta_html = f"""
        <div style="
            background-color: {color};
            color: {text_color};
            padding: 20px;
            border-radius: 10px;
            box-shadow: 2px 2px 12px rgba(0,0,0,0.1);
            margin-bottom: 20px;
        ">
            <h3 style="margin-bottom: 10px;">{titulo}</h3>
            <p style="font-size: 18px;"><strong>{label}</strong></p>
            <p style="font-size: 16px;">Confianza: {score:.0f}%</p>
        </div>
        """

        # Mostrar la imagen si está disponible
        if image_display:
            # Crear una columna para la imagen y otra para la tarjeta
            col_img, col_tarjeta = st.columns([1, 2])
            with col_img:
                st.image(image_display, caption="Imagen Procesada", use_column_width=True)
            with col_tarjeta:
                st.markdown(tarjeta_html, unsafe_allow_html=True)
        else:
            # Mostrar solo la tarjeta si no hay imagen
            st.markdown(tarjeta_html, unsafe_allow_html=True)
    else:
        st.write(f"No se pudieron obtener resultados de la {titulo.lower()}.")

