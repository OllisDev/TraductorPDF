import os
import streamlit as st
from google.cloud import translate_v3beta1 as translate

st.set_page_config(page_title="Traductor de documentos escaneados", page_icon="resources/valle_del_miro.ico")
st.title(" 🉑 Traductor de documentos escaneados🉑")

JSON = "C:/Users/iker/Documents/kinetic-fire-454010-r2-3b7f6884a8d9.json" # Clave API Google Cloud 
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = JSON

LANGUAGES = {"Español": "es", "Inglés": "en", "Chino": "zh-CN"} # Diccionario de clave-valor para almacenar los idiomas disponibles para traducir


col1, col2 = st.columns(2) # Desplegables para cambiar el idioma de origen y el idioma a traducir a la hora de traducir el documento
with col1:
    source_lang = st.selectbox("Idioma de origen", options=list(LANGUAGES.keys()), index=0)
with col2:
    target_lang = st.selectbox("Idioma a traducir", options=[lang for lang in LANGUAGES.keys() if lang != source_lang], index=0)

def translate_pdf(input_path, output_path, source_language, target_language):
    """Traduce un documento PDF usando Google Cloud Translation API"""
    client = translate.TranslationServiceClient()
    parent = "projects/kinetic-fire-454010-r2/locations/global"
    mime_type = "application/pdf"
    
    with open(input_path, "rb") as document_file:
        document_content = document_file.read()

    document = translate.types.DocumentInputConfig(
        content=document_content,
        mime_type=mime_type,
    )

    # Llamada a la API de Google Cloud
    response = client.translate_document(
        request={
            "parent": parent,
            "document_input_config": document,
            "source_language_code": source_language,
            "target_language_code": target_language,
        }
    )

    with open(output_path, "wb") as output_file:
        output_file.write(response.document_translation.byte_stream_outputs[0])

    return output_path

uploaded_file = st.file_uploader(" ↖️ Sube un PDF escaneado", type=["pdf"])

if uploaded_file:
    input_path = "input.pdf"
    output_path = "translated.pdf"
    
    with open(input_path, "wb") as f:
        f.write(uploaded_file.getbuffer())
    
    source_lang_code = LANGUAGES[source_lang]
    target_lang_code = LANGUAGES[target_lang]
    
    with st.spinner(" ⌛ Traduciendo documento..."):
        translated_pdf = translate_pdf(input_path, output_path, source_lang_code, target_lang_code)

    st.success(" ✅ PDF traducido creado con éxito.")
    with open(translated_pdf, "rb") as f:
        st.download_button(" ⬇️ Descargar PDF traducido", f, file_name="PDF_traducido.pdf")
