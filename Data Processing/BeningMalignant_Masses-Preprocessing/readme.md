# Dataset de Imágenes de Mamografías con Masas

## Descripción General
Este dataset contiene imágenes de mamografías con masas benignas y malignas. Las imágenes fueron extraídas de tres conjuntos de datos reconocidos de mamografías: **INbreast**, **MIAS** y **DDSM**. El dataset fue preprocesado y aumentado para incrementar el número de muestras, lo que lo hace adecuado para aplicaciones de aprendizaje profundo en la detección de cáncer de mama.

## Detalles del Dataset
- **Publicado**: 30 de junio de 2020
- **Versión**: 2
- **DOI**: [10.17632/ywsbh3ndr8.2](https://doi.org/10.17632/ywsbh3ndr8.2)
- **Contribuyentes**: Ting-Yu Lin, Mei-Ling Huang

### Conjuntos de Datos Fuente
- **INbreast**: Inicialmente contribuyó con 106 imágenes de masas.
- **MIAS**: Inicialmente contribuyó con 53 imágenes de masas.
- **DDSM**: Inicialmente contribuyó con 2188 imágenes de masas.

### Después de la Aumentación
- **INbreast**: 7632 imágenes.
- **MIAS**: 3816 imágenes.
- **DDSM**: 13128 imágenes.

### Procesamiento de Imágenes
- **Aumentación de Datos**: Se aplicaron técnicas como rotación, volteo y escalado para aumentar el tamaño del dataset.
- **Ecualización de Histograma Adaptativa Limitada por Contraste (CLAHE)**: Se utilizó esta técnica para mejorar el contraste de las imágenes, lo que permite una mejor visualización de las características relevantes.

### Formato de las Imágenes
Todas las imágenes fueron redimensionadas a **227x227 píxeles** para garantizar consistencia y facilitar su uso en modelos de aprendizaje automático.

### Tamaño Total del Dataset
Después del preprocesamiento y la aumentación, el dataset contiene un total de **24,576 imágenes**.


### Cita

Lin, Ting-Yu; Huang, Mei-Ling (2020), “Dataset of Breast mammography images with Masses”, Mendeley Data, V2, doi: [10.17632/ywsbh3ndr8.2](https://doi.org/10.17632/ywsbh3ndr8.2)


