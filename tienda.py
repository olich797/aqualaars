import streamlit as st
import firebase_admin
from firebase_admin import credentials, firestore
import pandas as pd
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
import io
import json

# ✅ Obtener los Secrets desde Streamlit Cloud
firebase_secrets = dict(st.secrets["firebase"])
firebase_secrets["private_key"] = firebase_secrets["private_key"].replace("\\n", "\n")  # 🔹 Corrige el formato de la clave privada

# ✅ Verificar si Firebase ya está inicializado
if not firebase_admin._apps:
    cred = credentials.Certificate(firebase_secrets)
    firebase_admin.initialize_app(cred)

# ✅ Conectar a Firestore
db = firestore.client()


# 🔑 Verificar si el usuario está autenticado
if "autenticado" not in st.session_state:
    st.session_state.autenticado = False

# 🛠 Pantalla de login
if not st.session_state.autenticado:
    st.title("🔑 Iniciar Sesión")

    user = st.text_input("Usuario:")
    password = st.text_input("Contraseña:", type="password")

    if st.button("Ingresar"):
        if user == "admin" and password == "admin":
            st.session_state.autenticado = True
            st.success("Login exitoso. Bienvenido a la aplicación!")
        else:
            st.error("Usuario o contraseña incorrectos.")

    st.stop()  # 🔴 Detiene la ejecución si el usuario no está autenticado

if "pagina" not in st.session_state:
    st.session_state.pagina = "Inicio"

if st.session_state.pagina == "Inicio":
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

    # 🔹 Buscador de productos
    
    busqueda = st.text_input(" 🔍 Ingrese el nombre del producto")

    # 🔹 Obtener lista de productos desde Firebase
    productos = db.collection("inventario").stream()
    productos_lista = []
    
    for producto in productos:
        datos = producto.to_dict()
        if busqueda.lower() in datos["nombre"].lower():  # Filtrar por búsqueda
            productos_lista.append({
                "Nombre": datos["nombre"],
                "Cantidad": datos["cantidad"],
                "Precio USD": round(datos["precio_usd"], 2),
                "Precio BOB": round(datos["precio_usd"] * 6.96, 2),
                "Precio BS": round(datos["precio_bs"], 2)
            })

    # 🔹 Mostrar tabla con productos filtrados
    if productos_lista:
        df = pd.DataFrame(productos_lista)
        st.table(df)
    else:
        st.warning("No se encontraron productos.")
