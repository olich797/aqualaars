# ventas.py
import streamlit as st
import pandas as pd
from datetime import datetime

def registrar_venta(db):
    if "rol" not in st.session_state or st.session_state.rol not in ["admin", "user"]:
        st.warning("⚠️ No tienes permisos para acceder a esta sección.")
        st.stop()
    st.header("🛒 Registrar Venta")

    nombre_cliente = st.text_input("Nombre del Cliente")
    ci_nit = st.text_input("CI o NIT")
    fecha_venta = st.date_input("Fecha de la venta", value=datetime.today())

    if "productos_venta" not in st.session_state:
        st.session_state.productos_venta = []

    # 🔍 Selección desde inventario
    productos_db = list(db.collection("inventario").stream())
    nombres_productos = [p.to_dict()["nombre"] for p in productos_db]

    st.subheader("📦 Seleccionar Producto del Inventario")
    producto_seleccionado = st.selectbox("Producto", [""] + nombres_productos)

    producto_info = next((p for p in productos_db if p.to_dict()["nombre"] == producto_seleccionado), None)
    cantidad_disponible = producto_info.to_dict()["cantidad"] if producto_info else 0
    precio_unitario = producto_info.to_dict()["precio_bs"] if producto_info else 0

    if cantidad_disponible >= 1:
        cantidad_venta = st.number_input("Cantidad a vender", min_value=1, max_value=cantidad_disponible, step=1)
    else:
        st.warning(f"⚠️ No hay stock disponible para '{producto_seleccionado}'.")
        cantidad_venta = None

    if st.button("Agregar al carrito desde inventario"):
        if producto_seleccionado and cantidad_venta:
            st.session_state.productos_venta.append({
                "ID": producto_info.id,
                "Nombre": producto_seleccionado,
                "Cantidad": cantidad_venta,
                "Precio Unitario BOB": precio_unitario,
                "Precio Total BOB": round(precio_unitario * cantidad_venta, 2),
                "manual": False
            })
            st.success(f"Producto '{producto_seleccionado}' agregado a la venta.")

    # ✍️ Ingreso manual de productos
    st.subheader("✏️ Agregar Producto Manualmente")
    nombre_manual = st.text_input("Nombre del producto manual")
    cantidad_manual = st.number_input("Cantidad", min_value=1, step=1, key="cantidad_manual")
    precio_manual = st.number_input("Precio Unitario BOB", min_value=0.01, step=0.01, key="precio_manual")
    precio_total_manual = round(cantidad_manual * precio_manual, 2)

    if st.button("Agregar producto manual"):
        if nombre_manual:
            st.session_state.productos_venta.append({
                "ID": None,
                "Nombre": nombre_manual,
                "Cantidad": cantidad_manual,
                "Precio Unitario BOB": precio_manual,
                "Precio Total BOB": precio_total_manual,
                "manual": True
            })
            st.success(f"Producto manual '{nombre_manual}' agregado a la venta.")

    # 🧾 Mostrar productos agregados con edición y eliminación
    if st.session_state.productos_venta:
        st.subheader("🧺 Productos en la Venta")

        nueva_lista = []
        for i, item in enumerate(st.session_state.productos_venta):
            col1, col2, col3, col4, col5 = st.columns([2.5, 0.8, 1.1, 1.1, 1.1])

            with col1:
                st.write(item["Nombre"])

            with col2:
                cantidad_editada = st.number_input(
                    "", min_value=1, step=1, value=int(item["Cantidad"]),
                    key=f"cantidad_{i}", label_visibility="collapsed"
                )

            with col3:
                precio_editado = st.number_input(
                    "", min_value=0.01, step=0.01, value=float(item["Precio Unitario BOB"]),
                    key=f"precio_{i}", label_visibility="collapsed"
                )

            precio_total = round(cantidad_editada * precio_editado, 2)

            with col4:
                if st.button("Guardar", key=f"guardar_{i}"):
                    item["Cantidad"] = cantidad_editada
                    item["Precio Unitario BOB"] = precio_editado
                    item["Precio Total BOB"] = precio_total
                    st.success(f"✅ Producto '{item['Nombre']}' actualizado.")

            with col5:
                eliminar = st.button("Eliminar", key=f"eliminar_{i}")
                if eliminar:
                    st.success(f"🗑 Producto '{item['Nombre']}' eliminado.")
                    continue  # No lo agregamos a la nueva lista

            nueva_lista.append(item)

        st.session_state.productos_venta = nueva_lista

        total_venta = sum([item["Precio Total BOB"] for item in st.session_state.productos_venta])
        st.write(f"**Total de la venta:** {round(total_venta, 2)} BOB")

        if st.button("💾 Registrar Venta"):
            venta_id = f"venta_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            venta_data = {
                "nombre_cliente": nombre_cliente,
                "ci_nit": ci_nit,
                "fecha_venta": fecha_venta.strftime("%Y-%m-%d"),
                "productos": st.session_state.productos_venta,
                "total": round(total_venta, 2)
            }

            db.collection("ventas").document(venta_id).set(venta_data)

            for item in st.session_state.productos_venta:
                if not item.get("manual") and item["ID"]:
                    producto_ref = db.collection("inventario").document(item["ID"])
                    producto_actual = producto_ref.get().to_dict()
                    nueva_cantidad = producto_actual["cantidad"] - item["Cantidad"]
                    producto_ref.update({"cantidad": nueva_cantidad})

            st.success(f"✅ Venta registrada con ID: {venta_id}")
            st.session_state.productos_venta = []

    if st.button("🔙 Volver al inicio"):
        st.session_state.pagina = "Inicio"