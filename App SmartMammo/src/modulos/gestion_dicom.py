# src/modulos/gestion_dicom.py

import streamlit as st
import os
import numpy as np
import pydicom
import logging
from PIL import Image
from io import BytesIO
import zipfile

from src.modulos.procesamiento_i import procesamiento_individual
from src.modulos.procesamiento_m import procesamiento_masivo
from src.modulos.visor_dicom import visualizar_dicom

logger = logging.getLogger(__name__)

def gestionar_dicom(opciones):
    if opciones.get('subseccion') == "Visor DICOM":
        visualizar_dicom(opciones)
    elif opciones.get('subseccion') == "Exportar Imágenes a PNG/JPG":
        exportar_imagenes_png_jpg(opciones)

def exportar_imagenes_png_jpg(opciones):
    st.header("Exportar Imágenes a PNG/JPG")
    st.info("Convierte imágenes DICOM a formato PNG o JPG aplicando transformaciones opcionales.")

    # Subir múltiples archivos DICOM
    uploaded_files = st.file_uploader(
        "Cargar archivos DICOM",
        type=["dcm", "dicom"],
        accept_multiple_files=True
    )

    if not uploaded_files:
        st.info("Por favor, carga uno o más archivos DICOM para convertir.")
        return

    # Seleccionar el tamaño de salida
    size_options = {
        "224x224": (224, 224),
        "256x256": (256, 256),
        "512x512": (512, 512),
        "1024x1024": (1024, 1024)
    }
    selected_size_label = st.selectbox("Selecciona el tamaño de salida", list(size_options.keys()))
    selected_size = size_options[selected_size_label]

    # Seleccionar el formato de salida
    format_options = ["PNG", "JPG"]
    selected_format = st.selectbox("Selecciona el formato de salida", format_options)

    # **Eliminar las opciones adicionales**
    # Opciones comentadas para no aparecer en la interfaz
    # aplicar_transformaciones = st.checkbox("Aplicar Transformaciones", value=False)
    # opciones_transformaciones = {}
    # if aplicar_transformaciones:
    #     st.write("### Selecciona las Transformaciones a Aplicar")

    #     # Crear una lista de transformaciones
    #     transformaciones = [
    #         ('voltear_horizontal', "Volteo Horizontal"),
    #         ('voltear_vertical', "Volteo Vertical"),
    #         ('brillo_contraste', "Ajuste de Brillo y Contraste"),
    #         ('ruido_gaussiano', "Añadir Ruido Gaussiano"),
    #         ('recorte_redimension', "Recorte Aleatorio y Redimensionado"),
    #         ('desenfoque', "Aplicar Desenfoque")
    #     ]

    #     # Diccionario para almacenar las selecciones
    #     for key, label in transformaciones:
    #         opciones_transformaciones[key] = st.checkbox(label=label, value=False, key=key)

    # Botón para iniciar la conversión
    if st.button("Iniciar Conversión"):
        with st.spinner("Procesando las imágenes..."):
            total_files = len(uploaded_files)
            if total_files == 0:
                st.warning("No se encontraron archivos DICOM para procesar.")
                return

            progress_bar = st.progress(0)
            status_text = st.empty()

            # Crear un archivo ZIP en memoria
            zip_buffer = BytesIO()
            with zipfile.ZipFile(zip_buffer, "a", zipfile.ZIP_DEFLATED) as zip_file:
                for idx, dicom_file in enumerate(uploaded_files):
                    dicom_bytes = dicom_file.getvalue()
                    image = convertir_dicom_bytes_a_imagen(
                        dicom_bytes,
                        selected_size,
                        # aplicar_transformaciones,
                        # opciones_transformaciones
                        aplicar_transformaciones=False,
                        opciones_transformaciones={}
                    )
                    if image is not None:
                        output_filename = f"{os.path.splitext(dicom_file.name)[0]}.{selected_format.lower()}"
                        img_bytes = BytesIO()
                        image.save(img_bytes, format=selected_format)
                        img_bytes.seek(0)
                        zip_file.writestr(output_filename, img_bytes.read())
                    else:
                        st.error(f"No se pudo procesar el archivo: {dicom_file.name}")

                    # Actualizar barra de progreso
                    progress = (idx + 1) / total_files
                    progress_bar.progress(progress)
                    status_text.text(f"Procesando {idx + 1} de {total_files} imágenes...")

            st.success("Conversión completada.")

            # Preparar el ZIP para descarga
            zip_buffer.seek(0)
            st.download_button(
                label="Descargar Imágenes Convertidas",
                data=zip_buffer,
                file_name="imagenes_convertidas.zip",
                mime="application/zip"
            )

# Funciones auxiliares

