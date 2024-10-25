# src/modulos/procesamiento_m.py

import streamlit as st
from PIL import Image
import os
import logging
import pydicom
import numpy as np

from transformers import pipeline
import torch
from fpdf import FPDF  # Importar fpdf para generar el PDF
from io import BytesIO

logger = logging.getLogger(__name__)

def procesamiento_masivo(opciones):
    uploaded_images = opciones.get('uploaded_images')

    if uploaded_images:
        st.write(f"**Cantidad de imágenes cargadas**: {len(uploaded_images)}")

        # Rutas de los modelos
        current_dir = os.path.dirname(os.path.abspath(__file__))
        model_path_primary = os.path.join(current_dir, '../../data/modelos/ViT-large-patch16-224_B/checkpoint-7520')
        model_path_secondary_masas = os.path.join(current_dir, '../../data/modelos/VT_15/checkpoint-7279')
        model_path_secondary_calcifi = os.path.join(current_dir, '../../data/modelos/Cal_ViT-large-patch16-224_A.ipynb', 'checkpoint-3780')

        # Llamar a la función de procesamiento masivo
        procesar_imagenes_masivas(uploaded_images, model_path_primary, model_path_secondary_masas, model_path_secondary_calcifi)
    else:
        st.info("Por favor, carga una o más imágenes DICOM, PNG o JPG para realizar la clasificación.")

