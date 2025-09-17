import streamlit as st
from utils import inicializar_firebase
from auth import mostrar_login
from navigation import mostrar_menu
from inventario import mostrar_inventario
from proforma import generar_proforma
from reporte import mostrar_reporte
from inventario import mostrar_inventario, mostrar_busqueda_inicial
from ventas import registrar_venta
from reporte_ventas import mostrar_reporte_ventas

db = inicializar_firebase(st.secrets["firebase"])

if "autenticado" not in st.session_state:
    st.session_state.autenticado = False

if not st.session_state.autenticado:
    if mostrar_login():
        st.stop()

if "pagina" not in st.session_state:
    st.session_state.pagina = "Inicio"

if st.session_state.pagina == "Inicio":
    mostrar_menu()
    mostrar_busqueda_inicial(db)


if st.session_state.pagina == "Inventario":
    mostrar_inventario(db)

if st.session_state.pagina == "Proforma":
    generar_proforma(db)

if st.session_state.pagina == "Reporte":
    mostrar_reporte(db)
    
if st.session_state.pagina == "Venta":
    registrar_venta(db)

if st.session_state.pagina == "Reporte Ventas":
    mostrar_reporte_ventas(db)
