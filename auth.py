# auth.py
import streamlit as st

def mostrar_login():
    st.title("🔑 Iniciar Sesión")
    user = st.text_input("Usuario:")
    password = st.text_input("Contraseña:", type="password")

    if st.button("Ingresar"):
        if user == "admin" and password == "admin":
            st.session_state.autenticado = True
            st.success("Login exitoso. Bienvenido a la aplicación!")
        else:
            st.error("Usuario o contraseña incorrectos.")
        return False
    return True