# src/modulos/visor_dicom.py

import streamlit as st
from PIL import Image, ImageEnhance
import pydicom
import numpy as np
from io import BytesIO
import logging
from pydicom.pixels import apply_voi_lut
import base64
import json

from src.modulos.procesamiento_i import procesamiento_individual  # Importar la función de procesamiento individual

logger = logging.getLogger(__name__)

def visualizar_dicom(opciones):
    st.write("---")
    st.header("Visor Avanzado de Imágenes DICOM")

    # Subir múltiples archivos DICOM
    uploaded_files = st.file_uploader(
        "Cargar archivos DICOM",
        type=["dcm", "dicom"],
        accept_multiple_files=True
    )

    if not uploaded_files:
        st.info("Por favor, carga uno o más archivos DICOM para visualizar.")
        return

    num_imagenes = len(uploaded_files)
    logger.info(f"Cantidad de imágenes cargadas para visualización: {num_imagenes}")

    # Seleccionar la imagen a visualizar
    selected_file = st.selectbox(
        "Selecciona una imagen DICOM para visualizar",
        uploaded_files,
        format_func=lambda x: x.name
    )

    # Checkbox para abrir el visor
    abrir_visor = st.checkbox("Abrir Visor DICOM")

    if abrir_visor:
        mostrar_visor(selected_file, opciones)

