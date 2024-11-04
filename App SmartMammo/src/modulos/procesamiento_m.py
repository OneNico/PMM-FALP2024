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

        # Nombres de los modelos en Hugging Face
        model_name_primary = "nc7777/clasificador_primario"
        model_name_secondary_masas = "nc7777/clasificador_masas"
        model_name_secondary_calcifi = "nc7777/clasificador_calcificaciones"

        # Llamar a la función de procesamiento masivo
        procesar_imagenes_masivas(uploaded_images, model_name_primary, model_name_secondary_masas,
                                  model_name_secondary_calcifi)
    else:
        st.info("Por favor, carga una o más imágenes DICOM, PNG o JPG para realizar la clasificación.")


def procesar_imagenes_masivas(uploaded_images, model_name_primary, model_name_secondary_masas,
                              model_name_secondary_calcifi):
    """
    Procesa múltiples imágenes para clasificación masiva.
    Clasifica cada imagen en la clasificación primaria y secundaria,
    luego ordena y muestra los nombres de las imágenes según la categoría.
    Además, compara las predicciones del modelo primario con las etiquetas verdaderas
    basadas en el prefijo del nombre del archivo y calcula estadísticas de precisión.
    """
    resultados = []
    correct_primary = 0
    incorrect_primary = 0
    correct_secondary_masas = 0
    incorrect_secondary_masas = 0
    correct_secondary_calcificaciones = 0
    incorrect_secondary_calcificaciones = 0

    # Variables para contar subcategorías por categoría primaria
    benignas_masas = 0
    malignas_masas = 0
    sospechosas_masas = 0

    benignas_calcificaciones = 0
    malignas_calcificaciones = 0
    sospechosas_calcificaciones = 0

    errores = 0  # Contador de errores en el procesamiento

    # Cargar los modelos una vez para optimizar el rendimiento
    classifier_primary = cargar_modelo(model_name_primary)
    classifier_secondary_masas = cargar_modelo(model_name_secondary_masas)
    classifier_secondary_calcifi = cargar_modelo(model_name_secondary_calcifi)

    if not classifier_primary:
        st.error("No se pudo cargar el modelo primario. Asegúrate de que la ruta sea correcta.")
        return

    # Definir los mapeos de predicción
    prediction_mapping_primary = {
        '0': 'calcificaciones',
        '1': 'masas',
        '2': 'no_encontrado'
    }

    prediction_mapping_secondary = {
        '0': 'benigno',
        '1': 'maligno',
        '2': 'sospechoso'
    }

    # Inicializar la barra de progreso
    progress_bar = st.progress(0)
    status_text = st.empty()
    status_text.text("Clasificando las imágenes con IA...")

    # Crear una fila de columnas para centrar el GIF
    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        gif_placeholder = st.empty()  # Crear un espacio reservado para el GIF
        gif_url = "https://media.giphy.com/media/fksTuJKgDCrdnkG497/giphy.gif"  # URL del GIF
        gif_placeholder.image(gif_url, width=300)  # Mostrar el GIF con ancho de 300px (ajustable)

    total_images = len(uploaded_images)

    # Procesar cada imagen
    for idx, uploaded_image in enumerate(uploaded_images):
        # Procesar la imagen
        image_display, image_classification, tipo_archivo = procesar_archivo(uploaded_image)

        if image_classification:
            # Realizar la clasificación primaria
            mapped_result_primary = clasificar_imagen(image_classification, classifier_primary,
                                                      prediction_mapping_primary)
            if not mapped_result_primary:
                # Agregar el resultado con clasificación primaria fallida
                resultados.append({
                    'nombre_archivo': uploaded_image.name,
                    'categoria_primaria': 'error',
                    'categoria_secundaria': None,
                    'primary_correct': False
                })
                errores += 1
                continue  # Salta a la siguiente imagen si falla la clasificación primaria

            etiqueta_primaria = mapped_result_primary['label']

            # Determinar la etiqueta verdadera basada en el prefijo del nombre del archivo
            ground_truth_primary = determinar_ground_truth(uploaded_image.name)

            # Comparar la predicción con la etiqueta verdadera
            if etiqueta_primaria == ground_truth_primary:
                primary_correct = True
                correct_primary += 1
            else:
                primary_correct = False
                incorrect_primary += 1

            # Inicializar la clasificación secundaria
            etiqueta_secundaria = None

            # Determinar la etiqueta verdadera secundaria
            ground_truth_secondary = determinar_ground_truth_secondary(uploaded_image.name, etiqueta_primaria)

            # Realizar la clasificación secundaria según la clasificación primaria
            if primary_correct and ground_truth_secondary:
                if etiqueta_primaria == 'masas' and classifier_secondary_masas:
                    mapped_result_secondary = clasificar_imagen(image_classification, classifier_secondary_masas,
                                                                prediction_mapping_secondary)
                    if mapped_result_secondary:
                        etiqueta_secundaria = mapped_result_secondary['label']
                        # Incrementar las subcategorías según la categoría primaria
                        if etiqueta_secundaria == 'benigno':
                            benignas_masas += 1
                        elif etiqueta_secundaria == 'maligno':
                            malignas_masas += 1
                        elif etiqueta_secundaria == 'sospechoso':
                            sospechosas_masas += 1
                        # Comparar con la etiqueta verdadera secundaria
                        if etiqueta_secundaria == ground_truth_secondary:
                            correct_secondary_masas += 1
                        else:
                            incorrect_secondary_masas += 1

                elif etiqueta_primaria == 'calcificaciones' and classifier_secondary_calcifi:
                    mapped_result_secondary_calcifi = clasificar_imagen(image_classification,
                                                                        classifier_secondary_calcifi,
                                                                        prediction_mapping_secondary)
                    if mapped_result_secondary_calcifi:
                        etiqueta_secundaria = mapped_result_secondary_calcifi['label']
                        # Incrementar las subcategorías según la categoría primaria
                        if etiqueta_secundaria == 'benigno':
                            benignas_calcificaciones += 1
                        elif etiqueta_secundaria == 'maligno':
                            malignas_calcificaciones += 1
                        elif etiqueta_secundaria == 'sospechoso':
                            sospechosas_calcificaciones += 1
                        # Comparar con la etiqueta verdadera secundaria
                        if etiqueta_secundaria == ground_truth_secondary:
                            correct_secondary_calcificaciones += 1
                        else:
                            incorrect_secondary_calcificaciones += 1

            # Agregar el resultado al listado
            resultados.append({
                'nombre_archivo': uploaded_image.name,
                'categoria_primaria': etiqueta_primaria,
                'categoria_secundaria': etiqueta_secundaria,
                'primary_correct': primary_correct
            })
        else:
            # Agregar el resultado con error en el procesamiento
            resultados.append({
                'nombre_archivo': uploaded_image.name,
                'categoria_primaria': 'error',
                'categoria_secundaria': None,
                'primary_correct': False
            })
            errores += 1

        # Actualizar la barra de progreso
        progress = (idx + 1) / total_images
        progress_bar.progress(progress)

    # Actualizar el estado al finalizar
    status_text.text("Clasificación completada.")

    # Eliminar el GIF una vez completada la clasificación
    gif_placeholder.empty()

    if resultados:
        # Definir el orden de prioridad para las categorías secundarias
        prioridad = {
            'maligno': 1,
            'sospechoso': 2,
            'benigno': 3,
            'no_encontrado': 4,
            'error': 5
        }

        # Función para determinar la prioridad de una imagen
        def determinar_prioridad(resultado):
            categoria = resultado['categoria_secundaria'] if resultado['categoria_secundaria'] else resultado[
                'categoria_primaria']
            if categoria in prioridad:
                return prioridad[categoria]
            else:
                # Si no hay clasificación secundaria, asignar la prioridad más baja
                return prioridad['no_encontrado']

        # Ordenar las imágenes según la prioridad
        resultados_ordenados = sorted(resultados, key=determinar_prioridad)

        # Calcular estadísticas
        total = len(resultados_ordenados)
        masas_total = len([res for res in resultados_ordenados if res['categoria_primaria'] == 'masas'])
        calcificaciones_total = len(
            [res for res in resultados_ordenados if res['categoria_primaria'] == 'calcificaciones'])
        no_encontrados = len([res for res in resultados_ordenados if res['categoria_primaria'] == 'no_encontrado'])
        errores_total = errores  # Ya contamos los errores en la variable 'errores'

        # Calcular porcentajes para categorías primarias en base al total de imágenes
        porcentaje_masas = (masas_total / total) * 100 if total > 0 else 0
        porcentaje_calcificaciones = (calcificaciones_total / total) * 100 if total > 0 else 0
        porcentaje_no_encontradas = (no_encontrados / total) * 100 if total > 0 else 0

        # Calcular porcentajes por subcategoría dentro de cada categoría primaria
        # (Ya no se necesitan para la interfaz, pero se usan en el PDF)
        porcentaje_benigno_calcificaciones = (benignas_calcificaciones / total) * 100 if total > 0 else 0
        porcentaje_maligno_calcificaciones = (malignas_calcificaciones / total) * 100 if total > 0 else 0
        porcentaje_sospechoso_calcificaciones = (sospechosas_calcificaciones / total) * 100 if total > 0 else 0

        porcentaje_benigno_masas = (benignas_masas / total) * 100 if total > 0 else 0
        porcentaje_maligno_masas = (malignas_masas / total) * 100 if total > 0 else 0
        porcentaje_sospechoso_masas = (sospechosas_masas / total) * 100 if total > 0 else 0

        # Mostrar el resumen de resultados en tarjetas
        st.markdown("---")  # Separador
        st.subheader("Resultados de Clasificación")

        # Crear columnas para las tarjetas
        col1, col2, col3 = st.columns(3)

        with col1:
            st.markdown(
                f"""
                <div style="background-color: #d4edda; padding: 15px; border-radius: 10px;">
                    <h4 style="color: #155724;">Calcificaciones: {porcentaje_calcificaciones:.0f}% del total</h4>
                    <div style="margin-bottom: 10px;">
                        <strong>Benigno:</strong> {benignas_calcificaciones} mamografías
                    </div>
                    <div style="margin-bottom: 10px;">
                        <strong>Maligno:</strong> {malignas_calcificaciones} mamografías
                    </div>
                    <div style="margin-bottom: 10px;">
                        <strong>Sospechoso:</strong> {sospechosas_calcificaciones} mamografías
                    </div>
                </div>
                """,
                unsafe_allow_html=True
            )

        with col2:
            st.markdown(
                f"""
                <div style="background-color: #f8d7da; padding: 15px; border-radius: 10px;">
                    <h4 style="color: #721c24;">Masas: {porcentaje_masas:.0f}% del total</h4>
                    <div style="margin-bottom: 10px;">
                        <strong>Benigno:</strong> {benignas_masas} mamografías
                    </div>
                    <div style="margin-bottom: 10px;">
                        <strong>Maligno:</strong> {malignas_masas} mamografías
                    </div>
                    <div style="margin-bottom: 10px;">
                        <strong>Sospechoso:</strong> {sospechosas_masas} mamografías
                    </div>
                </div>
                """,
                unsafe_allow_html=True
            )

        with col3:
            st.markdown(
                f"""
                <div style="background-color: #fff3cd; padding: 15px; border-radius: 10px;">
                    <h4 style="color: #856404;">No Encontradas: {porcentaje_no_encontradas:.0f}% del total</h4>
                    <div style="margin-bottom: 10px;">
                        <strong>Total:</strong> {no_encontrados} mamografías
                    </div>
                    <div style="margin-bottom: 10px;">
                        <strong>Errores en el procesamiento:</strong> {errores_total} mamografías
                    </div>
                </div>
                """,
                unsafe_allow_html=True
            )

        # Generar el reporte PDF con los detalles actualizados
        pdf_buffer = generar_reporte_pdf(
            resultados_ordenados,
            masas_total,
            calcificaciones_total,
            no_encontrados,
            benignas_masas,
            malignas_masas,
            sospechosas_masas,
            benignas_calcificaciones,
            malignas_calcificaciones,
            sospechosas_calcificaciones,
            errores_total,
            total,
            porcentaje_masas,
            porcentaje_calcificaciones,
            porcentaje_no_encontradas
        )

        # Descargar el PDF
        st.download_button(
            label="Descargar Reporte PDF",
            data=pdf_buffer,
            file_name="reporte_clasificacion_masiva.pdf",
            mime="application/pdf"
        )
    else:
        st.write("No se obtuvieron resultados de clasificación para las imágenes cargadas.")


