# src/modulos/procesamiento_i.py

import numpy as np
import streamlit as st
from PIL import Image
import os
from transformers import pipeline
import torch
import logging
import pydicom

logger = logging.getLogger(__name__)

def procesamiento_individual(opciones):
    uploaded_image = opciones.get('uploaded_image')

    if uploaded_image is not None:
        # Procesar la imagen
        image_display, image_classification, tipo_archivo = procesar_archivo(uploaded_image)

        if image_display and image_classification:
            # Mostrar la imagen cargada en su calidad original
            st.image(image_display, caption='Imagen Cargada', use_column_width=True)

            # Rutas de los modelos
            current_dir = os.path.dirname(os.path.abspath(__file__))
            model_path_primary = os.path.join(current_dir, '../../data/modelos/ViT-large-patch16-224_B/checkpoint-7520')
            model_path_secondary_masas = os.path.join(current_dir, '../../data/modelos/VT_15/checkpoint-7279')
            model_path_secondary_calcifi = os.path.join(current_dir, '../../data/modelos/Cal_ViT-large-patch16-224_A.ipynb', 'checkpoint-3780')

            # Cargar los modelos
            classifier_primary = cargar_modelo(model_path_primary)
            classifier_secondary_masas = cargar_modelo(model_path_secondary_masas)
            classifier_secondary_calcifi = cargar_modelo(model_path_secondary_calcifi)

            if classifier_primary:
                # Definir mapeo de etiquetas para el modelo primario
                prediction_mapping_primary = {
                    '0': 'calcificaciones',
                    '1': 'masas',
                    '2': 'no_encontrado'
                }

                # Realizar la inferencia primaria
                mapped_result_primary = clasificar_imagen(image_classification, classifier_primary, prediction_mapping_primary)

                # Mostrar los resultados de la clasificación primaria
                mostrar_resultados(mapped_result_primary, "Clasificación Primaria")

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

                            # Mostrar los resultados de la clasificación secundaria para masas
                            mostrar_resultados(mapped_result_secondary_masas, "Clasificación Secundaria para Masas")
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

                            # Mostrar los resultados de la clasificación secundaria para calcificaciones
                            mostrar_resultados(mapped_result_secondary_calcifi, "Clasificación Secundaria para Calcificaciones")
                        else:
                            st.error("No se pudo cargar el modelo secundario para la clasificación de calcificaciones.")

                # Mostrar el reporte
                if st.button("Mostrar Reporte"):
                    mostrar_reporte(
                        mapped_result_primary,
                        mapped_result_secondary_masas,
                        mapped_result_secondary_calcifi
                    )
            else:
                st.error("No se pudo cargar el modelo primario para la clasificación.")
        else:
            st.error("No se pudo procesar la imagen cargada.")
    else:
        st.info("Por favor, carga una imagen DICOM, PNG o JPG para realizar la clasificación.")

# Funciones auxiliares

def cargar_modelo(model_path):
    """
    Carga un modelo de clasificación de imágenes desde la ruta especificada.
    """
    if not os.path.exists(model_path):
        st.error(f"La ruta del modelo especificada no existe: {model_path}")
        return None

    try:
        # Determinar dispositivo
        if torch.cuda.is_available():
            device = 0  # GPU CUDA
        elif torch.backends.mps.is_available():
            device = "mps"  # GPU Apple MPS
        else:
            device = -1  # CPU

        # Cargar el pipeline de clasificación de imágenes
        classifier = pipeline("image-classification", model=model_path, device=device)
        return classifier
    except Exception as e:
        st.error(f"Ocurrió un error al cargar el modelo: {e}")
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
        mapped_result = {
            'label': prediction_mapping.get(top_result['label'], top_result['label']),
            'score': top_result['score']
        }
        return mapped_result
    except Exception as e:
        st.error(f"Ocurrió un error durante la clasificación: {e}")
        return None

def mostrar_resultados(mapped_result, titulo):
    """
    Muestra los resultados de la clasificación en la interfaz de Streamlit.
    """
    if mapped_result:
        st.write(f"### Resultado de la {titulo}")
        st.write(f"**{mapped_result['label'].capitalize()}**: {mapped_result['score'] * 100:.2f}%")
    else:
        st.write(f"No se pudieron obtener resultados de la {titulo.lower()}.")