def mostrar_visor(selected_file, opciones):
    imagen, ds, pixel_spacing = procesar_imagen_dicom(selected_file)

    if imagen is not None:
        # Control de brillo y contraste
        col1, col2 = st.columns([1, 1])
        with col1:
            brillo = st.slider("Brillo", -100, 100, 0, key=f"brillo_{selected_file.name}")
        with col2:
            contraste = st.slider("Contraste", -100, 100, 0, key=f"contraste_{selected_file.name}")

        # Aplicar ajustes de brillo y contraste
        imagen_editada = ajustar_brillo_contraste(imagen, brillo, contraste)

        # Convertir la imagen a base64 para incrustarla en HTML
        buffered = BytesIO()
        imagen_editada.save(buffered, format="PNG")
        img_base64 = base64.b64encode(buffered.getvalue()).decode()

        # HTML y JavaScript para hacer la imagen draggable, zoom, rotación y reset
        draggable_image_html = f"""
        <html>
        <head>
        <style>
            #container {{
                width: 100%;
                height:800px; /* Altura ajustada */
                position: relative;
                overflow: hidden;
                border: 1px solid #ddd;
                background-color: #000; /* Fondo negro para mejor visualización */
                display: flex;
                align-items: center;
                justify-content: center;
            }}
            #draggable {{
                position: absolute;
                cursor: grab;
                user-select: none;
                transition: transform 0.1s ease;
                max-width: none;
                max-height: none;
                z-index: 100;
            }}
            #controls {{
                position: absolute;
                top: 10px;
                left: 10px;
                z-index: 1000;
            }}
            #controls button {{
                background-color: #1F4E79;
                color: white;
                border: none;
                padding: 5px 10px;
                margin-right: 5px;
                margin-bottom: 5px;
                border-radius: 3px;
                cursor: pointer;
                font-size: 16px;
            }}
            #canvas {{
                position: absolute;
                top: 0;
                left: 0;
                z-index: 200;
            }}
        </style>
        </head>
        <body>
            <div id="container">
                <div id="controls">
                    <button onclick="zoomIn()">+</button>
                    <button onclick="zoomOut()">-</button>
                    <button onclick="rotateLeft()">⟲</button>
                    <button onclick="rotateRight()">⟳</button>
                    <button onclick="resetTransformations()">⎌ Reset</button>
                </div>
                <img id="draggable" src="data:image/png;base64,{img_base64}" draggable="false" />
            </div>
            <script>
                const img = document.getElementById("draggable");
                const container = document.getElementById("container");
                let isDragging = false;
                let startX, startY;
                let translateX = 0, translateY = 0;
                let scale = 1;
                let rotation = 0;
                const imageKey = {json.dumps(selected_file.name)};  // Clave única para cada imagen

                // Agregar una variable para almacenar las transformaciones iniciales
                let initialTransformations = {{}};

                // Función para calcular la escala y posición inicial
                function calculateInitialScale() {{
                    const containerWidth = container.clientWidth;
                    const containerHeight = container.clientHeight;
                    const imgNaturalWidth = img.naturalWidth;
                    const imgNaturalHeight = img.naturalHeight;

                    const scaleWidth = containerWidth / imgNaturalWidth;
                    const scaleHeight = containerHeight / imgNaturalHeight;
                    let initialScale = Math.min(scaleWidth, scaleHeight);

                    // Multiplicar la escala inicial por un factor para agrandar la imagen
                    initialScale *= 1.2; // Puedes ajustar este valor (1.2) para agrandar más o menos la imagen

                    scale = initialScale;

                    // Centrar la imagen
                    translateX = (containerWidth - imgNaturalWidth * scale) / 2;
                    translateY = (containerHeight - imgNaturalHeight * scale) / 2;

                    rotation = 0;

                    // Guardar las transformaciones iniciales
                    initialTransformations = {{
                        translateX: translateX,
                        translateY: translateY,
                        scale: scale,
                        rotation: rotation
                    }};
                }}

                // Cargar transformaciones desde localStorage
                function loadTransformations() {{
                    const savedTransformations = localStorage.getItem('transformations_' + imageKey);
                    if (savedTransformations) {{
                        const {{ translateX: tx, translateY: ty, scale: s, rotation: r }} = JSON.parse(savedTransformations);
                        translateX = tx;
                        translateY = ty;
                        scale = s;
                        rotation = r;
                    }} else {{
                        // No hay transformaciones guardadas, calcular escala inicial
                        calculateInitialScale();
                    }}
                }}

                // Guardar transformaciones en localStorage
                function saveTransformations() {{
                    const transformations = {{
                        translateX,
                        translateY,
                        scale,
                        rotation
                    }};
                    localStorage.setItem('transformations_' + imageKey, JSON.stringify(transformations));
                }}

                // Llamar a loadTransformations al cargar la imagen
                img.onload = () => {{
                    calculateInitialScale();
                    loadTransformations();
                    updateTransform();
                }};

                img.addEventListener("mousedown", (e) => {{
                    isDragging = true;
                    startX = e.clientX - translateX;
                    startY = e.clientY - translateY;
                    img.style.cursor = "grabbing";
                }});

                img.addEventListener("mousemove", (e) => {{
                    if (isDragging) {{
                        translateX = e.clientX - startX;
                        translateY = e.clientY - startY;
                        updateTransform();
                    }}
                }});

                img.addEventListener("mouseup", (e) => {{
                    if (isDragging) {{
                        isDragging = false;
                        img.style.cursor = "grab";
                    }}
                }});

                // Asegurar que los eventos funcionen también si el ratón sale de la imagen
                document.addEventListener("mouseup", (e) => {{
                    if (isDragging) {{
                        isDragging = false;
                        img.style.cursor = "grab";
                    }}
                }});

                // Prevenir el comportamiento por defecto de arrastre de la imagen
                img.addEventListener("dragstart", (e) => {{
                    e.preventDefault();
                }});

                function zoomIn() {{
                    scale += 0.1;
                    updateTransform();
                }}

                function zoomOut() {{
                    scale = Math.max(0.1, scale - 0.1);
                    updateTransform();
                }}

                function rotateLeft() {{
                    rotation -= 15;
                    updateTransform();
                }}

                function rotateRight() {{
                    rotation += 15;
                    updateTransform();
                }}

                function resetTransformations() {{
                    // Restaurar las transformaciones iniciales
                    translateX = initialTransformations.translateX;
                    translateY = initialTransformations.translateY;
                    scale = initialTransformations.scale;
                    rotation = initialTransformations.rotation;

                    // Eliminar las transformaciones guardadas en localStorage
                    localStorage.removeItem('transformations_' + imageKey);

                    updateTransform();
                }}

                function updateTransform() {{
                    img.style.transform = `translate(${{translateX}}px, ${{translateY}}px) scale(${{scale}}) rotate(${{rotation}}deg)`;
                    // Guardar las transformaciones
                    saveTransformations();
                }}
            </script>
        </body>
        </html>
        """

        # Mostrar la imagen con funcionalidad de arrastre, zoom, rotación y reset
        st.components.v1.html(draggable_image_html, height=800)  # Ajustar la altura a 800

        # Descargar DICOM modificado y PNG de alta resolución, y botón "Analizar mamografía"
        st.subheader("Descargar Imagen Modificada")

        # Convertir la imagen editada a escala de grises para guardar en DICOM
        imagen_gris = imagen_editada.convert("L")
        pixel_data = np.array(imagen_gris)

        # Botones para descargar en DICOM, PNG y Analizar mamografía
        col1, col2, col3 = st.columns(3)
        with col1:
            dicom_buffer = BytesIO()
            try:
                # Aplicar los cambios al dataset DICOM
                ds.PixelData = pixel_data.tobytes()
                ds.Rows, ds.Columns = pixel_data.shape

                ds.save_as(dicom_buffer)
                dicom_buffer.seek(0)

                # Preparar el archivo para descarga
                st.download_button(
                    label="Descargar DICOM Modificado",
                    data=dicom_buffer,
                    file_name=f"modificado_{selected_file.name}",
                    mime="application/dicom",
                    key="download_dicom"
                )
            except Exception as e:
                st.error(f"Error al preparar el archivo DICOM: {e}")

        with col2:
            try:
                png_buffer = BytesIO()
                # Guardar la imagen editada en el buffer con alta calidad
                imagen_editada.save(png_buffer, format="PNG")
                png_buffer.seek(0)

                # Preparar el archivo para descarga
                st.download_button(
                    label="Descargar PNG de Alta Resolución",
                    data=png_buffer,
                    file_name=f"modificado_{selected_file.name}.png",
                    mime="image/png",
                    key="download_png"
                )
            except Exception as e:
                st.error(f"Error al preparar la imagen PNG: {e}")

        with col3:
            analizar = st.button("Analizar mamografía", key=f"analizar_{selected_file.name}")

        if analizar:
            with st.spinner("Analizando..."):
                opciones_procesamiento = {
                    'uploaded_image': selected_file
                }
                procesamiento_individual(opciones_procesamiento)
    else:
        st.error(f"No se pudo procesar la imagen {selected_file.name}")

