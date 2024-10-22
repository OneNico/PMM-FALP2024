# src/procesamiento/transformaciones.py

import albumentations as A
import numpy as np

def construir_pipeline_transformaciones(opciones):
    """
    Construye el pipeline de transformaciones basado en las opciones seleccionadas.

    :param opciones: Diccionario de opciones de transformación.
    :return: Pipeline de transformaciones de Albumentations.
    """
    transformaciones = []

    # Rotación Aleatoria eliminada
    # if opciones.get('rotar', False):
    #     transformaciones.append(A.Rotate(limit=45, p=1.0))

    if opciones.get('voltear_horizontal', False):
        transformaciones.append(A.HorizontalFlip(p=1.0))

    if opciones.get('voltear_vertical', False):
        transformaciones.append(A.VerticalFlip(p=1.0))

    if opciones.get('brillo_contraste', False):
        transformaciones.append(A.RandomBrightnessContrast(p=1.0))

    if opciones.get('ruido_gaussiano', False):
        # Aumentar var_limit para hacer el ruido más visible
        transformaciones.append(A.GaussNoise(var_limit=(20.0, 80.0), p=1.0))

    # Filtro de Enfoque eliminado
    # if opciones.get('enfoque', False):
    #     transformaciones.append(A.Sharpen(p=1.0))

    if opciones.get('recorte_redimension', False):
        transformaciones.append(A.RandomResizedCrop(
            height=224, width=224, scale=(0.8, 1.0), ratio=(0.9, 1.1), p=1.0))

    if opciones.get('desenfoque', False):
        # Aumentar blur_limit para hacer el desenfoque más notable
        transformaciones.append(A.Blur(blur_limit=7, p=1.0))

    # Si no se seleccionó ninguna transformación, aplicar una transformación que no hace nada
    if not transformaciones:
        transformaciones.append(A.NoOp())

    pipeline = A.Compose(transformaciones)

    return pipeline

def aplicar_transformaciones(data, opciones):
    """
    Aplica transformaciones a la imagen utilizando Albumentations.

    :param data: Datos de la imagen como un array de NumPy.
    :param opciones: Diccionario de opciones de transformación.
    :return: Datos de imagen transformados.
    """
    # Construir el pipeline de transformaciones basado en las opciones
    augmentation_pipeline = construir_pipeline_transformaciones(opciones)

    # Convertir data a uint8 y expandir dimensiones si es necesario
    image = (data * 255).astype(np.uint8)

    # Si la imagen es en escala de grises, agregar una dimensión de canal
    if len(image.shape) == 2:
        image = np.expand_dims(image, axis=2)

    # Aplicar el pipeline de augmentación
    augmented = augmentation_pipeline(image=image)
    image_augmented = augmented['image']

    # Si la imagen sigue teniendo un solo canal, volver a reducir la dimensión
    if image_augmented.shape[2] == 1:
        image_augmented = np.squeeze(image_augmented, axis=2)

    # Convertir de vuelta a float para consistencia
    image_augmented = image_augmented.astype(np.float32) / 255.0

    return image_augmented
