# src/utilidades/manejo_archivos.py

import uuid

def generar_nombre_unico(nombre_original):
    """
    Genera un nombre de archivo único basado en UUID y mantiene la extensión original.

    :param nombre_original: Nombre original del archivo.
    :return: Nuevo nombre de archivo único.
    """
    ext = nombre_original.split('.')[-1]
    unique_id = uuid.uuid4().hex
    nuevo_nombre = f"{unique_id}.{ext}"
    return nuevo_nombre