def procesar_imagenes_masivas(uploaded_images, model_path_primary, model_path_secondary_masas, model_path_secondary_calcifi):
    """
    Procesa múltiples imágenes para clasificación masiva.
    Clasifica cada imagen en la clasificación primaria y secundaria,
    luego ordena y muestra los nombres de las imágenes según la categoría.
    """
    resultados = []

    # Cargar los modelos una vez para optimizar el rendimiento
    classifier_primary = cargar_modelo(model_path_primary)
    classifier_secondary_masas = cargar_modelo(model_path_secondary_masas)
    classifier_secondary_calcifi = cargar_modelo(model_path_secondary_calcifi)

    if not classifier_primary:
        st.error("No se pudo cargar el modelo primario. Asegúrate de que la ruta sea correcta.")
        return

    # Definir los mapeos de predicción
    prediction_mapping_primary = {
        '0': 'calcificaciones',
        '1': 'masas',
        '2': 'no_encontrado'
    }

    prediction_mapping_secondary_masas = {
        '0': 'benigno',
        '1': 'maligno',
        '2': 'sospechoso'
    }

    prediction_mapping_secondary_calcifi = {
        '0': 'benigno',
        '1': 'maligno',
        '2': 'sospechoso'
    }

    # Procesar cada imagen
    for uploaded_image in uploaded_images:
        st.write(f"### Procesando imagen: {uploaded_image.name}")
        image_display, image_classification, tipo_archivo = procesar_archivo(uploaded_image)

        if image_classification:
            # Realizar la clasificación primaria
            mapped_result_primary = clasificar_imagen(image_classification, classifier_primary, prediction_mapping_primary)
            if not mapped_result_primary:
                st.error(f"No se pudo clasificar la imagen primariamente: {uploaded_image.name}")
                continue

            etiqueta_primaria = mapped_result_primary['label']

            # Inicializar la clasificación secundaria
            etiqueta_secundaria = None

            # Realizar la clasificación secundaria según la clasificación primaria
            if etiqueta_primaria == 'masas' and classifier_secondary_masas:
                mapped_result_secondary = clasificar_imagen(image_classification, classifier_secondary_masas, prediction_mapping_secondary_masas)
                if mapped_result_secondary:
                    etiqueta_secundaria = mapped_result_secondary['label']
                else:
                    st.error(f"No se pudo clasificar secundariamente (masas): {uploaded_image.name}")
            elif etiqueta_primaria == 'calcificaciones' and classifier_secondary_calcifi:
                mapped_result_secondary_calcifi = clasificar_imagen(image_classification, classifier_secondary_calcifi, prediction_mapping_secondary_calcifi)
                if mapped_result_secondary_calcifi:
                    etiqueta_secundaria = mapped_result_secondary_calcifi['label']
                else:
                    st.error(f"No se pudo clasificar secundariamente (calcificaciones): {uploaded_image.name}")

            # Agregar el resultado al listado
            resultados.append({
                'nombre_archivo': uploaded_image.name,
                'categoria_primaria': etiqueta_primaria,
                'categoria_secundaria': etiqueta_secundaria
            })
        else:
            st.error(f"No se pudo procesar la imagen: {uploaded_image.name}")

    if resultados:
        # Definir el orden de prioridad para las categorías secundarias
        prioridad = {
            'maligno': 1,
            'sospechoso': 2,
            'benigno': 3,
            'no_encontrado': 4
        }

        # Función para determinar la prioridad de una imagen
        def determinar_prioridad(resultado):
            categoria = resultado['categoria_secundaria']
            if categoria in prioridad:
                return prioridad[categoria]
            else:
                # Si no hay clasificación secundaria, asignar la prioridad más baja
                return prioridad['no_encontrado']

        # Separar las imágenes en dos listas: 'masas'/'calcificaciones' y 'no_encontrado'
        masas_calcificaciones = [res for res in resultados if res['categoria_primaria'] in ['masas', 'calcificaciones']]
        no_encontrados = [res for res in resultados if res['categoria_primaria'] == 'no_encontrado']

        # Ordenar las imágenes de 'masas' y 'calcificaciones' según la prioridad secundaria
        masas_calcificaciones_sorted = sorted(masas_calcificaciones, key=determinar_prioridad)

        # Ordenar las imágenes 'no_encontrado' (pueden no requerir orden específico)
        no_encontrados_sorted = sorted(no_encontrados, key=lambda x: x['nombre_archivo'])

        # Combinar las listas ordenadas
        resultados_ordenados = masas_calcificaciones_sorted + no_encontrados_sorted

        # Mostrar los resultados ordenados
        st.markdown("---")  # Separador
        st.subheader("Resultados de la Clasificación Masiva")

        for res in resultados_ordenados:
            st.write(f"**Imagen:** {res['nombre_archivo']}")
            st.write(f"- **Categoría Primaria:** {res['categoria_primaria'].capitalize()}")
            if res['categoria_secundaria']:
                st.write(f"- **Categoría Secundaria:** {res['categoria_secundaria'].capitalize()}")
            else:
                st.write("- **Categoría Secundaria:** No aplicable")
            st.write("")  # Línea en blanco

        # Mostrar un resumen
        total = len(resultados_ordenados)
        masas = len([res for res in resultados_ordenados if res['categoria_primaria'] == 'masas'])
        calcificaciones = len([res for res in resultados_ordenados if res['categoria_primaria'] == 'calcificaciones'])
        no_encontrados = len([res for res in resultados_ordenados if res['categoria_primaria'] == 'no_encontrado'])

        malignas = len([res for res in resultados_ordenados if res['categoria_secundaria'] == 'maligno'])
        sospechosas = len([res for res in resultados_ordenados if res['categoria_secundaria'] == 'sospechoso'])
        benignas = len([res for res in resultados_ordenados if res['categoria_secundaria'] == 'benigno'])

        porcentaje_mas_cal = masas + calcificaciones
        porcentaje_maligno = (malignas / porcentaje_mas_cal) * 100 if porcentaje_mas_cal > 0 else 0
        porcentaje_sospechoso = (sospechosas / porcentaje_mas_cal) * 100 if porcentaje_mas_cal > 0 else 0
        porcentaje_benigno = (benignas / porcentaje_mas_cal) * 100 if porcentaje_mas_cal > 0 else 0

        st.markdown("---")
        st.write(f"**Total de imágenes procesadas:** {total}")
        st.write(f"**Masas:** {masas}")
        st.write(f"**Calcificaciones:** {calcificaciones}")
        st.write(f"**No Encontradas:** {no_encontrados}")
        st.write(f"**Malignas:** {malignas} ({porcentaje_maligno:.2f}%)")
        st.write(f"**Sospechosas:** {sospechosas} ({porcentaje_sospechoso:.2f}%)")
        st.write(f"**Benignas:** {benignas} ({porcentaje_benigno:.2f}%)")

        # Generar el reporte PDF
        pdf_buffer = generar_reporte_pdf(resultados_ordenados, masas, calcificaciones, no_encontrados, malignas, sospechosas, benignas, porcentaje_maligno, porcentaje_sospechoso, porcentaje_benigno, total)

        # Descargar el PDF
        st.download_button(
            label="Descargar Reporte PDF",
            data=pdf_buffer,
            file_name="reporte_clasificacion_masiva.pdf",
            mime="application/pdf"
        )
    else:
        st.write("No se obtuvieron resultados de clasificación para las imágenes cargadas.")

