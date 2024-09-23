## 📂 Carpeta `processed`

Esta carpeta está destinada a almacenar las imágenes procesadas y los archivos CSV generados durante las diferentes etapas del preprocesamiento. Debido al tamaño que alcanzan estos archivos procesados, esta carpeta no se incluye en el repositorio de GitHub.

### Instrucciones

1. **Descarga el dataset original:**
   Descarga el dataset original desde [VinDr-Mammo Dataset](https://usmcl-my.sharepoint.com/:u:/g/personal/nicolas_ruizr_usm_cl/ERkdXH9Oma9AivuEORKtI6UBkiTr58_FuwL0Xc1YcNhr9w?e=WWd7wa)) y sigue las instrucciones para ubicar los archivos en la carpeta `original/`.

Una vez descargado se debe descomprimir y renombrar como "Vindrmammo" y ubicarlo en la carpeta llamada original. Debiese quedar así la estructura:

```bash

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
```
            
2. **Ejecución de los notebooks:**
   Una vez que hayas descargado los datos originales, debes ejecutar los notebooks disponibles en la carpeta `notebooks/` para realizar las siguientes tareas:
   
   - Generación de CSV necesarios
   - Generación de subsets de imágenes
   - Extracción de Regiones de Interés (ROI).


3. **Generación automática:**
   Las imágenes procesadas (convertidas a PNG, recortadas, etc.) y los archivos CSV serán automáticamente generados y almacenados en la carpeta `processed/` tras la ejecución de los notebooks.

### Estructura esperada

Después de ejecutar los notebooks, la estructura de la carpeta `processed/` debería verse de la siguiente manera:

```bash
📂 VinDr-Mammo-Preprocessing
│
├── 📂 data/        
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

```
