import streamlit as st
import pandas as pd
import os
import zipfile
from pdf2image import convert_from_path
from io import  BytesIO

def pdf_to_images(pdf_file):
    images = convert_from_path(pdf_file)
    return images

def create_zip(images):
    zip_buffer = BytesIO()
    with zipfile.ZipFile(zip_buffer, "w") as zip_file:
        for i, img in enumerate(images):
            img_bytes = BytesIO()
            img.save(img_bytes, format = "JPEG")
            zip_file.writestr(f"page_{i+1}.jpg", img_bytes.getvalue())
    zip_buffer.seek(0)
    return zip_buffer

st.set_page_config(page_title= "Traductor de documentos en Chino", page_icon= "C:/hlocal/TraductorPDF/resources/logo_valle_del_miro.ico")
st.title("Traductor de documentos en Chino")
uploaded_file = st.file_uploader("Sube un archivo PDF", type=["pdf"])
if uploaded_file:
    with open("temp.pdf", "wb") as f:
        f.write(uploaded_file.getbuffer())
 
    st.success ("PDF cargado correctamente")

    if st.button("Convertir a imágenes"):
        images = pdf_to_images("temp.pdf")
        zip_buffer = create_zip(images)

        st.download_button(
            label = "Descargar ZIP",
            data = zip_buffer,
            file_name = "imagenes_pdf.zip",
            mime = "application/zip"
        )