def generar_reporte_pdf(resultados_ordenados, masas, calcificaciones, no_encontrados, malignas, sospechosas, benignas, porcentaje_maligno, porcentaje_sospechoso, porcentaje_benigno, total):
    """
    Genera un reporte PDF con los resultados de la clasificación masiva.
    Ordena las imágenes por prioridad: maligno, sospechoso, benigno, no encontrado.
    Incluye conteo, porcentajes y recomendaciones médicas basadas en los resultados.
    """
    pdf = FPDF()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)

    # Título
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(0, 10, "Reporte de Clasificación Masiva", ln=True, align='C')
    pdf.ln(10)

    # Tabla de resultados
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(60, 10, "Nombre de Imagen", 1, 0, 'C')
    pdf.cell(60, 10, "Categoría Primaria", 1, 0, 'C')
    pdf.cell(60, 10, "Categoría Secundaria", 1, 1, 'C')

    pdf.set_font("Arial", '', 12)
    for res in resultados_ordenados:
        pdf.cell(60, 10, res['nombre_archivo'], 1, 0, 'C')
        pdf.cell(60, 10, res['categoria_primaria'].capitalize(), 1, 0, 'C')
        sec_label = res['categoria_secundaria'].capitalize() if res['categoria_secundaria'] else 'No aplicable'
        pdf.cell(60, 10, sec_label, 1, 1, 'C')

    pdf.ln(10)

    # Resumen
    pdf.set_font("Arial", 'B', 14)
    pdf.cell(0, 10, "Resumen", ln=True)
    pdf.set_font("Arial", '', 12)

    pdf.cell(0, 10, f"**Total de imágenes procesadas:** {total}", ln=True)
    pdf.cell(0, 10, f"**Masas:** {masas}", ln=True)
    pdf.cell(0, 10, f"**Calcificaciones:** {calcificaciones}", ln=True)
    pdf.cell(0, 10, f"**No Encontradas:** {no_encontrados}", ln=True)
    pdf.cell(0, 10, f"**Malignas:** {malignas} ({porcentaje_maligno:.2f}%)", ln=True)
    pdf.cell(0, 10, f"**Sospechosas:** {sospechosas} ({porcentaje_sospechoso:.2f}%)", ln=True)
    pdf.cell(0, 10, f"**Benignas:** {benignas} ({porcentaje_benigno:.2f}%)", ln=True)

    pdf.ln(10)

    # Conclusiones
    pdf.set_font("Arial", 'B', 14)
    pdf.cell(0, 10, "Conclusiones", ln=True)
    pdf.set_font("Arial", '', 12)

    # Recomendaciones médicas basadas en los resultados
    recomendaciones = ""

    if porcentaje_maligno > 30:  # Umbral para determinar "mucho maligno"
        recomendaciones += (
            "Se han identificado una alta proporción de hallazgos malignos en las imágenes analizadas. "
            "Es imperativo que estos pacientes sean derivados para una evaluación médica inmediata y se considere "
            "la realización de biopsias para confirmar el diagnóstico y determinar el tratamiento adecuado.\n\n"
        )
    elif porcentaje_maligno > 0:
        recomendaciones += (
            "Se han identificado hallazgos malignos que requieren atención médica especializada. "
            "Se recomienda realizar evaluaciones adicionales y considerar tratamientos oportunos según el caso.\n\n"
        )

    if masas > 0 or calcificaciones > 0:
        recomendaciones += (
            "Los hallazgos identificados (masas y calcificaciones) deben ser evaluados por un especialista para determinar "
            "la necesidad de intervenciones adicionales. El seguimiento regular es esencial para monitorear cualquier cambio "
            "en los hallazgos observados.\n\n"
        )

    if not recomendaciones:
        recomendaciones = (
            "No se identificaron hallazgos significativos en las imágenes analizadas. Se recomienda continuar con "
            "controles regulares según las indicaciones médicas para mantener una vigilancia adecuada de la salud mamaria."
        )

    pdf.multi_cell(0, 10, recomendaciones)

    # Nota sobre la precisión del modelo
    pdf.ln(5)
    pdf.set_font("Arial", 'I', 12)
    pdf.multi_cell(0, 10, "Nota: Este modelo tiene una precisión del 70% aproximadamente. Aunque es una herramienta útil para la clasificación inicial, puede cometer errores. Se recomienda que los resultados sean revisados y confirmados por un profesional de la salud.")

    # Guardar el PDF en un buffer
    pdf_content = pdf.output(dest='S').encode('latin1')
    return pdf_content

# Funciones auxiliares implementadas en este archivo

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
