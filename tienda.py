import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from utils import inicializar_firebase
from auth import mostrar_login
from navigation import mostrar_menu
from inventario import mostrar_inventario
from proforma import generar_proforma
from reporte import mostrar_reporte

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

if st.session_state.pagina == "Inventario":
    mostrar_inventario(db)

if st.session_state.pagina == "Proforma":
    generar_proforma(db)

if st.session_state.pagina == "Reporte":
    mostrar_reporte(db)