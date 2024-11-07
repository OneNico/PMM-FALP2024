
# SMART MAMMO

En este repositorio encontramos el desarrollo de la interfáz de nuestra aplicación, realizado con el framework streamlit.

## Descripción

SMART MAMMO es una herramienta diseñada para ayudar en la clasificación y análisis de mamografías, utilizando técnicas avanzadas de Deep Learning. La aplicación permite la visualización de imágenes DICOM, procesamiento masivo de imágenes y ofrece resultados de clasificación con modelos entrenados en conjuntos de datos especializados.

## Características

- **Visor DICOM**: Visualiza y ajusta imágenes DICOM con controles de brillo y contraste, zoom, rotación y desplazamiento.
- **Procesamiento Masivo**: Procesa múltiples imágenes DICOM, PNG o JPG de forma simultánea, aplicando modelos de clasificación para obtener resultados y generar reportes en PDF.
- **Clasificación Inteligente**: Utiliza modelos de Deep Learning para clasificar imágenes en categorías como masas, calcificaciones y no encontrado, con subcategorías adicionales de benigno, maligno y sospechoso.

## Instalación

### Prerrequisitos

- Python 3.7 o superior
- Pip instalado

### Pasos de instalación

1. Clona este repositorio:

   ```bash
   git clone https://github.com/tu_usuario/SMART_MAMMO.git
   cd SMART_MAMMO


2. Crea un entorno virtual (opcional pero recomendado):
   ```bash
   python -m venv venv
   source venv/bin/activate  # En Windows: venv\Scripts\activate

3. Instala las dependencias:
   ```bash
   pip install -r requirements.txt


4. Ejecuta la aplicación Streamlit:
   ```bash
   streamlit run app.py


## Estructura del Proyecto:
```bash
├── app.py
├── requirements.txt
├── src
    ├── __init__.py
    ├── modulos
    │   ├── __init__.py
    │   ├── gestion_dicom.py
    │   ├── procesamiento_i.py
    │   ├── procesamiento_m.py
    │   └── visor_dicom.py
    └── ui
        ├── __init__.py
        ├── styles.css
        └── visual.py



   