# ✅ INVENTARIO (Ahora con Sidebar para Configuración)
if st.session_state.pagina == "Inventario":
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

    # 🔹 Mostrar, editar y eliminar productos con formato mejorado
    st.subheader("📋 Inventario de Productos")

    busqueda = st.text_input("Buscar producto por nombre", key="busqueda_producto")
    productos = db.collection("inventario").stream()

    productos_lista = []
    for producto in productos:
        datos = producto.to_dict()
        doc_id = producto.id  # Obtener el ID del documento en Firebase
        if busqueda.lower() in datos["nombre"].lower():
            productos_lista.append({
                "ID": doc_id,
                "Nombre": datos["nombre"],
                "Cantidad": datos["cantidad"],
                "Precio USD": round(datos["precio_usd"], 2),
                "Precio BOB": round(datos["precio_usd"] * nuevo_tipo_cambio, 2),
                "Precio BS": datos["precio_bs"]
            })

    # 🔹 Mostrar tabla correctamente en filas alineadas
    if productos_lista:

        col1, col2, col3, col4, col5, col6, col7 = st.columns([2.5, 0.9, 0.8, 0.8, 0.8, 1.1, 1.1])
        with col1:
            st.write("Nombre")

        with col2:  
            st.write("Cantidad")

        with col3:
            st.write("USD")

        with col4:
            st.write("BOB")

        with col5:
            st.write("BS")

        with col6:
            st.write("")

        with col7:
            st.write("")
        
        df = pd.DataFrame(productos_lista)

        # Mostrar tabla con edición en cada fila
        for index, item in df.iterrows():
            col1, col2, col3, col4, col5, col6, col7 = st.columns([2.5, 0.9, 0.8, 0.8, 0.8, 1.1, 1.1])

            with col1:
                st.write(item["Nombre"])

            with col2:
                cantidad_editada = st.number_input("", min_value=1, step=1, value=item["Cantidad"], key=f"cantidad_{item['ID']}", label_visibility="collapsed")

            with col3:
                precio_editado = st.number_input("", min_value=0.01, step=0.01, value=item["Precio USD"], key=f"precio_{item['ID']}", label_visibility="collapsed")

            with col4:
                st.write(f"{item['Precio BOB']}")

            with col5:
                precio_editado_bs = st.number_input("", min_value=0.01, step=0.01, value=item["Precio BS"], key=f"precio_bs_{item['ID']}", label_visibility="collapsed")
            
            with col6:
                guardar_btn = st.button("Guardar", key=f"guardar_{item['ID']}")

                if guardar_btn:
                    db.collection("inventario").document(item["ID"]).update({
                        "cantidad": cantidad_editada,
                        "precio_usd": precio_editado,
                        "precio_bob": round(precio_editado * nuevo_tipo_cambio, 2),
                        "precio_bs": precio_editado_bs
                    })
                    st.success(f"✅ Producto '{item['Nombre']}' actualizado.")

            with col7:
                eliminar_btn = st.button("Eliminar", key=f"eliminar_{item['ID']}")

                if eliminar_btn:
                    db.collection("inventario").document(item["ID"]).delete()
                    st.success(f"🗑 Producto '{item['Nombre']}' eliminado.")

    else:
        st.warning("No se encontraron productos.")
        
    if st.button("🔙 Volver al inicio"):
        st.session_state.pagina = "Inicio"
        
