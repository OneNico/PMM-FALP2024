# PMM-FALP2024

**Clasificación de Imágenes de
Mamografía usando Machine Learning
para la Detección de Tejido Canceroso.** es un proyecto que se enmarca en el contexto de las Memorias Multidisciplinarias de la Universidad Técnica Federico Santa María orientado en la clasificación de lesiones en mamografías utilizando modelos de Deep Learning. El objetivo es desarrollar un sistema automatizado que permita identificar regiones sospechosas en las mamografías, para luego clasificarlas en tejido sano o sospechoso. El sistema utiliza un enfoque basado en Machine Learning con el fin de mejorar la precisión y eficiencia en el diagnóstico.

## Estructura del Proyecto

El proyecto está organizado en varias carpetas y archivos, cada una dedicada a diferentes aspectos del desarrollo y la validación del modelo:

### 1. **Evaluation and Testing** 
   - Esta carpeta está planificada para incluir scripts y notebooks utilizados para la evaluación del modelo entrenado. 
   
### 2. **Exploratory Data Analysis**
   - Contiene notebooks utilizados para realizar un análisis exploratorio de los datos. En esta etapa, se estudian los datos disponibles, las distribuciones y las características de las imágenes y los metadatos que formarán la base del entrenamiento.
   - Incluye visualizaciones de las mamografías y un análisis del dataset elegido el cual es VinDr-Mammo.


### 3. **Model Training and Validation** 
   - Esta carpeta está destinada a contener los scripts y notebooks relacionados con el entrenamiento y validación del modelo de Deep Learning.
 

### 4. **VinDr-Mammo-Preprocessing**
   - Contiene scripts y notebooks que se encargan del preprocesamiento de las imágenes de mamografías. Este módulo convierte las imágenes en formato DICOM a PNG, recorta las regiones de interés (ROI) y aplica técnicas de normalización.
   - Herramientas utilizadas: `pydicom`, `OpenCV`, y `NumPy`.

### 4. **BeningMalignant_Masses-Preprocessing**
   - Contiene el set de datos llamado "Dataset of Breast mammography images with Masses" , el cual contiene imágenes de masas tanto beningnas como malignas, ya pre-procesadas.
     

## Requisitos

Para ejecutar los scripts de este repositorio, es necesario tener instaladas las siguientes dependencias:

- `Python 3.8+`
- `OpenCV`
- `pydicom`
- `NumPy`
- `Pandas`
- `Matplotlib`
- `Seaborn`


## Uso

1. **Preprocesamiento de Imágenes**:
   - Ejecuta los notebooks dentro de la carpeta `VinDr-Mammo-Preprocessing` para convertir las imágenes DICOM a PNG y extraer las regiones de interés (lesiones).

2. **Análisis Exploratorio**:
   - Utiliza los notebooks en la carpeta `Exploratory Data Analysis` para obtener información detallada sobre la calidad de los datos y las características clave.


### Referencias
- Hieu T. Nguyen et al. "A large-scale benchmark dataset for computer-aided diagnosis in full-field digital mammography" – A preprint is available on medRxiv.


- Lin, Ting-Yu; Huang, Mei-Ling (2020), “Dataset of Breast mammography images with Masses”, Mendeley Data, V2, doi: 10.17632/ywsbh3ndr8.2



