# VinDr-Mammo Preprocessing

## Descripción del Proyecto

Este repositorio contiene el preprocesamiento de imágenes médicas DICOM del dataset **VinDr-Mammo**. El objetivo es preparar las imágenes para su posterior clasificación, específicamente para detectar tejido canceroso utilizando modelos de Deep Learning. El preprocesamiento incluye la conversión de imágenes DICOM a formatos más manejables (PNG/JPEG), la extracción de Regiones de Interés (ROI) y el aumento de datos para mejorar la robustez del modelo.

El flujo de trabajo ha sido diseñado para alimentar a otros equipos de trabajo que se encargarán de entrenar y evaluar modelos de clasificación basados en las imágenes preprocesadas.

## Estructura del Repositorio

```plaintext
📂 VinDr-Mammo-Preprocessing
│
├── 📂 data/
│   ├── 📂 original/
│   │   └── 📂 Vindrmammo/
            └── 📂 images/    # Carpeta base de imágenes DICOM originales
                └── 📂 fff2339ea4b5d2f1792672ba7d52b318/  #Carpeta de un exámen con sus 4 vistas en formato DICOM 
                    └── 5144bf29398269fa2cf8c36b9c6db7f3.dicom
                    └── fe9b6ffe97a3b4b763cf94c9982254beb.dicom
                    └── e4199214f5b40bd40847f5c2aedc44ef.dicom
                    └── f1b6aa1cc6246c2760b882243657212e.dicom
                └── 📂 ffe7a45f8390f242db3b843762a4a7aa/
                └── 📂 .../
            └── finding_annotations.csv 
            └── breast-level_annotations.csv
            └── metadata.csv                
│   └── 📂 processed/
│       ├── images_png/               # Imágenes convertidas a PNG
│       ├── roi_images/               # Imágenes recortadas con las ROI
│       ├── augmented_images/         # Imágenes aumentadas
│       └── csv/
│           ├── breast_level_annotations.csv   # CSV con anotaciones a nivel de imagen
│           ├── finding_annotations.csv        # CSV con anotaciones de hallazgos
│           ├── ss1.csv                        # CSV con ROI seleccionadas
│           └── metacomprimida.csv             # Otros CSV procesados o comprimidos
│
├── 📂 notebooks/
│   ├── Preprocessing_DICOM_to_PNG.ipynb       # Conversión de DICOM a PNG
│   ├── ROI_Extraction.ipynb                   # Extracción de ROI
│   ├── Data_Augmentation.ipynb                # Aumento de datos
│   └── Dataset_Balancing.ipynb                # Balanceo del dataset
│
├── 📂 utils/
│   └── utils.py                               # Funciones auxiliares
│
├── 📂 results/
│   ├── 📂 visualizations/                     # Gráficos de resultados
│   └── performance_report.md                  # Resumen del preprocesamiento
│
├── README.md                                  # Este archivo
└── requirements.txt                           # Dependencias necesarias



## Requisitos

Para poder ejecutar los Notebooks y scripts de preprocesamiento, asegúrate de instalar las siguientes dependencias. Puedes instalar todo con el archivo `requirements.txt`:

```bash
pip install -r requirements.txt
```

### Dependencias:
- `pydicom`
- `opencv-python`
- `numpy`
- `pandas`
- `matplotlib`
- `seaborn`

## Flujo de Trabajo

El flujo de trabajo del preprocesamiento se divide en las siguientes etapas:

### 1. Conversión de DICOM a PNG/JPEG
- **Notebook**: `Preprocessing_DICOM_to_PNG.ipynb`
- **Descripción**: Las imágenes DICOM se convierten a formatos más manejables (PNG o JPEG) y se redimensionan a un tamaño adecuado (por ejemplo, 299x299 píxeles).
- **Entrada**: Imágenes DICOM en `data/original/dicom/`.
- **Salida**: Imágenes PNG en `data/processed/images_png/`.

### 2. Extracción de Regiones de Interés (ROI)
- **Notebook**: `ROI_Extraction.ipynb`
- **Descripción**: Se extraen las ROI de las imágenes, utilizando las coordenadas de las cajas delimitadoras en los archivos CSV de anotaciones. Las imágenes resultantes contienen solo las áreas de interés.
- **Entrada**: Imágenes PNG y CSV de anotaciones en `data/processed/`.
- **Salida**: Imágenes con las ROI recortadas en `data/processed/roi_images/`.

### 3. Aumento de Datos
- **Notebook**: `Data_Augmentation.ipynb`
- **Descripción**: Se aplican técnicas de aumento de datos a las imágenes para generar múltiples versiones y mejorar la generalización del modelo (rotaciones, inversiones, ajustes de brillo/contraste, etc.).
- **Entrada**: Imágenes PNG o ROI.
- **Salida**: Imágenes aumentadas en `data/processed/augmented_images/`.

### 4. Balanceo del Dataset
- **Notebook**: `Dataset_Balancing.ipynb`
- **Descripción**: Se ajusta el balance entre las clases aplicando oversampling o undersampling para manejar el desbalance en las categorías (normal, benigno, maligno).
- **Entrada**: CSV con anotaciones y clases de las imágenes.
- **Salida**: Dataset balanceado en los archivos CSV.

## Instrucciones de Uso

1. **Clonar el repositorio**:

   ```bash
   git clone https://github.com/tu-usuario/VinDr-Mammo-Preprocessing.git
   cd VinDr-Mammo-Preprocessing
   ```

2. **Instalar las dependencias**:

   ```bash
   pip install -r requirements.txt
   ```

3. **Ejecutar los Notebooks**: Abre los Notebooks en la carpeta `notebooks/` y ejecuta cada uno según la etapa de preprocesamiento que desees realizar:
   - Para convertir las imágenes DICOM: Ejecuta `Preprocessing_DICOM_to_PNG.ipynb`.
   - Para extraer las ROI: Ejecuta `ROI_Extraction.ipynb`.
   - Para realizar aumento de datos: Ejecuta `Data_Augmentation.ipynb`.
   - Para balancear el dataset: Ejecuta `Dataset_Balancing.ipynb`.

## Resultados

Los resultados de cada etapa de preprocesamiento se almacenan en las siguientes carpetas:

- **`data/processed/images_png/`**: Contiene las imágenes convertidas a PNG.
- **`data/processed/roi_images/`**: Contiene las imágenes recortadas con las ROI.
- **`data/processed/augmented_images/`**: Contiene las imágenes aumentadas.
- **`data/processed/csv/`**: Contiene los archivos CSV actualizados con las anotaciones y coordenadas de las ROI.


---

### Citación


```
Nguyen, H. T., Nguyen, H. Q., Pham, H. H., Lam, K., Le, L. T., Dao, M., & Vu, V. (2022). VinDr-Mammo: A large-scale benchmark dataset for computer-aided diagnosis in full-field digital mammography. *medRxiv*. https://doi.org/10.1101/2022.03.07.22272009
```

