## 📂 Carpeta `processed`

Esta carpeta está destinada a almacenar las imágenes procesadas y los archivos CSV generados durante las diferentes etapas del preprocesamiento. Debido al tamaño que alcanzan estos archivos procesados, esta carpeta no se incluye en el repositorio de GitHub.

### Instrucciones

1. **Descarga el dataset original:**
   Descarga el dataset original desde [VinDr-Mammo Dataset](https://vindr.ai/datasets/mammo) y sigue las instrucciones para ubicar los archivos en la carpeta `original/`.

2. **Ejecución de los notebooks:**
   Una vez que hayas descargado los datos originales, debes ejecutar los notebooks disponibles en la carpeta `notebooks/` para realizar las siguientes tareas:
   
   - Conversión de las imágenes DICOM a formatos PNG.
   - Extracción de Regiones de Interés (ROI).
   - Aumento de datos (Data Augmentation).
   - Balanceo del dataset.

3. **Generación automática:**
   Las imágenes procesadas (convertidas a PNG, recortadas, aumentadas, etc.) y los archivos CSV serán automáticamente generados y almacenados en la carpeta `processed/` tras la ejecución de los notebooks.

### Estructura esperada

Después de ejecutar los notebooks, la estructura de la carpeta `processed/` debería verse de la siguiente manera:

```bash
📂 VinDr-Mammo-Preprocessing/
│
├── 📂 data/
│   └── 📂 processed/
│       ├── 📂 images_png/               # Imágenes convertidas a PNG
│       ├── 📂 roi_images/               # Imágenes recortadas con las ROI
│       ├── 📂 augmented_images/         # Imágenes aumentadas
│       └── 📂 csv/
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
└── README.md
