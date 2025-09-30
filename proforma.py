# proforma.py
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import io
from datetime import datetime, timedelta

def generar_proforma(db):
    if "rol" not in st.session_state or st.session_state.rol not in ["admin", "user"]:
        st.warning("⚠️ No tienes permisos para acceder a esta sección.")
        st.stop()
    st.header("📝 Generar Proforma")

    nombre_cliente = st.text_input("Nombre del Cliente")
    ci_nit = st.text_input("CI o NIT")
    fecha_actual = st.date_input("Fecha de emisión", value=datetime.today())
    fecha_vencimiento = st.date_input("Fecha de vencimiento", value=datetime.today() + timedelta(days=30))

    if "productos_lista" not in st.session_state:
        st.session_state.productos_lista = []

    productos_db = list(db.collection("inventario").stream())  
    nombres_productos = [producto.to_dict()["nombre"] for producto in productos_db]

    st.subheader("Seleccionar Producto del Inventario")
    producto_inventario = st.selectbox("Selecciona un producto", [""] + nombres_productos)
    producto_encontrado = next((p.to_dict() for p in productos_db if p.to_dict()["nombre"] == producto_inventario), None)
    precio_unitario_inventario = round(producto_encontrado["precio_bs"], 2) if producto_encontrado else 0
    cantidad_inventario = st.number_input("Cantidad", min_value=1, step=1, key="cantidad_inventario")
    precio_total_inventario = round(cantidad_inventario * precio_unitario_inventario, 2)

    if st.button("Agregar desde Inventario"):
        if producto_inventario:
            st.session_state.productos_lista.append({
                "Nombre": producto_inventario,
                "Cantidad": cantidad_inventario,
                "Precio Unitario BOB": precio_unitario_inventario,
                "Precio Total BOB": precio_total_inventario
            })
            st.success(f"Producto '{producto_inventario}' agregado correctamente.")

    st.subheader("Agregar Producto Manualmente")
    producto_manual = st.text_input("Nombre del producto")
    cantidad_manual = st.number_input("Cantidad", min_value=1, step=1, key="cantidad_manual")
    precio_unitario_manual = st.number_input("Precio Unitario BOB", min_value=0.01, step=0.01, key="precio_manual")
    precio_total_manual = round(cantidad_manual * precio_unitario_manual, 2)

    if st.button("Agregar Producto Manual"):
        if producto_manual:
            st.session_state.productos_lista.append({
                "Nombre": producto_manual,
                "Cantidad": cantidad_manual,
                "Precio Unitario BOB": precio_unitario_manual,
                "Precio Total BOB": precio_total_manual
            })
            st.success(f"Producto '{producto_manual}' agregado correctamente.")

    if st.session_state.productos_lista:
        st.subheader("Lista de Productos en la Proforma")
        col1, col2, col3, col4 = st.columns([2.5, 0.6, 1.1, 0.9])
        with col1: st.markdown("**Producto**")
        with col2: st.markdown("**Cantidad**")
        with col3: st.markdown("**Precio Unitario BOB**")
        with col4: st.markdown("**Eliminar**")

        nueva_lista = []
        for i, item in enumerate(st.session_state.productos_lista):
            col1, col2, col3, col4 = st.columns([2.5, 0.6, 1.1, 0.9])
            with col1: st.write(item["Nombre"])
            with col2:
                item["Cantidad"] = st.number_input("", min_value=1, step=1, value=int(item["Cantidad"]), key=f"cantidad_{i}", label_visibility="collapsed")
            with col3:
                precio_unitario = float(item.get("Precio Unitario BOB", 0.0))
                item["Precio Unitario BOB"] = st.number_input("", min_value=0.01, step=0.01, value=precio_unitario, key=f"precio_bs_{i}", label_visibility="collapsed")
            item["Precio Total BOB"] = round(item["Cantidad"] * item["Precio Unitario BOB"], 2)
            with col4:
                eliminar = st.button(f"Eliminar", key=f"eliminar_{i}")
            if not eliminar:
                nueva_lista.append(item)
            else:
                st.success(f"Producto '{item['Nombre']}' eliminado correctamente.")

        st.session_state.productos_lista = nueva_lista
        total_proforma = sum([item["Precio Total BOB"] for item in st.session_state.productos_lista])
        st.write(f"**Total en BOB:** {round(total_proforma, 2)} BOB")

        if st.button("📥 Guardar Proforma en la Base de Datos"):
            proforma_id = f"proforma_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            proforma_data = {
                "nombre_cliente": nombre_cliente,
                "ci_nit": ci_nit,
                "fecha_emision": fecha_actual.strftime("%Y-%m-%d"),
                "fecha_vencimiento": fecha_vencimiento.strftime("%Y-%m-%d"),
                "productos": st.session_state.productos_lista,
                "total": round(total_proforma, 2)
            }
            db.collection("proformas").document(proforma_id).set(proforma_data)
            st.success(f"✅ La proforma ha sido guardada en Firebase con ID: {proforma_id}")

            fig, ax = plt.subplots(figsize=(10, 6))
            ax.set_title("Proforma", fontsize=24, fontweight="bold")
            ax.text(0.5, 0.5, "Aqualaars", font="Arial", fontweight="bold", fontsize=90, color="#00BFFF", alpha=0.2, ha="center", va="center", transform=ax.transAxes)
            ax.text(0.64, 0.36, "Todo para su piscina", font="Arial",fontweight="bold" , fontsize=30, color="#00BFFF",alpha=0.2, ha="center", va="center", transform=ax.transAxes)
            ax.text(0, 0.85, f"Nombre: {nombre_cliente}         CI/NIT: {ci_nit}", fontsize=12)
            ax.text(0, 0.78, f"Fecha emisión: {fecha_actual}", fontsize=12)
            ax.text(0, 0.71, f"Fecha vencimiento: {fecha_vencimiento}", fontsize=12)

            col_labels = ["Producto", "Cantidad", "Precio Unitario BOB", "Precio Total BOB"]
            table_data = [[item["Nombre"], item["Cantidad"], item["Precio Unitario BOB"], item["Precio Total BOB"]] for item in st.session_state.productos_lista]
            tabla = ax.table(cellText=table_data, colLabels=col_labels, cellLoc="center", loc="center", colWidths=[0.50, 0.13, 0.18, 0.18])
            tabla.auto_set_font_size(False)
            tabla.set_fontsize(10)
            tabla.scale(1.2, 1.2)
            ax.text(0, -0.02, f"Total: {round(total_proforma, 2)} BOB", fontsize=14, fontweight="bold")
            ax.axis("off")
            st.pyplot(fig)

            buffer = io.BytesIO()
            plt.savefig(buffer, format="pdf", bbox_inches="tight")
            buffer.seek(0)

            st.download_button(label="📥 Descargar Proforma", data=buffer, file_name="proforma.pdf", mime="application/pdf")
    else:
        st.warning("No se han agregado productos a la proforma.")

    if st.button("🆕 Nueva Proforma"):
        st.session_state.nombre_cliente = ""
        st.session_state.ci_nit = ""
        st.session_state.fecha_actual = datetime.today()
        st.session_state.fecha_vencimiento = datetime.today() + timedelta(days=30)
        st.session_state.productos_lista = []

    if st.button("🔙 Volver al inicio"):
        st.session_state.pagina = "Inicio"