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
        Realiza la detección de objetos en una imagen PIL y devuelve la imagen con detecciones superpuestas.
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

            # Crear una máscara vacía con las mismas dimensiones que la imagen original
            logger.info("Creando la máscara de detecciones.")
            mask = Image.new('L', image_pil.size, 0)  # 'L' para modo de imagen en escala de grises

            # Dibujar las cajas delimitadoras en la máscara
            draw = ImageDraw.Draw(mask)

            # Convertir las cajas a un array de NumPy
            boxes_array = boxes.xyxy.cpu().numpy()  # Convertir a CPU y luego a NumPy

            for box in boxes_array:
                # Obtener las coordenadas de la caja y asegurarse de que son enteros
                x1, y1, x2, y2 = map(int, box[:4])
                # Dibujar un rectángulo lleno (valor 255) en la máscara
                draw.rectangle([x1, y1, x2, y2], outline=255, fill=255)

            # Superponer la máscara coloreada sobre la imagen original
            logger.info("Superponiendo la máscara de detecciones sobre la imagen original.")
            # Convertir la imagen original a modo RGBA
            image_rgba = image_rgb.convert('RGBA')

            # Crear una imagen del color de la máscara (por ejemplo, rojo semitransparente)
            mask_color = (255, 0, 0, 100)  # (R, G, B, Alpha)

            # Crear una imagen del color de la máscara con transparencia
            colored_mask = Image.new('RGBA', image_pil.size, mask_color)

            # Usar la máscara como canal alfa
            mask_np = np.array(mask)
            alpha_mask = (mask_np / 255) * mask_color[3]  # Escalar el valor de alfa según la máscara

            # Reemplazar el canal alfa en la máscara coloreada
            colored_mask.putalpha(Image.fromarray(alpha_mask.astype('uint8')))

            # Superponer la máscara coloreada sobre la imagen original
            combined = Image.alpha_composite(image_rgba, colored_mask)

            # Convertir de vuelta a RGB si es necesario
            result_image = combined.convert('RGB')

            logger.info("Detecciones superpuestas exitosamente.")
            return result_image

        except Exception as e:
            logger.error(f"Error durante la detección de objetos: {e}")
            return image_pil
