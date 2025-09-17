# ventas.py
import streamlit as st
import pandas as pd
from datetime import datetime

def registrar_venta(db):
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
        cantidad_venta = st.number_input(
            "Cantidad a vender",
            min_value=1,
            max_value=cantidad_disponible,
            step=1
        )
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

    # 🧾 Mostrar productos agregados
    if st.session_state.productos_venta:
        st.subheader("🧺 Productos en la Venta")

        columnas_visibles = ["Nombre", "Cantidad", "Precio Unitario BOB", "Precio Total BOB"]
        df = pd.DataFrame(st.session_state.productos_venta)[columnas_visibles]
        st.table(df)

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

            # 🔄 Actualizar inventario solo para productos no manuales
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