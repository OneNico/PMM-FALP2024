# src/ui/opciones_procesamiento.py

import streamlit as st

def mostrar_opciones_procesamiento():
    """
    Muestra opciones de procesamiento en la barra lateral y devuelve las selecciones.
    """
    st.sidebar.header("Opciones de Procesamiento")
    aplicar_voilut = st.sidebar.checkbox("Aplicar VOI LUT", value=True)
    aplicar_normalizacion = st.sidebar.checkbox("Aplicar normalización", value=True)
    aplicar_filtro = st.sidebar.checkbox("Aplicar filtro de suavizado", value=False)
    # Puedes agregar más opciones según tus necesidades

    opciones = {
        "voilut": aplicar_voilut,
        "normalizacion": aplicar_normalizacion,
        "filtro": aplicar_filtro,
        # Agrega más opciones si lo deseas
    }
    return opciones