def generar_reporte_pdf(resultados_ordenados, masas_total, calcificaciones_total, no_encontrados,
                        benignas_masas, malignas_masas, sospechosas_masas,
                        benignas_calcificaciones, malignas_calcificaciones, sospechosas_calcificaciones,
                        errores_total, total, porcentaje_masas, porcentaje_calcificaciones, porcentaje_no_encontradas):
    """
    Genera un reporte PDF con los resultados de la clasificación masiva.
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
        nombre = res['nombre_archivo']
        categoria_primaria = res['categoria_primaria'].capitalize()
        categoria_secundaria = res['categoria_secundaria'].capitalize() if res[
            'categoria_secundaria'] else 'No aplicable'
        pdf.cell(60, 10, nombre, 1, 0, 'C')
        pdf.cell(60, 10, categoria_primaria, 1, 0, 'C')
        pdf.cell(60, 10, categoria_secundaria, 1, 1, 'C')

    pdf.ln(10)

    # Resumen
    pdf.set_font("Arial", 'B', 14)
    pdf.cell(0, 10, "Resumen", ln=True)
    pdf.set_font("Arial", '', 12)

    pdf.cell(0, 10, f"Total de imágenes procesadas: {total}", ln=True)
    pdf.cell(0, 10, f"Masas: {masas_total} ({porcentaje_masas:.0f}%)", ln=True)
    pdf.cell(0, 10, f"Calcificaciones: {calcificaciones_total} ({porcentaje_calcificaciones:.0f}%)", ln=True)
    pdf.cell(0, 10, f"No Encontradas: {no_encontrados} ({porcentaje_no_encontradas:.0f}%)", ln=True)
    pdf.cell(0, 10, f"Errores en el procesamiento: {errores_total} mamografías", ln=True)

    pdf.ln(10)

    # Detalle por categoría primaria
    pdf.set_font("Arial", 'B', 14)
    pdf.cell(0, 10, "Detalle por Categoría Primaria", ln=True)

    # Calcificaciones
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(0, 10, "Calcificaciones", ln=True)
    pdf.set_font("Arial", '', 12)
    pdf.cell(0, 10, f"Benigno: {benignas_calcificaciones} mamografías", ln=True)
    pdf.cell(0, 10, f"Maligno: {malignas_calcificaciones} mamografías", ln=True)
    pdf.cell(0, 10, f"Sospechoso: {sospechosas_calcificaciones} mamografías", ln=True)
    pdf.ln(5)

    # Masas
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(0, 10, "Masas", ln=True)
    pdf.set_font("Arial", '', 12)
    pdf.cell(0, 10, f"Benigno: {benignas_masas} mamografías", ln=True)
    pdf.cell(0, 10, f"Maligno: {malignas_masas} mamografías", ln=True)
    pdf.cell(0, 10, f"Sospechoso: {sospechosas_masas} mamografías", ln=True)

    pdf.ln(10)

    # Conclusiones
    pdf.add_page()
    pdf.set_font("Arial", 'B', 14)
    pdf.cell(0, 10, "Conclusiones", ln=True)
    pdf.set_font("Arial", '', 12)

    recomendaciones = ""

    # Evaluar la proporción de hallazgos malignos
    total_malignos = malignas_masas + malignas_calcificaciones
    total_sospechosos = sospechosas_masas + sospechosas_calcificaciones
    total_benignos = benignas_masas + benignas_calcificaciones

    porcentaje_maligno_total = (total_malignos / total) * 100 if total > 0 else 0

    if porcentaje_maligno_total > 30:
        recomendaciones += (
            "Se han identificado una alta proporción de hallazgos malignos en las imágenes analizadas. "
            "Es imperativo que estos pacientes sean derivados para una evaluación médica inmediata y se considere "
            "la realización de biopsias para confirmar el diagnóstico y determinar el tratamiento adecuado.\n\n"
        )
    elif porcentaje_maligno_total > 0:
        recomendaciones += (
            "Se han identificado hallazgos malignos que requieren atención médica especializada. "
            "Se recomienda realizar evaluaciones adicionales y considerar tratamientos oportunos según el caso.\n\n"
        )

    if masas_total > 0 or calcificaciones_total > 0:
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
    pdf.multi_cell(0, 10,
                   "Nota: Este modelo tiene una precisión del 70% aproximadamente. Aunque es una herramienta útil para la clasificación inicial, puede cometer errores. Se recomienda que los resultados sean revisados y confirmados por un profesional de la salud.")

    # Guardar el PDF en un buffer
    pdf_content = pdf.output(dest='S').encode('latin1')
    return pdf_content


# Funciones auxiliares implementadas en este archivo

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
        return None


def determinar_ground_truth(nombre_archivo):
    """
    Determina la etiqueta verdadera primaria basada en el prefijo del nombre del archivo.
    """
    nombre_archivo = nombre_archivo.lower()
    if nombre_archivo.startswith('mass_'):
        return 'masas'
    elif nombre_archivo.startswith('calc_'):
        return 'calcificaciones'
    elif nombre_archivo.startswith('no_'):
        return 'no_encontrado'
    else:
        return 'no_encontrado'


def determinar_ground_truth_secondary(nombre_archivo, categoria_primaria):
    """
    Determina la etiqueta verdadera secundaria basada en el nombre del archivo y la categoría primaria.
    """
    nombre_archivo = nombre_archivo.lower()
    partes = nombre_archivo.split('_')

    if categoria_primaria == 'masas' and len(partes) >= 2:
        return partes[1]
    elif categoria_primaria == 'calcificaciones' and len(partes) >= 2:
        return partes[1]
    else:
        return None  # No aplica o no está definido
