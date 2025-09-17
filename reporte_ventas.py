# reporte_ventas.py
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import io

def mostrar_reporte_ventas(db):
    st.header("📊 Reporte de Ventas")

    busqueda_nombre = st.text_input("Buscar por nombre del cliente")
    busqueda_ci = st.text_input("Buscar por CI/NIT")

    ventas = db.collection("ventas").stream()
    ventas_lista = []

    for venta in ventas:
        datos = venta.to_dict()
        ventas_lista.append({
            "ID": venta.id,
            "Fecha Venta": datos.get("fecha_venta", ""),
            "Nombre Cliente": datos.get("nombre_cliente", ""),
            "CI/NIT": datos.get("ci_nit", ""),
            "Total BOB": datos.get("total", 0),
            "Productos": datos.get("productos", [])
        })

    ventas_filtradas = ventas_lista

    if busqueda_nombre.strip():
        ventas_filtradas = [v for v in ventas_filtradas if busqueda_nombre.lower() in v["Nombre Cliente"].lower()]

    if busqueda_ci.strip():
        ventas_filtradas = [v for v in ventas_filtradas if busqueda_ci in v["CI/NIT"]]

    if ventas_filtradas:
        df_ventas = pd.DataFrame(ventas_filtradas, columns=["Fecha Venta", "Nombre Cliente", "CI/NIT", "Total BOB"])
        st.table(df_ventas)

        venta_seleccionada = st.selectbox("Selecciona una venta para ver el comprobante", [v["ID"] for v in ventas_filtradas])

        if venta_seleccionada:
            datos_venta = next((v for v in ventas_filtradas if v["ID"] == venta_seleccionada), None)

            if datos_venta:
                fig, ax = plt.subplots(figsize=(10, 6))
                ax.set_title("Comprobante de Venta", fontsize=18, fontweight="bold")
                ax.text(0.5, 0.5, "Aqualaars", font="Arial", fontweight="bold", fontsize=90, color="#00BFFF", alpha=0.2, ha="center", va="center", transform=ax.transAxes)
                ax.text(0.5, 0.45, "Todo para su piscina", font="Arial", fontsize=14, color="#0077CC", ha="center", va="center", transform=ax.transAxes)
                ax.text(0, 0.85, f"Cliente: {datos_venta['Nombre Cliente']}         CI/NIT: {datos_venta['CI/NIT']}", fontsize=12)
                ax.text(0, 0.78, f"Fecha de venta: {datos_venta['Fecha Venta']}", fontsize=12)

                col_labels = ["Producto", "Cantidad", "Precio Unitario BOB", "Precio Total BOB"]
                table_data = [[item["Nombre"], item["Cantidad"], item["Precio Unitario BOB"], item["Precio Total BOB"]] for item in datos_venta["Productos"]]

                tabla = ax.table(cellText=table_data, colLabels=col_labels, cellLoc="center", loc="center", colWidths=[0.50, 0.13, 0.18, 0.18])
                tabla.auto_set_font_size(False)
                tabla.set_fontsize(10)
                tabla.scale(1.2, 1.2)

                ax.text(0, -0.02, f"Total: {round(datos_venta['Total BOB'], 2)} BOB", fontsize=14, fontweight="bold")
                ax.axis("off")

                buffer = io.BytesIO()
                plt.savefig(buffer, format="png", bbox_inches="tight")
                buffer.seek(0)
                st.image(buffer)
            else:
                st.warning("No se encontraron productos en esta venta.")
    else:
        st.warning("No se encontraron ventas con esos criterios.")

    if st.button("🔙 Volver al inicio"):
        st.session_state.pagina = "Inicio"