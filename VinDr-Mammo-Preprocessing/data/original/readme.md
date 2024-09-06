# 📂 Carpeta `original`

Esta carpeta está destinada a contener los datos originales del dataset VinDr-Mammo, que debido a su tamaño (~350 GB) no puede ser incluido en este repositorio de GitHub.

## Instrucciones

1. **Descarga el dataset VinDr-Mammo:**

   El dataset completo se puede descargar desde la página oficial de PhysioNet o desde la fuente oficial [VinDr-Mammo Dataset](https://vindr.ai/datasets/mammo).

2. **Ubica los archivos en la carpeta correspondiente:**

   Una vez descargado el dataset completo, deberás crear manualmente la estructura de carpetas necesaria y mover los archivos de imágenes DICOM y los archivos CSV a la carpeta `originals/Vindrmammo/`.

3. **Estructura esperada:**

   El dataset descargado debe organizarse de la siguiente forma dentro de la carpeta `originals/`:

   ```bash
   📂 originals/
   │
   └── 📂 Vindrmammo/
       └── 📂 images/    # Carpeta base de imágenes DICOM originales
           └── 📂 fff2339ea4b5d2f1792672ba7d52b318/  # Carpeta de un exámen con sus 4 vistas en formato DICOM 
               └── 5144bf29398269fa2cf8c36b9c6db7f3.dicom
               └── fe9b6ffe97a3b4b763cf94c9982254beb.dicom
               └── e4199214f5b40bd40847f5c2aedc44ef.dicom
               └── f1b6aa1cc6246c2760b882243657212e.dicom
           └── 📂 ffe7a45f8390f242db3b843762a4a7aa/
           └── 📂 .../
       └── finding_annotations.csv 
       └── breast-level_annotations.csv
       └── metadata.csv

4. **Ubicación de los archivos CSV:**


- **finding_annotations.csv**: Archivo CSV con las anotaciones de hallazgos y coordenadas de las ROI.
- **breast-level_annotations.csv**: Archivo CSV con las anotaciones a nivel de imagen.
- **metadata.csv**: Archivo CSV con los metadatos de las imágenes.

