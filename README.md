# Clasificación de Imágenes de Mamografía Usando Deep Learning

Este repositorio contiene el desarrollo de la aplicación **Smart Mammo**, creada como parte del desafío tecnológico "Clasificación de imágenes de mamografía usando Machine Learning" en el programa de memorias multidisciplinarias de la Universidad Técnica Federico Santa María en colaboración con la Fundación Arturo López Pérez (FALP).

## Contexto del Desafío

El proyecto tiene como objetivo crear un sistema automatizado que permita detectar tumores o tejidos cancerosos en imágenes de mamografía utilizando técnicas de Machine Learning y Deep Learning. Esto es crucial para mejorar la detección temprana del cáncer de mama, especialmente en campañas de detección masiva, donde el volumen de imágenes puede sobrecargar a los profesionales de la salud. La automatización de este proceso permite priorizar a los pacientes que requieren atención inmediata, optimizando así el uso de los recursos médicos.

Smart Mammo integra modelos de clasificación para identificar áreas sospechosas en mamografías, clasificándolas según su probabilidad de malignidad. Además, el sistema permite visualizar los resultados, generar reportes y realizar la inferencia sobre grandes volúmenes de imágenes de manera eficiente.

---

## Estructura del Repositorio

Este repositorio se organiza en las siguientes carpetas principales:

### 1. **App SmartMammo**
   - **Descripción**: Contiene los archivos necesarios para la implementación de la interfaz de usuario de la aplicación Smart Mammo, desarrollada en Streamlit.
   - **Contenido**:
     - `src`: Carpeta principal del código de la aplicación, organizada en dos subcarpetas:
       - `modulos`: Incluye los módulos específicos para la clasificación, procesamiento y generación de reportes de las imágenes.
       - `ui`: Contiene los componentes de la interfaz de usuario, como el diseño de la barra lateral y los estilos de la app.
     - `app.py`: Archivo principal para ejecutar la aplicación.
     - `requirements.txt`: Lista de dependencias necesarias para el funcionamiento de la aplicación.
   - **Propósito**: Facilitar la interacción con el sistema a través de una interfaz intuitiva, permitiendo la carga, visualización, clasificación y reporte de mamografías.

### 2. **Data Processing**
   - **Descripción**: Incluye scripts y archivos para el preprocesamiento de datos, esenciales para asegurar la calidad de las imágenes y los metadatos antes de entrenar o validar el modelo.
   - **Contenido**:
     - `BeningMalignant_Masses-Preprocessing`: Scripts y configuraciones específicas para preprocesar datos de masas benignas y malignas.
     - `VinDr-Mammo-Preprocessing`: Scripts para el procesamiento del dataset VinDr-Mammo.
   - **Propósito**: Preparar los datos en formato adecuado para el entrenamiento y la inferencia, asegurando consistencia y calidad en el conjunto de datos.

### 3. **Evaluation and Testing**
   - **Descripción**: Contiene notebooks dedicados a la evaluación y prueba del modelo entrenado, verificando su precisión y sensibilidad en diferentes conjuntos de datos.
   - **Propósito**: Validar el rendimiento del modelo para asegurar su fiabilidad antes de integrarlo en la aplicación.

### 4. **Exploratory Data Analysis**
   - **Descripción**: Esta carpeta contiene notebooks y scripts para el análisis exploratorio de los datos, permitiendo una comprensión profunda de las características del dataset.
   - **Propósito**: Identificar patrones y particularidades en los datos, como distribuciones y relaciones, que pueden influir en el rendimiento del modelo.

### 5. **Model Training and Validation**
   - **Descripción**: Almacena los scripts y notebooks utilizados para el entrenamiento y validación de los modelos de clasificación de mamografías.
   - **Propósito**: Permitir el entrenamiento de modelos de Deep Learning que puedan clasificar imágenes de mamografía en categorías de malignidad, optimizando los parámetros para obtener un alto rendimiento en el reconocimiento de tejidos sospechosos.

### 6. **Protótipo App**
   - **Descripción**: Incluye archivos y configuraciones del prototipo inicial de la aplicación Smart Mammo.
   - **Propósito**: Proveer una base para el desarrollo de la aplicación final, con pruebas iniciales de funcionalidad y diseño que luego se refinan en la implementación final.