# ✅ PROFORMA
if st.session_state.pagina == "Proforma":
    st.header("📝 Generar Proforma")

    # Datos del cliente
    nombre_cliente = st.text_input("Nombre del Cliente")
    ci_nit = st.text_input("CI o NIT")
    fecha_actual = st.date_input("Fecha de emisión", value=datetime.today())
    fecha_vencimiento = st.date_input("Fecha de vencimiento", value=datetime.today() + timedelta(days=30))

    # ✅ Inicializar productos_lista si no existe
    if "productos_lista" not in st.session_state:
        st.session_state.productos_lista = []

    # Obtener lista de productos del inventario
    productos_db = list(db.collection("inventario").stream())  
    nombres_productos = [producto.to_dict()["nombre"] for producto in productos_db]

    # 🔹 Selección de producto del inventario
    st.subheader("Seleccionar Producto del Inventario")
    producto_inventario = st.selectbox("Selecciona un producto", [""] + nombres_productos)

    # Buscar en la base de datos si el producto existe
    producto_encontrado = next((p.to_dict() for p in productos_db if p.to_dict()["nombre"] == producto_inventario), None)

    # 🔹 Asignar precio correctamente si el producto existe
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

    # 🔹 Ingreso manual de productos
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

    # 🔹 Mostrar tabla y modificar/eliminar productos
    if st.session_state.productos_lista:
        st.subheader("Lista de Productos en la Proforma")

        # 🔹 Mostrar encabezados una sola vez
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.markdown("**Producto**")
        with col2:
            st.markdown("**Cantidad**")
        with col3:
            st.markdown("**Precio Unitario BOB**")
        with col4:
            st.markdown("**Eliminar**")

    # 🔁 Mostrar cada producto en una fila
        nueva_lista = []
        
        for i, item in enumerate(st.session_state.productos_lista):
            col1, col2, col3, col4 = st.columns(4)
        
            with col1:
                st.write(item["Nombre"])
        
            with col2:
                item["Cantidad"] = st.number_input(
                    "", min_value=1, step=1,
                    value=int(item["Cantidad"]),
                    key=f"cantidad_{i}",
                    label_visibility="collapsed"
                )
        
            with col3:
                precio_unitario = float(item.get("Precio Unitario BOB", 0.0))
                item["Precio Unitario BOB"] = st.number_input(
                    "", min_value=0.01, step=0.01,
                    value=precio_unitario,
                    key=f"precio_bs_{i}",
                    label_visibility="collapsed"
                )
        
            item["Precio Total BOB"] = round(item["Cantidad"] * item["Precio Unitario BOB"], 2)
        
            with col4:
                eliminar = st.button(f"🗑 Eliminar", key=f"eliminar_{i}")
            
            if not eliminar:
                nueva_lista.append(item)
            else:
                st.success(f"Producto '{item['Nombre']}' eliminado correctamente.")
        
        # ✅ Actualizar la lista en session_state
        st.session_state.productos_lista = nueva_lista

        total_proforma = sum([item["Precio Total BOB"] for item in st.session_state.productos_lista])
        st.write(f"**Total en BOB:** {round(total_proforma, 2)} BOB")

        if st.button("📥 Guardar Proforma en la Base de Datos"):
            proforma_id = f"proforma_{datetime.now().strftime('%Y%m%d_%H%M%S')}"  # ID único basado en la fecha y hora
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


        # ✅ Crear imagen con matplotlib (con tabla y gota de agua)
        fig, ax = plt.subplots(figsize=(10, 6))  # Ajustar tamaño para mejor distribución

        # Configurar título con gota
        ax.set_title("Proforma", fontsize=24, fontweight="bold")

        # 🔹 Agregar marca de agua "Aqualaars" en color celeste y semitransparente
        ax.text(0.5, 0.5, "Aqualaars",font = "Arial",fontweight="bold",fontsize=90, color="#00BFFF", alpha=0.2,
        ha="center", va="center", transform=ax.transAxes)


        # Información del cliente (ubicada arriba pero con menos espacio)
        ax.text(0, 0.85, f"Nombre: {nombre_cliente}         CI/NIT: {ci_nit}", fontsize=12)
        ax.text(0, 0.78, f"Fecha emisión: {fecha_actual}", fontsize=12)
        ax.text(0, 0.71, f"Fecha vencimiento: {fecha_vencimiento}", fontsize=12)

        # Ubicar la tabla en el **centro** de la imagen
        col_labels = ["Producto", "Cantidad", "Precio Unitario BOB", "Precio Total BOB"]
        table_data = [[item["Nombre"], item["Cantidad"], item["Precio Unitario BOB"], item["Precio Total BOB"]] for item in st.session_state.productos_lista]

        tabla = ax.table(cellText=table_data, colLabels=col_labels, cellLoc="center", loc="center", colWidths=[0.50, 0.13, 0.18, 0.18])

        # Estilizar la tabla
        tabla.auto_set_font_size(False)
        tabla.set_fontsize(10)
        tabla.scale(1.2, 1.2)

        # Ubicar el total **justo debajo** de la tabla, sin demasiado espacio
        ax.text(0, -0.02, f"Total: {round(total_proforma, 2)} BOB", fontsize=14, fontweight="bold")

        # Ocultar los ejes para un diseño más limpio
        ax.axis("off")
        
        st.pyplot(fig)
        
        # ✅ Guardar imagen en buffer como PDF
        buffer = io.BytesIO()
        plt.savefig(buffer, format="pdf", bbox_inches="tight")
        buffer.seek(0)

        # ✅ Botón de descarga como PDF
        st.download_button(label="📥 Descargar Proforma",
                   data=buffer,
                   file_name="proforma.pdf",
                   mime="application/pdf")
        
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

              
if st.session_state.pagina == "Reporte":
    st.header("📊 Reporte de Proformas")

    # 🔹 Buscador de proformas
    busqueda_nombre = st.text_input("Buscar por nombre del cliente")
    busqueda_ci = st.text_input("Buscar por CI/NIT")

    # 🔹 Obtener lista de proformas desde Firebase
    proformas = db.collection("proformas").stream()
    proformas_lista = []

    for proforma in proformas:
        datos = proforma.to_dict()
        proformas_lista.append({
            "ID": proforma.id,
            "Fecha Emisión": datos.get("fecha_emision", ""),
            "Fecha Vencimiento": datos.get("fecha_vencimiento", ""),
            "Nombre Cliente": datos.get("nombre_cliente", ""),
            "CI/NIT": datos.get("ci_nit", ""),
            "Total BOB": datos.get("total", 0),
            "Productos": datos.get("productos", [])
        })

    # ✅ Aplicar filtros solo si el usuario ingresó algo
    proformas_filtradas = proformas_lista

    if busqueda_nombre.strip():
        proformas_filtradas = [p for p in proformas_filtradas if busqueda_nombre.strip().lower() in p.get("Nombre Cliente", "").strip().lower()]

    if busqueda_ci.strip():
        proformas_filtradas = [p for p in proformas_filtradas if busqueda_ci.strip() in p.get("CI/NIT", "").strip()]

    # 🔹 Mostrar tabla con resultados filtrados
    if proformas_filtradas:
        df_proformas = pd.DataFrame(proformas_filtradas, columns=["Fecha Emisión", "Fecha Vencimiento", "Nombre Cliente", "CI/NIT", "Total BOB"])
        st.table(df_proformas)

        # 🔹 Selector de proforma (solo muestra resultados filtrados)
        proforma_seleccionada = st.selectbox("Selecciona una proforma para ver la imagen", [p["ID"] for p in proformas_filtradas])

        if proforma_seleccionada:
            datos_proforma = next((p for p in proformas_filtradas if p["ID"] == proforma_seleccionada), None)

            if datos_proforma:
                # ✅ Crear imagen con matplotlib (igual a la vista en "Proforma")
                fig, ax = plt.subplots(figsize=(10, 6))

                # Configurar título
                ax.set_title("Proforma", fontsize=18, fontweight="bold")

                # 🔹 Agregar marca de agua "Aqualaars" en color celeste y semitransparente
                ax.text(0.5, 0.5, "Aqualaars",font = "Arial",fontweight="bold",fontsize=90, color="#00BFFF", alpha=0.2,
                ha="center", va="center", transform=ax.transAxes)
                
                # Información del cliente
                ax.text(0, 0.85, f"Nombre: {datos_proforma['Nombre Cliente']}         CI/NIT: {datos_proforma['CI/NIT']}", fontsize=12)
                ax.text(0, 0.78, f"Fecha emisión: {datos_proforma['Fecha Emisión']}", fontsize=12)
                ax.text(0, 0.71, f"Fecha vencimiento: {datos_proforma['Fecha Vencimiento']}", fontsize=12)

                # Tabla de productos
                col_labels = ["Producto", "Cantidad", "Precio Unitario BOB", "Precio Total BOB"]
                table_data = [[item["Nombre"], item["Cantidad"], item["Precio Unitario BOB"], item["Precio Total BOB"]] for item in datos_proforma["Productos"]]

                tabla = ax.table(cellText=table_data, colLabels=col_labels, cellLoc="center", loc="center", colWidths=[0.50, 0.13, 0.18, 0.18])

                # Estilizar la tabla
                tabla.auto_set_font_size(False)
                tabla.set_fontsize(10)
                tabla.scale(1.2, 1.2)

                # Ubicar el total debajo de la tabla
                ax.text(0, -0.02, f"Total: {round(datos_proforma['Total BOB'], 2)} BOB", fontsize=14, fontweight="bold")

                # Ocultar los ejes
                ax.axis("off")

                # ✅ Guardar imagen en buffer para visualizarla
                buffer = io.BytesIO()
                plt.savefig(buffer, format="png", bbox_inches="tight")
                buffer.seek(0)

                # ✅ Mostrar imagen en la interfaz
                st.image(buffer)
            else:
                st.warning("Esta proforma no tiene productos registrados.")
    else:
        st.warning("No se encontraron proformas con esos criterios.")

    if st.button("🔙 Volver al inicio"):
        st.session_state.pagina = "Inicio"
