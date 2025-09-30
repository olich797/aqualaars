# navigation.py
import streamlit as st

if "rol" not in st.session_state or st.session_state.rol not in ["admin", "user"]:
    st.warning("⚠️ No tienes permisos para acceder a esta sección.")
    st.stop()

def mostrar_menu():
    st.title("Aqualaars")
    st.write("Selecciona a qué sección quieres ir:")
    col1, col2, col3, col4, col5 = st.columns(5)

    with col1:
        if st.button("📦 Inventario"):
            st.session_state.pagina = "Inventario"
    with col2:
        if st.button("🧾 Proforma"):
            st.session_state.pagina = "Proforma"
    with col3:
        if st.button("📊 Reporte Proformas"):
            st.session_state.pagina = "Reporte"
    with col4:
        if st.button("🛒 Venta"):
            st.session_state.pagina = "Venta"
    with col5:
        if st.button("📈 Reporte Ventas"):
            st.session_state.pagina = "Reporte Ventas"