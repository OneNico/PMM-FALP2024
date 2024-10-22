# src/ui/convertir_png.py

import streamlit as st
import os
import shutil
from src.procesamiento.convertir_png import convertir_dicom_a_imagen
from concurrent.futures import ThreadPoolExecutor
import cv2


def mostrar_convertir_png(opciones):
    """
    Muestra la sección 'Convertir a PNG' y maneja la conversión de DICOM a PNG o JPG.
    """
    st.header("Convertir DICOM a PNG o JPG")
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
                        if selected_format == "PNG":
                            cv2.imwrite(output_path, image)
                        elif selected_format == "JPG":
                            cv2.imwrite(output_path, image, [int(cv2.IMWRITE_JPEG_QUALITY), 95])
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
    st.write(f"- **Origen:** `data/raw/{selected_subfolder}`")
    st.write(f"- **Destino:** `data/processed/{selected_subfolder}`")

