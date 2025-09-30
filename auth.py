import streamlit as st

def mostrar_login(db):
    st.title("🔑 Iniciar Sesión")

    user = st.text_input("Correo electrónico:")
    password = st.text_input("Contraseña:", type="password")

    if st.button("Ingresar"):
        usuario_doc = db.collection("usuarios").document(user).get()

        if usuario_doc.exists:
            datos = usuario_doc.to_dict()
            if datos.get("password") == password:
                st.session_state.autenticado = True
                st.session_state.usuario = user
                st.session_state.rol = datos.get("rol", "sin_rol")
                st.success(f"Login exitoso. Rol asignado: {st.session_state.rol}")
            else:
                st.error("Contraseña incorrecta.")
        else:
            st.error("Usuario no registrado.")