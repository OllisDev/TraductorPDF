import fitz  # PyMuPDF
from PIL import Image
import os

def convert_pdf_to_images(pdf_path, output_folder="temp_images"):
    """
    Convierte un archivo PDF en imágenes JPG y las guarda en una carpeta.

    :param pdf_path: Ruta del archivo PDF de entrada.
    :param output_folder: Carpeta donde se guardarán las imágenes.
    :return: Lista de rutas de imágenes generadas.
    """
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    doc = fitz.open(pdf_path)
    image_paths = []

    for page_num in range(len(doc)):
        page = doc[page_num]
        pix = page.get_pixmap()
        img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
        image_path = os.path.join(output_folder, f"page_{page_num + 1}.jpg")
        img.save(image_path, "JPEG")
        image_paths.append(image_path)

    return image_paths
