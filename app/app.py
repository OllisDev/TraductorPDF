import os
import streamlit as st
from google.cloud import translate_v3beta1 as translate
from PyPDF2 import PdfReader
from datetime import datetime

st.set_page_config(page_title="Traductor de documentos escaneados", page_icon="resources/valle_del_miro.ico")
st.title(" 🉑 Traductor de documentos escaneados🉑")

JSON = "C:/Users/iker/Documents/kinetic-fire-454010-r2-3b7f6884a8d9.json"  # Clave API Google Cloud
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = JSON

LANGUAGES = {"Español": "es", "Inglés": "en", "Chino": "zh-CN", "Alemán": "de"}

TEMP_FOLDER = "temp_files"
os.makedirs(TEMP_FOLDER, exist_ok=True)

MAX_PAGES = int(os.getenv("MAX_PAGES", 10))

col1, col2 = st.columns(2)
with col1:
    source_lang = st.selectbox("Idioma de origen", options=list(LANGUAGES.keys()), index=0)
with col2:
    available_target_langs = [lang for lang in LANGUAGES.keys() if lang != source_lang]
    target_lang = st.selectbox("Idioma a traducir", options=available_target_langs, index=0)

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

uploaded_file = st.file_uploader(" ↖️ Sube un PDF escaneado (máx. 10 páginas)", type=["pdf"])

if uploaded_file:
    timestamp = datetime.now().strftime("%Y%m%d")
    original_filename = os.path.splitext(uploaded_file.name)[0]
    
    # Ahora el archivo de entrada también tiene timestamp
    input_filename = f"{timestamp}_{original_filename}_input.pdf"
    input_path = os.path.join(TEMP_FOLDER, input_filename)

    # Guardamos el archivo, reemplazando si ya existe
    with open(input_path, "wb") as f:
        f.write(uploaded_file.getbuffer())

    reader = PdfReader(input_path)
    total_pages = len(reader.pages)

    if total_pages > MAX_PAGES:
        st.error(f"🚫 El documento tiene {total_pages} páginas. Solo se permiten documentos de {MAX_PAGES} páginas o menos.")
        st.stop()

    source_lang_code = LANGUAGES[source_lang]
    target_lang_code = LANGUAGES[target_lang]

    output_filename = f"{timestamp}_{original_filename}_{target_lang_code}.pdf"
    output_path = os.path.join(TEMP_FOLDER, output_filename)

    if st.button("Traducir documento"):
        with st.spinner(" ⌛ Traduciendo documento..."):
            translated_pdf = translate_pdf(input_path, output_path, source_lang_code, target_lang_code)

        st.success(" ✅ PDF traducido creado con éxito.")
        with open(translated_pdf, "rb") as f:
            st.download_button(" ⬇️ Descargar PDF traducido", f, file_name=output_filename)
