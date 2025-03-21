import os
import streamlit as st
from google.cloud import translate_v3beta1 as translate
from PyPDF2 import PdfReader, PdfWriter
from datetime import datetime

st.set_page_config(page_title="Traductor de documentos escaneados", page_icon="resources/valle_del_miro.ico")
st.title(" 🉑 Traductor de documentos escaneados🉑")

JSON = "C:/Users/iker/Documents/kinetic-fire-454010-r2-3b7f6884a8d9.json"  # Clave API Google Cloud
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = JSON

LANGUAGES = {"Español": "es", "Inglés": "en", "Chino": "zh-CN", "Alemán": "de"}  # Diccionario de idiomas

TEMP_FOLDER = "temp_files" # Crear un carpeta temporal para guardar en memoria el input y el output de los documentos
os.makedirs(TEMP_FOLDER, exist_ok=True)

MAX_PAGES = int(os.getenv("MAX_PAGES", 10)) # Limitar documentos PDF de 10 paginas

col1, col2 = st.columns(2)
with col1:
    source_lang = st.selectbox("Idioma de origen", options=list(LANGUAGES.keys()), index=0)
with col2:
    available_target_langs = [lang for lang in LANGUAGES.keys() if lang != source_lang]
    target_lang = st.selectbox("Idioma a traducir", options=available_target_langs, index=0)

def limit_pages_pdf(input_path, output_path):
    reader = PdfReader(input_path)
    writer = PdfWriter()

    num_pages = min(len(reader.pages), MAX_PAGES)

    for i in range(num_pages):
        writer.add_page(reader.pages[i])

    with open(output_path, "wb") as f:
        writer.write(f)

    return output_path

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

uploaded_file = st.file_uploader(" ↖️ Sube un PDF escaneado (Máx. 10 páginas)", type=["pdf"])

if uploaded_file:
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    input_path = os.path.join(TEMP_FOLDER, f"{timestamp}_input.pdf")
    limited_path = os.path.join(TEMP_FOLDER, f"{timestamp}_limited.pdf")

    with open(input_path, "wb") as f:
        f.write(uploaded_file.getbuffer())

    reader = PdfReader(input_path)
    total_pages = len(reader.pages)

    if total_pages > MAX_PAGES:
        st.error(f"🚫 El documento tiene {total_pages} páginas. Solo se permiten documentos de {MAX_PAGES} páginas o menos.")
        st.stop()

    limit_pages_pdf(input_path, limited_path)

    source_lang_code = LANGUAGES[source_lang]
    target_lang_code = LANGUAGES[target_lang]

    # Obtener el nombre original del archivo sin la extensión
    original_filename = os.path.splitext(uploaded_file.name)[0]
    output_filename = f"{timestamp}_{original_filename}_{target_lang_code}.pdf"
    output_path = os.path.join(TEMP_FOLDER, output_filename)

    # Botón para controlar la traducción
    if st.button("Traducir documento"):
        with st.spinner(" ⌛ Traduciendo documento..."):
            translated_pdf = translate_pdf(limited_path, output_path, source_lang_code, target_lang_code)

        st.success(" ✅ PDF traducido creado con éxito.")
        with open(translated_pdf, "rb") as f:
            st.download_button(" ⬇️ Descargar PDF traducido", f, file_name=output_filename)
