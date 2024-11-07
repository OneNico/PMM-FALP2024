import logging
from PIL import Image, ImageDraw
from ultralytics import YOLO
import numpy as np
from huggingface_hub import hf_hub_download

logger = logging.getLogger(__name__)

class Detector:
    def __init__(self, model_name):
        try:
            logger.info("Descargando el modelo desde Hugging Face...")
            model_path = hf_hub_download(repo_id=model_name, filename="best.pt")
            logger.info("Modelo descargado exitosamente.")
            self.model = YOLO(model_path)
            logger.info("Modelo YOLO cargado exitosamente.")
        except Exception as e:
            logger.error(f"Error al cargar el modelo YOLO: {e}")
            self.model = None

    def detectar_objetos(self, image_pil):
        """
        Realiza la detección de objetos en una imagen PIL y devuelve la imagen con bounding boxes dibujadas.
        """
        if not self.model:
            logger.error("El modelo YOLO no está cargado.")
            return None

        try:
            # Convertir la imagen PIL a formato compatible con YOLO
            logger.info("Convirtiendo la imagen a RGB para la inferencia con YOLO.")
            image_rgb = image_pil.convert('RGB')

            # Realizar la inferencia utilizando el modelo YOLO
            logger.info("Realizando la inferencia con el modelo YOLO...")
            result = self.model.predict(image_rgb, conf=0.2, verbose=False, imgsz=1280)[0]
            logger.info("Inferencia completada.")

            # Obtener las cajas delimitadoras de las detecciones
            boxes = result.boxes

            if boxes is None or len(boxes) == 0:
                logger.info("No se encontraron detecciones en la imagen.")
                return image_pil  # Retornar la imagen original si no hay detecciones

            # Crear una copia de la imagen para dibujar las bounding boxes
            logger.info("Dibujando las bounding boxes sobre la imagen.")
            draw = ImageDraw.Draw(image_rgb)

            # Convertir las cajas a un array de NumPy
            boxes_array = boxes.xyxy.cpu().numpy()  # Convertir a CPU y luego a NumPy

            for box in boxes_array:
                # Obtener las coordenadas de la caja y asegurarse de que son enteros
                x1, y1, x2, y2 = map(int, box[:4])
                # Dibujar el rectángulo de la bounding box
                draw.rectangle([x1, y1, x2, y2], outline="red", width=5)

            logger.info("Bounding boxes dibujadas exitosamente.")
            return image_rgb

        except Exception as e:
            logger.error(f"Error durante la detección de objetos: {e}")
            return image_pil

