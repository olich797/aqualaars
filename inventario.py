# inventario.py
import streamlit as st
import pandas as pd

def mostrar_inventario(db):
    st.header("📦 Inventario")

    # 🛠 Sidebar (Configuración)
    st.sidebar.header("⚙️ Configuración")

    tipo_cambio_doc = db.collection("configuracion").document("tipo_cambio").get()
    tipo_cambio_actual = tipo_cambio_doc.to_dict().get("valor", 6.96) if tipo_cambio_doc.exists else 6.96

    nuevo_tipo_cambio = st.sidebar.number_input("Tipo de cambio USD -> BOB", min_value=0.01, value=tipo_cambio_actual, step=0.01)

    if st.sidebar.button("Guardar tipo de cambio"):
        db.collection("configuracion").document("tipo_cambio").set({"valor": nuevo_tipo_cambio})
        st.sidebar.success("Tipo de cambio actualizado.")

    # 🔹 Agregar productos
    st.subheader("Agregar Producto")
    
    nombre = st.text_input("Nombre del producto")
    cantidad = st.number_input("Cantidad", min_value=1, step=1)
    precio_usd = st.number_input("Precio Unitario en USD", min_value=0.01, step=0.01)
    precio_bob = round(precio_usd * nuevo_tipo_cambio, 2)
    precio_bs = st.number_input("Precio Unitario en BS", min_value=0.01, step=0.01)
    
    if st.button("Agregar Producto"):
        db.collection("inventario").add({
            "nombre": nombre,
            "cantidad": cantidad,
            "precio_usd": precio_usd,
            "precio_bob": precio_bob,
            "precio_bs": precio_bs
        })
        st.success("Producto agregado correctamente")

    # 🔹 Mostrar, editar y eliminar productos
    st.subheader("📋 Inventario de Productos")

    busqueda = st.text_input("Buscar producto por nombre", key="busqueda_producto")
    productos = db.collection("inventario").stream()

    productos_lista = []
    for producto in productos:
        datos = producto.to_dict()
        doc_id = producto.id
        if busqueda.lower() in datos["nombre"].lower():
            productos_lista.append({
                "ID": doc_id,
                "Nombre": datos["nombre"],
                "Cantidad": datos["cantidad"],
                "Precio USD": round(datos["precio_usd"], 2),
                "Precio BOB": round(datos["precio_usd"] * nuevo_tipo_cambio, 2),
                "Precio BS": datos["precio_bs"]
            })

    if productos_lista:
        col1, col2, col3, col4, col5, col6, col7 = st.columns([2.5, 0.9, 0.8, 0.8, 0.8, 1.1, 1.1])
        with col1: st.write("Nombre")
        with col2: st.write("Cantidad")
        with col3: st.write("USD")
        with col4: st.write("BOB")
        with col5: st.write("BS")
        with col6: st.write("")
        with col7: st.write("")

        df = pd.DataFrame(productos_lista)

        for index, item in df.iterrows():
            col1, col2, col3, col4, col5, col6, col7 = st.columns([2.5, 0.9, 0.8, 0.8, 0.8, 1.1, 1.1])
            with col1: st.write(item["Nombre"])
            with col2:
                cantidad_editada = st.number_input("", min_value=1, step=1, value=item["Cantidad"], key=f"cantidad_{item['ID']}", label_visibility="collapsed")
            with col3:
                precio_editado = st.number_input("", min_value=0.01, step=0.01, value=item["Precio USD"], key=f"precio_{item['ID']}", label_visibility="collapsed")
            with col4: st.write(f"{item['Precio BOB']}")
            with col5:
                precio_editado_bs = st.number_input("", min_value=0.01, step=0.01, value=item["Precio BS"], key=f"precio_bs_{item['ID']}", label_visibility="collapsed")
            with col6:
                if st.button("Guardar", key=f"guardar_{item['ID']}"):
                    db.collection("inventario").document(item["ID"]).update({
                        "cantidad": cantidad_editada,
                        "precio_usd": precio_editado,
                        "precio_bob": round(precio_editado * nuevo_tipo_cambio, 2),
                        "precio_bs": precio_editado_bs
                    })
                    st.success(f"✅ Producto '{item['Nombre']}' actualizado.")
            with col7:
                if st.button("Eliminar", key=f"eliminar_{item['ID']}"):
                    db.collection("inventario").document(item["ID"]).delete()
                    st.success(f"🗑 Producto '{item['Nombre']}' eliminado.")
    else:
        st.warning("No se encontraron productos.")

    if st.button("🔙 Volver al inicio"):
        st.session_state.pagina = "Inicio"