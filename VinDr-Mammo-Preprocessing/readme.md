# VinDr-Mammo Preprocessing

## Descripción del Proyecto

Este repositorio contiene el preprocesamiento de imágenes médicas DICOM del dataset **VinDr-Mammo**. El objetivo es preparar las imágenes para su posterior clasificación, específicamente para detectar tejido canceroso utilizando modelos de Deep Learning. El preprocesamiento incluye la conversión de imágenes DICOM a formatos más manejables como PNG, la extracción de Regiones de Interés (ROI) y el aumento de datos para mejorar la robustez del modelo.

El flujo de trabajo ha sido diseñado para alimentar a los otros integrantes del grupo que se encargarán de entrenar y evaluar modelos de clasificación basados en las imágenes preprocesadas.

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
│       ├── 📂 subset_datos/               # Subset de imágenes DICOM con algun filtro del origial Dataset
            ├── 📂 Images_Mass_Calc       # Subset de Imágenes DICOM filtradas con masas y calcificaciones
│       ├── 📂 roi_images/               # Imágenes recortadas con las ROI
            ├── 📂 ROICROP1           # Primeros recortes obtenidos de masas y calcificaciones
│       ├── 📂 augmented_images/         # Imágenes aumentadas
│       └── 📂 csv/
│           ├── combined_annotations_metadata.csv   # CSV de la unión del csv de anotaciones con el de metadata
│           ├── filtered_mass_calcifications.csv    # similar al anterior pero filtrando masas y calcificaciones
│           ├── filtered_with_image_names.csv       # Añadiendo una nueva columna para las que las imágenes con mas de 1 anotación tengan nombre distinto
│           └── CROP1.csv          # csv con las nuevas coordenadas de los recortes realizados de masas y calcificaciones.
│
├── 📂 notebooks/
│   ├── Generación_de_CSV.ipynb     # Notebook que genera los CSV guardados en la carpeta con ese nombre
│   ├── Generar_imágenes_Masas.ipynb                   # Copia las imágenes de la carpeta original, las filtra y las guarda en subset_datos
│   ├── ROI_Mass_Calc.ipynb              # Primeros recortes obtenidos de masas y calcificaciones
│ 
│
├── 📂 results/
│   ├── visualizations.ipynb/                  # Gráficos de resultados del procesamiento hecho ( pendiente)
│   
│
├── README.md                                  # Este archivo





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


### Citación


```
Nguyen, H. T., Nguyen, H. Q., Pham, H. H., Lam, K., Le, L. T., Dao, M., & Vu, V. (2022). VinDr-Mammo: A large-scale benchmark dataset for computer-aided diagnosis in full-field digital mammography. *medRxiv*. https://doi.org/10.1101/2022.03.07.22272009
```

