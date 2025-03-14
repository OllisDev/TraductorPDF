import streamlit as st
import pandas as pd

st.title("Traductor de documentos en Chino")
uploaded_file = st.file_uploader("Sube un archivo PDF", type=["pdf"])
if uploaded_file is not None:
    st.success("¡Archivo subido correctamente!")
    st.write(f"Nombre del archivo: {uploaded_file.name}")
    st.write(f"Tamaño: {(uploaded_file.size /1028)} Kb")

    if st.button("Procesar PDF"):
        st.write("Aquí podrías mostrar el texto extraído o generar un nuevo archivo.")

    # Agregar botones y opciones adicionales
    if st.button("Descargar PDF modificado"):
        st.write("Aquí podrías generar un link para la descarga.")
