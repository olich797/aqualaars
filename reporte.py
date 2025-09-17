# reporte.py
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import io

def mostrar_reporte(db):
    st.header("📊 Reporte de Proformas")

    busqueda_nombre = st.text_input("Buscar por nombre del cliente")
    busqueda_ci = st.text_input("Buscar por CI/NIT")

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

    proformas_filtradas = proformas_lista

    if busqueda_nombre.strip():
        proformas_filtradas = [p for p in proformas_filtradas if busqueda_nombre.strip().lower() in p.get("Nombre Cliente", "").strip().lower()]

    if busqueda_ci.strip():
        proformas_filtradas = [p for p in proformas_filtradas if busqueda_ci.strip() in p.get("CI/NIT", "").strip()]

    if proformas_filtradas:
        df_proformas = pd.DataFrame(proformas_filtradas, columns=["Fecha Emisión", "Fecha Vencimiento", "Nombre Cliente", "CI/NIT", "Total BOB"])
        st.table(df_proformas)

        proforma_seleccionada = st.selectbox("Selecciona una proforma para ver la imagen", [p["ID"] for p in proformas_filtradas])

        if proforma_seleccionada:
            datos_proforma = next((p for p in proformas_filtradas if p["ID"] == proforma_seleccionada), None)

            if datos_proforma:
                fig, ax = plt.subplots(figsize=(10, 6))
                ax.set_title("Proforma", fontsize=18, fontweight="bold")
                ax.text(0.5, 0.5, "Aqualaars", font="Arial", fontweight="bold", fontsize=90, color="#00BFFF", alpha=0.2, ha="center", va="center", transform=ax.transAxes)
                ax.text(0.64, 0.36, "Todo para su piscina", font="Arial",fontweight="bold" , fontsize=30, color="#00BFFF",alpha=0.2, ha="center", va="center", transform=ax.transAxes)
                ax.text(0, 0.85, f"Nombre: {datos_proforma['Nombre Cliente']}         CI/NIT: {datos_proforma['CI/NIT']}", fontsize=12)
                ax.text(0, 0.78, f"Fecha emisión: {datos_proforma['Fecha Emisión']}", fontsize=12)
                ax.text(0, 0.71, f"Fecha vencimiento: {datos_proforma['Fecha Vencimiento']}", fontsize=12)

                col_labels = ["Producto", "Cantidad", "Precio Unitario BOB", "Precio Total BOB"]
                table_data = [[item["Nombre"], item["Cantidad"], item["Precio Unitario BOB"], item["Precio Total BOB"]] for item in datos_proforma["Productos"]]

                tabla = ax.table(cellText=table_data, colLabels=col_labels, cellLoc="center", loc="center", colWidths=[0.50, 0.13, 0.18, 0.18])
                tabla.auto_set_font_size(False)
                tabla.set_fontsize(10)
                tabla.scale(1.2, 1.2)
                ax.text(0, -0.02, f"Total: {round(datos_proforma['Total BOB'], 2)} BOB", fontsize=14, fontweight="bold")
                ax.axis("off")

                buffer = io.BytesIO()
                plt.savefig(buffer, format="png", bbox_inches="tight")
                buffer.seek(0)
                st.image(buffer)
            else:
                st.warning("Esta proforma no tiene productos registrados.")
    else:
        st.warning("No se encontraron proformas con esos criterios.")

    if st.button("🔙 Volver al inicio"):
        st.session_state.pagina = "Inicio"