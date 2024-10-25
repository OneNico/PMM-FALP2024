# src/modulos/gestion_dicom.py

import streamlit as st
import os
import numpy as np
import pydicom
import logging
from PIL import Image
from concurrent.futures import ThreadPoolExecutor


logger = logging.getLogger(__name__)

def gestionar_dicom(opciones):
    if opciones.get('subseccion') == "Exploración de Imágenes DICOM":
        mostrar_exploracion_dicom(opciones)
    elif opciones.get('subseccion') == "Exportar Imágenes a PNG/JPG":
        exportar_imagenes_png_jpg(opciones)

def mostrar_exploracion_dicom(opciones):
    st.write("---")
    st.subheader("Exploración de Imágenes DICOM")

    uploaded_files = opciones.get('uploaded_files', [])
    if not uploaded_files:
        st.info("No has cargado ningún archivo DICOM.")
        return

    num_imagenes = len(uploaded_files)
    logger.info(f"Cantidad de imágenes cargadas: {num_imagenes}")

    if num_imagenes == 1:
        # Mostrar una sola imagen en alta resolución
        dicom_file = uploaded_files[0]
        with st.container():
            with st.spinner("Procesando la imagen..."):
                imagen, ds = procesar_imagen_dicom_cached(dicom_file.getvalue(), opciones)
            if imagen is not None:
                st.image(imagen, caption=dicom_file.name, use_column_width=True)
                if opciones.get('mostrar_metadatos', False) and ds is not None:
                    metadatos = obtener_metadatos_relevantes(ds)
                    st.expander("Metadatos").write(metadatos)
            else:
                st.error(f"No se pudo procesar la imagen {dicom_file.name}")
    else:
        # Mostrar múltiples imágenes en columnas con tamaño reducido
        num_columns = min(3, num_imagenes)  # Máximo 3 columnas
        cols = st.columns(num_columns)
        with ThreadPoolExecutor(max_workers=4) as executor:
            futures = [
                executor.submit(procesar_imagen_dicom_cached, dicom_file.getvalue(), opciones)
                for dicom_file in uploaded_files
            ]

            # Barra de progreso
            progress_bar = st.progress(0)
            total = len(futures)

            for idx, future in enumerate(futures):
                try:
                    imagen, ds = future.result()
                    logger.info(f"Imagen procesada: {uploaded_files[idx].name}")
                except Exception as e:
                    st.error(f"Error al procesar la imagen {uploaded_files[idx].name}: {e}")
                    logger.error(f"Error al procesar la imagen {uploaded_files[idx].name}: {e}")
                    continue

                dicom_file = uploaded_files[idx]
                if imagen is not None:
                    with cols[idx % num_columns]:
                        st.image(imagen, caption=dicom_file.name, use_column_width=True)
                        if opciones.get('mostrar_metadatos', False) and ds is not None:
                            metadatos = obtener_metadatos_relevantes(ds)
                            st.expander("Metadatos").write(metadatos)
                else:
                    st.error(f"No se pudo procesar la imagen {dicom_file.name}")

                # Actualizar barra de progreso
                progress_bar.progress((idx + 1) / total)