def procesar_imagen_dicom(dicom_file):
    try:
        dicom = pydicom.dcmread(BytesIO(dicom_file.getvalue()))
        original_image = dicom.pixel_array

        pixel_spacing = dicom.get('PixelSpacing', None)
        if pixel_spacing is not None:
            pixel_spacing = [float(spacing) for spacing in pixel_spacing]
        else:
            pixel_spacing = dicom.get('ImagerPixelSpacing', None)
            if pixel_spacing is not None:
                pixel_spacing = [float(spacing) for spacing in pixel_spacing]
            else:
                pixel_spacing = [1, 1]

        img_windowed = apply_voi_lut(original_image, dicom)

        photometric_interpretation = dicom.get('PhotometricInterpretation', 'UNKNOWN')
        if photometric_interpretation == 'MONOCHROME1':
            img_windowed = np.max(img_windowed) - img_windowed

        img_normalized_display = (img_windowed - np.min(img_windowed)) / (np.max(img_windowed) - np.min(img_windowed))
        img_normalized_display = (img_normalized_display * 255).astype(np.uint8)

        image_display = Image.fromarray(img_normalized_display).convert('L')

        return image_display, dicom, pixel_spacing

    except Exception as e:
        logger.error(f"Error al procesar el archivo DICOM: {e}")
        st.error(f"Error al procesar el archivo DICOM: {e}")
        return None, None, None

def ajustar_brillo_contraste(imagen, brillo, contraste):
    try:
        enhancer = ImageEnhance.Brightness(imagen)
        imagen = enhancer.enhance(1 + brillo / 100)

        enhancer = ImageEnhance.Contrast(imagen)
        imagen = enhancer.enhance(1 + contraste / 100)

        return imagen
    except Exception as e:
        logger.error(f"Error al ajustar brillo y contraste: {e}")
        st.error(f"Error al ajustar brillo y contraste: {e}")
        return imagen