def procesar_imagen_dicom_cached(dicom_file_bytes, opciones):
    """
    Procesa una imagen DICOM según las opciones seleccionadas y devuelve la imagen y el dataset.
    """
    try:
        # Leer el dataset DICOM
        ds = leer_imagen_dicom(dicom_file_bytes)

        # Verificar si ds es None
        if ds is None:
            logger.warning("Dataset DICOM no pudo ser leído.")
            return None, None

        # Obtener los datos de píxeles
        data = ds.pixel_array

        # Aplicar VOI LUT si está seleccionado
        if opciones.get("aplicar_voilut", True):
            data = apply_voi_lut(data, ds)

        # Si la interpretación es MONOCHROME1, invertimos la imagen y cambiamos a MONOCHROME2
        if ds.PhotometricInterpretation == 'MONOCHROME1':
            data = np.max(data) - data
            ds.PhotometricInterpretation = 'MONOCHROME2'

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

        # Convertir a imagen PIL
        image = Image.fromarray(image).convert('L')

        return image, ds

    except Exception as e:
        logger.error(f"Error al procesar el archivo DICOM: {e}")
        return None, None

def leer_imagen_dicom(dicom_file_bytes):
    """
    Lee un archivo DICOM y devuelve el dataset.
    """
    try:
        ds = pydicom.dcmread(BytesIO(dicom_file_bytes))
        return ds
    except Exception as e:
        logger.error(f"Error al leer el archivo DICOM: {e}")
        return None

def convertir_dicom_bytes_a_imagen(dicom_bytes, output_size=(224, 224), aplicar_transformaciones=False, opciones_transformaciones=None):
    """
    Convierte bytes de un archivo DICOM a una imagen PIL Image con el tamaño especificado.
    """
    try:
        # Leer el dataset DICOM
        dicom = pydicom.dcmread(BytesIO(dicom_bytes))
        original_image = dicom.pixel_array

        # Aplicar VOI LUT
        img_windowed = apply_voi_lut(original_image, dicom)

        # Manejar Photometric Interpretation
        photometric_interpretation = dicom.get('PhotometricInterpretation', 'UNKNOWN')
        if photometric_interpretation == 'MONOCHROME1':
            img_windowed = img_windowed.max() - img_windowed

        # Normalizar la imagen
        img_normalized = (img_windowed - img_windowed.min()) / (img_windowed.max() - img_windowed.min())

        # Aplicar transformaciones si está seleccionado
        if aplicar_transformaciones and opciones_transformaciones:
            img_normalized = aplicar_transformaciones_a_imagen(img_normalized, opciones_transformaciones)

        # Escalar a 0-255 y convertir a uint8
        img_normalized = (img_normalized * 255).astype(np.uint8)

        # Redimensionar la imagen
        img_resized = Image.fromarray(img_normalized).resize(output_size)

        return img_resized

    except Exception as e:
        logger.error(f"Error al procesar el archivo DICOM: {e}")
        return None

def construir_pipeline_transformaciones(opciones):
    """
    Construye el pipeline de transformaciones basado en las opciones seleccionadas.
    """
    import albumentations as A

    transformaciones = []

    if opciones.get('voltear_horizontal', False):
        transformaciones.append(A.HorizontalFlip(p=1.0))

    if opciones.get('voltear_vertical', False):
        transformaciones.append(A.VerticalFlip(p=1.0))

    if opciones.get('brillo_contraste', False):
        transformaciones.append(A.RandomBrightnessContrast(p=1.0))

    if opciones.get('ruido_gaussiano', False):
        transformaciones.append(A.GaussNoise(var_limit=(20.0, 80.0), p=1.0))

    if opciones.get('recorte_redimension', False):
        transformaciones.append(A.RandomResizedCrop(
            height=224, width=224, scale=(0.8, 1.0), ratio=(0.9, 1.1), p=1.0))

    if opciones.get('desenfoque', False):
        transformaciones.append(A.Blur(blur_limit=7, p=1.0))

    # Si no se seleccionó ninguna transformación, aplicar una transformación que no hace nada
    if not transformaciones:
        transformaciones.append(A.NoOp())

    pipeline = A.Compose(transformaciones)

    return pipeline

def aplicar_transformaciones(data, opciones):
    """
    Aplica transformaciones a la imagen utilizando Albumentations.
    """
    import albumentations as A

    # Construir el pipeline de transformaciones basado en las opciones
    augmentation_pipeline = construir_pipeline_transformaciones(opciones)

    # Convertir data a uint8 y expandir dimensiones si es necesario
    image = (data * 255).astype(np.uint8)

    # Si la imagen es en escala de grises, agregar una dimensión de canal
    if len(image.shape) == 2:
        image = np.expand_dims(image, axis=2)

    # Aplicar el pipeline de augmentación
    augmented = augmentation_pipeline(image=image)
    image_augmented = augmented['image']

    # Si la imagen sigue teniendo un solo canal, volver a reducir la dimensión
    if image_augmented.shape[2] == 1:
        image_augmented = np.squeeze(image_augmented, axis=2)

    # Convertir de vuelta a float para consistencia
    image_augmented = image_augmented.astype(np.float32) / 255.0

    return image_augmented

def aplicar_transformaciones_a_imagen(data, opciones):
    """
    Aplica transformaciones a la imagen utilizando Albumentations.
    """
    return aplicar_transformaciones(data, opciones)
