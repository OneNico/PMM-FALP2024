# PMM-FALP2024

**PMM-FALP2024** es un proyecto orientado a la detección y clasificación de lesiones en mamografías utilizando modelos de Deep Learning. El objetivo es desarrollar un sistema automatizado que permita identificar regiones sospechosas en las mamografías, para luego clasificarlas en tejido sano o sospechoso. El sistema utiliza un enfoque basado en Machine Learning con el fin de mejorar la precisión y eficiencia en el diagnóstico.

## Estructura del Proyecto

El proyecto está organizado en varias carpetas y archivos, cada una dedicada a diferentes aspectos del desarrollo y la validación del modelo:

### 1. **Evaluation and Testing** 
   - Esta carpeta está planificada para incluir scripts y notebooks utilizados para la evaluación del modelo entrenado. 
   
### 2. **Exploratory Data Analysis**
   - Contiene notebooks utilizados para realizar un análisis exploratorio de los datos. En esta etapa, se estudian los datos disponibles, las distribuciones y las características de las imágenes y los metadatos que formarán la base del entrenamiento.
   - Incluye visualizaciones de las mamografías y un análisis del dataset usado

### 3. **Model Training and Validation** 
   - Esta carpeta está destinada a contener los scripts y notebooks relacionados con el entrenamiento y validación del modelo de Deep Learning.
 

### 4. **VinDr-Mammo-Preprocessing**
   - Contiene scripts y notebooks que se encargan del preprocesamiento de las imágenes de mamografías. Este módulo convierte las imágenes en formato DICOM a PNG, recorta las regiones de interés (ROI) y aplica técnicas de normalización.
   - Herramientas utilizadas: `pydicom`, `OpenCV`, y `NumPy`.


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




## Licencia

Este proyecto está bajo la Licencia MIT. Para más detalles, consulta el archivo [LICENSE](LICENSE).

