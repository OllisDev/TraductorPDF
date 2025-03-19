import os
import streamlit as st
from google.cloud import translate_v3beta1 as translate

st.set_page_config(page_title="Traductor de documentos en Chino", page_icon="resources/valle_del_miro.ico")
st.title("Traductor de documentos en Chino")

JSON = "C:/Users/iker/Documents/kinetic-fire-454010-r2-3b7f6884a8d9.json"
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = JSON

def translate_pdf(input_path, output_path, target_language="zh-CN"):
    """Traduce un documento PDF usando Google Cloud Translation API"""
    client = translate.TranslationServiceClient()
    
    # Configurar la solicitud de traducción
    parent = "projects/kinetic-fire-454010-r2/locations/global"
    mime_type = "application/pdf"  # Tipo de archivo
    
    with open(input_path, "rb") as document_file:
        document_content = document_file.read()

    document = translate.types.DocumentInputConfig(
        content=document_content,
        mime_type=mime_type,
    )

    response = client.translate_document(
        request={
            "parent": parent,
            "document_input_config": document,
            "target_language_code": target_language,
        }
    )

    # Guardar el documento traducido
    with open(output_path, "wb") as output_file:
        output_file.write(response.document_translation.byte_stream_outputs[0])

    return output_path

uploaded_file = st.file_uploader("Sube un PDF escaneado", type=["pdf"])

if uploaded_file:
    input_path = "input.pdf"
    output_path = "translated.pdf"

    with open(input_path, "wb") as f:
        f.write(uploaded_file.getbuffer())

    with st.spinner("Traduciendo documento..."):
        translated_pdf = translate_pdf(input_path, output_path)

    st.success("PDF traducido creado con éxito.")
    with open(translated_pdf, "rb") as f:
        st.download_button("Descargar PDF traducido", f, file_name="PDF_traducido.pdf")