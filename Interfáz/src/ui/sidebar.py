# src/ui/sidebar.py

import streamlit as st

def mostrar_sidebar():
    """
    Muestra la barra lateral con opciones y devuelve las selecciones.
    """
    st.sidebar.header("Menú")

    # Opción para seleccionar el modo de carga
    tipo_carga = st.sidebar.radio("Selecciona el tipo de carga", ["Cargar Imágenes", "Cargar Carpeta"])
    opciones = {'tipo_carga': tipo_carga}

    st.sidebar.markdown("---")  # Separador

    if tipo_carga == "Cargar Imágenes":
        # Permitir al usuario cargar imágenes individuales
        uploaded_files = st.sidebar.file_uploader(
            label="Cargar imágenes DICOM",
            type=["dcm", "dicom"],
            accept_multiple_files=True,
            help="Puedes cargar uno o más archivos DICOM para visualizarlos."
        )
        opciones['uploaded_files'] = uploaded_files

        st.sidebar.markdown("---")  # Separador
        st.sidebar.subheader("Opciones de Procesamiento")

        aplicar_voilut = st.sidebar.checkbox("Aplicar VOI LUT", value=True)
        mostrar_metadatos = st.sidebar.checkbox("Mostrar Metadatos", value=False)
        aplicar_transformaciones = st.sidebar.checkbox("Aplicar Transformaciones", value=False)

        # Opción para invertir interpretación fotométrica
        invertir_interpretacion = st.sidebar.checkbox(
            "Invertir interpretación fotométrica",
            value=False,
            help="Invierte la interpretación fotométrica actual de la imagen"
        )

        opciones.update({
            'aplicar_voilut': aplicar_voilut,
            'mostrar_metadatos': mostrar_metadatos,
            'aplicar_transformaciones': aplicar_transformaciones,
            'invertir_interpretacion': invertir_interpretacion
        })

        if aplicar_transformaciones:
            st.sidebar.markdown("---")  # Separador
            st.sidebar.subheader("Transformaciones Disponibles")

            rotar = st.sidebar.checkbox("Rotar", value=False)
            voltear_horizontal = st.sidebar.checkbox("Volteo Horizontal", value=False)
            voltear_vertical = st.sidebar.checkbox("Volteo Vertical", value=False)
            brillo_contraste = st.sidebar.checkbox("Ajuste de Brillo y Contraste", value=False)
            ruido_gaussiano = st.sidebar.checkbox("Añadir Ruido Gaussiano", value=False)
            enfoque = st.sidebar.checkbox("Aplicar Enfoque", value=False)
            recorte_redimension = st.sidebar.checkbox("Recorte y Redimensionado Aleatorio", value=False)
            desenfoque = st.sidebar.checkbox("Aplicar Desenfoque", value=False)

            opciones.update({
                'rotar': rotar,
                'voltear_horizontal': voltear_horizontal,
                'voltear_vertical': voltear_vertical,
                'brillo_contraste': brillo_contraste,
                'ruido_gaussiano': ruido_gaussiano,
                'enfoque': enfoque,
                'recorte_redimension': recorte_redimension,
                'desenfoque': desenfoque
            })
    elif tipo_carga == "Cargar Carpeta":
        st.sidebar.markdown("---")  # Separador

        # Mostrar ruta de la carpeta a cargar
        ruta_carpeta = st.sidebar.text_input(
            "Ruta de la carpeta en el servidor",
            value="data/raw",
            help="Ingresa la ruta de la carpeta que contiene las imágenes DICOM."
        )
        opciones['ruta_carpeta'] = ruta_carpeta

        # Mostrar mensaje al presionar "Cargar Carpeta"
        st.sidebar.info("Recuerda cargar tus imágenes DICOM en la carpeta 'data/raw'.")

        # Establecer opciones por defecto para 'Cargar Carpeta'
        opciones.update({
            'aplicar_voilut': True,
            'mostrar_metadatos': False,
            'aplicar_transformaciones': False,
            'invertir_interpretacion': False,
            'interpretacion_fotometrica': '2'
        })

    # Agregar control de paginación
    if tipo_carga == "Cargar Carpeta":
        opciones['pagina'] = st.sidebar.number_input(
            "Página",
            min_value=1,
            step=1,
            value=1,
            help="Selecciona la página de imágenes a visualizar."
        )
        opciones['imagenes_por_pagina'] = st.sidebar.number_input(
            "Imágenes por Página",
            min_value=1,
            step=1,
            value=10,
            help="Define cuántas imágenes se mostrarán por página."
        )

    return opciones
