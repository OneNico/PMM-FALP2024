import os
import pandas as pd

# Definir las rutas a las carpetas donde se encuentran los datasets
RUTA_VINDR = '/Volumes/m2/Memoria/Code/PMM/Dataset/Vindrmammo'
RUTA_VINCOMPRIMIDO = '/Volumes/m2/Memoria/Code/PMM/Data Preprocessing/Mini data/Vincomprimido'
RUTA_VINCOMPRIMIDOPNG = '/Volumes/m2/Memoria/Code/PMM/Data Preprocessing/Mini data/Vincomprimidopng'


# Cargar archivos CSV del dataset Vindr
breast_level_annotations = pd.read_csv(os.path.join(RUTA_VINDR, 'breast-level_annotations.csv'))
finding_annotations = pd.read_csv(os.path.join(RUTA_VINDR, 'finding_annotations.csv'))
metadata = pd.read_csv(os.path.join(RUTA_VINDR, 'metadata.csv'))

# Cargar un archivo CSV del dataset Vincomprimido
metadatacomprimida = pd.read_csv(os.path.join('/Volumes/m2/Memoria/Code/PMM/Dataset', 'metacomprimida.csv'))

# Cargar las imágenes de Vindr
RUTA_IMAGENES_VINDR = os.path.join(RUTA_VINDR, 'images')
lista_imagenes_vindr = os.listdir(RUTA_IMAGENES_VINDR)

# Cargar las imágenes de Vincomprimido
lista_imagenes_vincomprimido = os.listdir(RUTA_VINCOMPRIMIDO)

# Cargar las imágenes de Vincomprimidopng
lista_imagenes_vincomprimidopng = os.listdir(RUTA_VINCOMPRIMIDOPNG)

def mostrar_primera_fila(dataframe, nombre):
    """Muestra las primeras filas de un DataFrame con un nombre específico."""
    print(f"\n{nombre}:")
    print(dataframe.head())


def contar_archivos_por_subcarpeta(ruta_imagenes):
    """Cuenta los archivos en cada subcarpeta dentro de la ruta especificada."""
    lista_subcarpetas = os.listdir(ruta_imagenes)
    conteo_archivos = {}

    for subcarpeta in lista_subcarpetas:
        ruta_subcarpeta = os.path.join(ruta_imagenes, subcarpeta)
        if os.path.isdir(ruta_subcarpeta):  # Asegurarse de que es una carpeta
            archivos = os.listdir(ruta_subcarpeta)
            conteo_archivos[subcarpeta] = len(archivos)

    return lista_subcarpetas, conteo_archivos