def mostrar_reporte(mapped_result_primary, mapped_result_secondary_masas=None, mapped_result_secondary_calcifi=None):
    """
    Genera y muestra un reporte basado en los resultados de la clasificación de la mamografía.
    """
    st.header("Reporte de Clasificación de Mamografías")

    st.subheader("Resultados de la Clasificación Primaria")
    if mapped_result_primary:
        st.write(f"**{mapped_result_primary['label'].capitalize()}**: {mapped_result_primary['score'] * 100:.2f}%")
    else:
        st.write("No se obtuvieron resultados de la clasificación primaria.")

    if mapped_result_primary and mapped_result_primary['label'] == 'masas' and mapped_result_secondary_masas:
        st.subheader("Resultados de la Clasificación Secundaria para Masas")
        st.write(f"**{mapped_result_secondary_masas['label'].capitalize()}**: {mapped_result_secondary_masas['score'] * 100:.2f}%")

    if mapped_result_primary and mapped_result_primary['label'] == 'calcificaciones' and mapped_result_secondary_calcifi:
        st.subheader("Resultados de la Clasificación Secundaria para Calcificaciones")
        st.write(f"**{mapped_result_secondary_calcifi['label'].capitalize()}**: {mapped_result_secondary_calcifi['score'] * 100:.2f}%")

    st.markdown("---")  # Separador

    st.subheader("Conclusiones")

    # Generar conclusiones basadas en los resultados
    if mapped_result_primary:
        if mapped_result_primary['label'] == 'no_encontrado':
            st.write("**Conclusión:** No se encontraron masas ni calcificaciones en la mamografía analizada. Los tejidos mamarios presentan características normales dentro de los parámetros evaluados. Se recomienda continuar con controles regulares según las indicaciones médicas.")
        elif mapped_result_primary['label'] in ['masas', 'calcificaciones']:
            # Obtener la etiqueta secundaria correspondiente
            if mapped_result_primary['label'] == 'masas' and mapped_result_secondary_masas:
                etiqueta_secundaria = mapped_result_secondary_masas['label']
            elif mapped_result_primary['label'] == 'calcificaciones' and mapped_result_secondary_calcifi:
                etiqueta_secundaria = mapped_result_secondary_calcifi['label']
            else:
                etiqueta_secundaria = None

            if etiqueta_secundaria:
                if etiqueta_secundaria == 'benigno':
                    st.write("**Conclusión:** Se han identificado hallazgos probablemente benignos. Se recomienda una evaluación inmediata con proyecciones adicionales o ecografía y seguimiento a corto plazo cada 6 meses, generalmente durante dos años, para confirmar la estabilidad del hallazgo en tamaño y aspecto.")
                    st.write("Los hallazgos tienen una alta probabilidad de ser benignos (más del 98%). ")
                    st.write("Si en un plazo mínimo de dos años el hallazgo se mantiene estable, se podrá considerar como benigno y continuar con controles anuales.")
                elif etiqueta_secundaria == 'sospechoso':
                    st.write("**Conclusión:** Se han identificado hallazgos sospechosos que requieren mayor evaluación. Se recomienda considerar la realización de una biopsia para caracterizar los hallazgos de manera definitiva y obtener un diagnóstico certero.")
                    st.write("Los hallazgos presentan una sospecha intermedia de malignidad. Es importante seguir las indicaciones médicas para determinar el plan de acción más adecuado.")
                elif etiqueta_secundaria == 'maligno':
                    st.write("**Conclusión:** Los hallazgos sugieren una alta probabilidad de malignidad. Se observan características que podrían indicar la presencia de cáncer, como masas con contornos irregulares o microcalcificaciones anómalas.")
                    st.write("Se recomienda encarecidamente realizar una biopsia para confirmar el diagnóstico y, de ser necesario, iniciar el tratamiento oportuno.")
            else:
                st.write("No se pudo determinar la clasificación secundaria. Se recomienda consultar con un especialista para una evaluación detallada.")
    else:
        st.write("No se pudieron generar conclusiones debido a la falta de resultados en la clasificación primaria.")

    st.markdown("---")  # Separador

    st.write("**Nota:** Este reporte es generado automáticamente y debe ser interpretado por un profesional de la salud. Siempre consulte a su médico para obtener un diagnóstico y tratamiento adecuados.")
