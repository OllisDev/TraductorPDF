from PyQt6.QtCore import QThread, pyqtSignal
from deep_translator import GoogleTranslator
from PIL import Image, ImageDraw, ImageFont
import pytesseract
import cv2
import numpy as np

# Configuración de Tesseract
pytesseract.pytesseract.tesseract_cmd = r'C:/Program Files/Tesseract-OCR/tesseract.exe'

class TranslationThread(QThread):
    # Declarar las señales
    finished = pyqtSignal(str)
    error = pyqtSignal(str)
    progress = pyqtSignal(int)

    def __init__(self, image_path, save_path):
        super().__init__()
        self.image_path = image_path
        self.save_path = save_path

    def run(self):
        try:
            # Cargar la imagen
            img = Image.open(self.image_path)
            img_gray = cv2.cvtColor(np.array(img), cv2.COLOR_RGB2GRAY)

            # Mejorar la calidad de la imagen para OCR
            img_gray = cv2.GaussianBlur(img_gray, (5, 5), 0)
            _, img_gray = cv2.threshold(img_gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

            # Extraer texto y sus coordenadas usando pytesseract
            data = pytesseract.image_to_data(img_gray, lang='spa', output_type=pytesseract.Output.DICT)

            # Traducir el texto en bloques completos
            translator = GoogleTranslator(source="auto", target="zh-CN")
            translated_texts = []
            total_text_blocks = len(data["text"])
            for i in range(total_text_blocks):
                text = data["text"][i]
                if text.strip():  # Solo procesar texto no vacío
                    translated_text = translator.translate(text)
                    translated_texts.append(translated_text)
                else:
                    translated_texts.append("")  # Texto vacío si no hay nada que traducir

                # Emitir progreso (aproximado)
                progress = int((i + 1) / total_text_blocks * 100)
                self.progress.emit(progress)

            # Dibujar el texto traducido en la imagen
            draw = ImageDraw.Draw(img)
            try:
                # Usar una fuente que soporte caracteres chinos
                font = ImageFont.truetype("msyh.ttc", 20)  # Fuente Microsoft YaHei (debe estar instalada)
            except IOError:
                self.error.emit("No se encontró la fuente para caracteres chinos.")
                return

            for i in range(len(data["text"])):
                if data["text"][i].strip():  # Solo procesar texto no vacío
                    x, y, w, h = data["left"][i], data["top"][i], data["width"][i], data["height"][i]
                    # Dibujar un fondo blanco para "borrar" el texto original
                    draw.rectangle([x, y, x + w, y + h], fill="white")
                    # Dibujar el texto traducido en la misma posición
                    if translated_texts[i]:  # Solo dibujar si el texto traducido no está vacío
                        draw.text((x, y), translated_texts[i], font=font, fill="black")

            # Guardar la imagen con el texto traducido
            if self.save_path:
                img.save(self.save_path, "JPEG")
                self.finished.emit(f"Imagen traducida guardada en {self.save_path}")
        except Exception as e:
            self.error.emit(f"Error durante la traducción: {str(e)}")
