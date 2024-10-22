# src/ui/visualizacion.py

import streamlit as st
from src.ui.carga_imagenes import cargar_imagenes
from src.procesamiento.procesar import procesar_imagen_dicom_cached
from src.procesamiento.lectura_dicom import obtener_metadatos_relevantes
from concurrent.futures import ThreadPoolExecutor
import logging

logger = logging.getLogger(__name__)

def mostrar_visualizacion(opciones):
    """
    Maneja la visualización de imágenes DICOM con las opciones de procesamiento seleccionadas.
    """
    st.write("---")
    st.subheader("Visualización de Imágenes DICOM")

    tipo_carga = opciones.get('tipo_carga')

    if tipo_carga == "Procesamiento de Imágenes":
        subseccion = opciones.get('subseccion')

        if subseccion == "Visualización de DICOM":
            dicom_files = cargar_imagenes(opciones)

            if not dicom_files:
                st.info("No hay imágenes para mostrar en esta sección.")
                return

            num_imagenes = len(dicom_files)
            logger.info(f"Cantidad de imágenes cargadas en 'Procesamiento de DICOM': {num_imagenes}")

            if num_imagenes == 1:
                # Mostrar una sola imagen en alta resolución
                dicom_file = dicom_files[0]
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
                        for dicom_file in dicom_files
                    ]

                    # Barra de progreso
                    progress_bar = st.progress(0)
                    total = len(futures)

                    for idx, future in enumerate(futures):
                        try:
                            imagen, ds = future.result()
                            logger.info(f"Imagen procesada: {dicom_files[idx].name}")
                        except Exception as e:
                            st.error(f"Error al procesar la imagen {dicom_files[idx].name}: {e}")
                            logger.error(f"Error al procesar la imagen {dicom_files[idx].name}: {e}")
                            continue

                        dicom_file = dicom_files[idx]
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
    elif tipo_carga == "Clasificación mediante Deep Learning":
        # Actualmente, no se muestra nada aquí.
        st.info("Funcionalidad de Clasificación mediante Deep Learning en desarrollo.")
