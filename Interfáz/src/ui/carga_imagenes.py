# src/ui/carga_imagenes.py

import streamlit as st
import io
import os

def cargar_imagenes(opciones, max_imagenes=100):
    """
    Carga archivos DICOM según el tipo de carga seleccionado por el usuario.
    Limita la cantidad de imágenes cargadas a 'max_imagenes'.
    """
    dicom_files = []

    tipo_carga = opciones.get('tipo_carga')

    if tipo_carga == "Procesamiento de Imágenes":
        uploaded_files = opciones.get('uploaded_files')
        if uploaded_files:
            st.success(f"Se han cargado {len(uploaded_files)} archivos.")
            dicom_files = uploaded_files
        else:
            st.info("Por favor, carga uno o más archivos DICOM.")
    elif tipo_carga == "Clasificación de Mamografías":
        # Actualmente, no se realiza ninguna carga aquí.
        # Puedes implementar futuras funcionalidades para la clasificación.
        st.info("Funcionalidad de Clasificación mediante Deep Learning en desarrollo.")
    else:
        st.info("Selecciona un método de carga de imágenes.")

    return dicom_files
