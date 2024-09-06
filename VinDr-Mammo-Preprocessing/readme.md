VinDr-Mammo Preprocessing
Descripción del Proyecto
Este repositorio contiene el preprocesamiento de imágenes médicas DICOM del dataset VinDr-Mammo. El objetivo es preparar las imágenes para su posterior clasificación, específicamente para detectar tejido canceroso utilizando modelos de Deep Learning. El preprocesamiento incluye la conversión de imágenes DICOM a formatos más manejables , la extracción de Regiones de Interés (ROI) y el aumento de datos para mejorar la robustez del modelo.

El flujo de trabajo ha sido diseñado para alimentar a otros equipos de trabajo que se encargarán de entrenar y evaluar modelos de clasificación basados en las imágenes preprocesadas.

Estructura del Repositorio

📂 VinDr-Mammo-Preprocessing
│
├── 📂 data/
│   ├── 📂 original/
│   │   └── dicom/                    # Imágenes DICOM originales
│   └── 📂 processed/
│       ├── images_png/               # Imágenes convertidas a PNG/JPEG
│       ├── roi_images/               # Imágenes recortadas con las ROI
│       ├── augmented_images/         # Imágenes aumentadas
│       └── csv/
│           ├── breast_level_annotations.csv   # CSV con anotaciones a nivel de imagen
│           ├── finding_annotations.csv        # CSV con anotaciones de hallazgos
│           ├── ss1.csv                        # CSV con ROI seleccionadas
│           └── metacomprimida.csv             # Otros CSV procesados o comprimidos
│
├── 📂 notebooks/
│   ├── Preprocessing_DICOM_to_PNG.ipynb       # Conversión de DICOM a PNG/JPEG
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


