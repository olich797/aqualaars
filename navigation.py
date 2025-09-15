# navigation.py
import streamlit as st

def mostrar_menu():
    st.title("🏠 Aqualaars")
    st.write("Selecciona a qué sección quieres ir:")
    col1, col2, col3 = st.columns(3)

    with col1:
        if st.button("📦 Inventario"):
            st.session_state.pagina = "Inventario"
    with col2:
        if st.button("📦 Proforma"):
            st.session_state.pagina = "Proforma"
    with col3:
        if st.button("📊 Reporte Proformas"):
            st.session_state.pagina = "Reporte"