def exportar_imagenes_png_jpg(opciones):
    st.header("Exportar Imágenes a PNG/JPG")
    st.info("Convierte todas las imágenes DICOM de una carpeta a formato PNG o JPG.")

    # Seleccionar la carpeta de origen desde 'data/raw'
    raw_data_dir = os.path.join(os.getcwd(), 'data', 'raw')
    processed_data_dir = os.path.join(os.getcwd(), 'data', 'processed')

    # Verificar si las carpetas existen
    if not os.path.exists(raw_data_dir):
        st.error(f"La carpeta de datos crudos no existe: {raw_data_dir}")
        return

    if not os.path.exists(processed_data_dir):
        st.info(f"La carpeta de datos procesados no existe. Se creará automáticamente: {processed_data_dir}")
        os.makedirs(processed_data_dir, exist_ok=True)

    # Listar subcarpetas en 'data/raw'
    subfolders = [f.name for f in os.scandir(raw_data_dir) if f.is_dir()]
    if not subfolders:
        st.warning(f"No se encontraron subcarpetas en: {raw_data_dir}")
        return

    # Seleccionar una subcarpeta
    selected_subfolder = st.selectbox("Selecciona la carpeta a convertir", subfolders)
    source_dir = os.path.join(raw_data_dir, selected_subfolder)

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

    # Botón para iniciar la conversión
    if st.button("Iniciar Conversión"):
        with st.spinner("Procesando las imágenes..."):
            # Definir la carpeta de salida
            output_dir = os.path.join(processed_data_dir, selected_subfolder)
            os.makedirs(output_dir, exist_ok=True)

            # Listar todos los archivos DICOM en la carpeta de origen
            dicom_files = []
            for root, dirs, files in os.walk(source_dir):
                for file in files:
                    if file.lower().endswith(('.dcm', '.dicom')):
                        dicom_files.append(os.path.join(root, file))

            total_files = len(dicom_files)
            if total_files == 0:
                st.warning(f"No se encontraron archivos DICOM en la carpeta: {source_dir}")
                return

            progress_bar = st.progress(0)
            status_text = st.empty()

            # Función para procesar una sola imagen
            def process_image(dicom_path):
                image_name = os.path.splitext(os.path.basename(dicom_path))[0]
                image = convertir_dicom_a_imagen(dicom_path, selected_size)
                if image is not None:
                    output_filename = f"{image_name}.{selected_format.lower()}"
                    output_path = os.path.join(output_dir, output_filename)
                    try:
                        image.save(output_path)
                        return True
                    except Exception as e:
                        print(f"Error al guardar {output_path}: {e}")
                        return False
                else:
                    return False

            # Procesar imágenes en paralelo
            with ThreadPoolExecutor(max_workers=4) as executor:
                futures = []
                for idx, dicom_path in enumerate(dicom_files):
                    futures.append(executor.submit(process_image, dicom_path))

                for idx, future in enumerate(futures):
                    result = future.result()
                    progress = (idx + 1) / total_files
                    progress_bar.progress(progress)
                    status_text.text(f"Procesando {idx + 1} de {total_files} imágenes...")

            st.success(f"Conversión completada. Imágenes guardadas en: {output_dir}")

    # Información adicional
    st.write("---")
    st.write("### Estructura de Carpetas:")
    st.write(f"- **Origen:** data/raw/{selected_subfolder}")
    st.write(f"- **Destino:** data/processed/{selected_subfolder}")

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
        ds = pydicom.dcmread(pydicom.filebase.DicomBytesIO(dicom_file_bytes))
        return ds
    except Exception as e:
        logger.error(f"Error al leer el archivo DICOM: {e}")
        return None

def obtener_metadatos_relevantes(ds):
    """
    Extrae y devuelve los metadatos relevantes del dataset DICOM.
    """
    metadatos = {
        "Patient ID": getattr(ds, 'PatientID', 'Desconocido'),
        "Study Date": getattr(ds, 'StudyDate', 'Desconocido'),
        "Modality": getattr(ds, 'Modality', 'Desconocido'),
        "Photometric Interpretation": getattr(ds, 'PhotometricInterpretation', 'Desconocido'),
        "Rows": getattr(ds, 'Rows', 'Desconocido'),
        "Columns": getattr(ds, 'Columns', 'Desconocido'),
    }
    return metadatos

def convertir_dicom_a_imagen(dicom_path, output_size=(224, 224)):
    """
    Convierte un archivo DICOM a una imagen PIL Image con el tamaño especificado.
    """
    try:
        # Leer el dataset DICOM
        dicom = pydicom.dcmread(dicom_path)
        original_image = dicom.pixel_array

        # Aplicar VOI LUT
        img_windowed = pydicom.pixel_data_handlers.apply_voi_lut(original_image, dicom)

        # Manejar Photometric Interpretation
        photometric_interpretation = dicom.get('PhotometricInterpretation', 'UNKNOWN')
        if photometric_interpretation == 'MONOCHROME1':
            img_windowed = img_windowed.max() - img_windowed

        # Normalizar la imagen
        img_normalized = (img_windowed - img_windowed.min()) / (img_windowed.max() - img_windowed.min()) * 255
        img_normalized = img_normalized.astype(np.uint8)

        # Redimensionar la imagen
        img_resized = Image.fromarray(img_normalized).resize(output_size)

        return img_resized

    except Exception as e:
        logger.error(f"Error al procesar {dicom_path}: {e}")
        return None

# Implementación de la función 'aplicar_transformaciones' dentro de este archivo

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
