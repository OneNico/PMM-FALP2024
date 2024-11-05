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
            ├── 📂 images_with_other    # Subset de datos DICOM que incluye además de masas y calcificaciones, otros hallazgos.   
│       ├── 📂 roi_images/               # Carpeta con imágenes recortadas con las ROI
│       ├── 📂 augmented_images/         # Carpeta con mágenes aumentadas 
│       └── 📂 csv/    # Carpeta que contiene distintos csv generados de los subset, aumentos o roircrop realziados
├── 📂 notebooks/ # Carpeta con los distintos notebooks utilizados durante el preprocesamiento del dataset.
├── README.md                                  # Este archivo

```



### Citación


```
Nguyen, H. T., Nguyen, H. Q., Pham, H. H., Lam, K., Le, L. T., Dao, M., & Vu, V. (2022). VinDr-Mammo: A large-scale benchmark dataset for computer-aided diagnosis in full-field digital mammography. *medRxiv*. https://doi.org/10.1101/2022.03.07.22272009
```

