import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from fpdf import FPDF
import io
import os
from datetime import datetime

# Función para realizar el análisis de stock
def analizar_stock(df):
    # Análisis ABC y Rotación
    df["Rotación 30 días"] = df["Stock"] / df["30 Días"]
    df["Rotación 21 días"] = df["Stock"] / df["21 Días"]
    df["Categoría ABC"] = pd.cut(df["Stock"].cumsum() / df["Stock"].sum(),
                                  bins=[0, 0.8, 0.95, 1], labels=["A", "B", "C"])
    df["Clasificación Rotación 30D"] = df["Rotación 30 días"].apply(
        lambda x: "Alta" if x <= 0.5 else "Media" if x <= 1.5 else "Baja")
    df["Clasificación Rotación 21D"] = df["Rotación 21 días"].apply(
        lambda x: "Alta" if x <= 0.5 else "Media" if x <= 1.5 else "Baja")
    df["ABC + Rotación"] = df["Categoría ABC"].astype(str).fillna("Sin Clasificación") + " - " + df["Clasificación Rotación 30D"].astype(str).fillna("Sin Clasificación")
    
    # Análisis de Espacio por Pallets
    df["Pallets"] = df["Stock"] / df["CajasPalet"]
    
    # Cálculo de Stock Excedente
    df["Factor de Stock"] = df["Stock"] / df["30 Días"]
    df["Clasificación Exceso Stock"] = df["Factor de Stock"].apply(
        lambda x: "Óptimo" if x <= 1.5 else "En Riesgo" if x <= 3 else "Excedente")
    
    # Clasificación por tipo de producto
    def clasificar_tipo_producto(descripcion):
        descripcion = str(descripcion).lower()
        if "pan" in descripcion or "baguette" in descripcion:
            return "Panadería"
        elif "croissant" in descripcion or "bollería" in descripcion or "donut" in descripcion:
            return "Bollería"
        elif "nata" in descripcion or "margarina" in descripcion or "mantequilla" in descripcion:
            return "Materias Primas"
        elif "chocolate" in descripcion or "cacao" in descripcion:
            return "Chocolate"
        else:
            return "Otros"
    
    df["Tipo de Producto"] = df["Descripción de artículo"].apply(clasificar_tipo_producto)
    
    # Cálculo de necesidades de reposición
    df["Consumo Diario"] = df["30 Días"] / 30
    df["Stock de Seguridad"] = df["Consumo Diario"] * 7
    df["Necesidad de Reposición"] = df["Stock de Seguridad"] - df["Stock"]
    df["Necesidad de Reposición"] = df["Necesidad de Reposición"].apply(lambda x: max(x, 0))
    
    # Análisis de productos obsoletos
    df["Fecha Última Venta"] = pd.to_datetime(df["UltimaVta"], errors="coerce")
    df["Días Sin Venta"] = (pd.Timestamp.today() - df["Fecha Última Venta"]).dt.days
    df["Estado de Obsolescencia"] = df["Días Sin Venta"].apply(lambda x: "Obsoleto" if x > 90 else "Activo")
    
    return df

# Función para generar el informe en Excel con fecha y hora
def generar_excel(df):
    output = io.BytesIO()
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M")
    file_name = f"Analisis_Stock_{timestamp}.xlsx"
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, sheet_name="Análisis de Stock", index=False)
    output.seek(0)
    return output.getvalue(), file_name

# Interfaz Streamlit
st.title("Análisis de Stock y Layout de Cámara Frigorífica")

# Subir archivo Excel
archivo = st.file_uploader("Sube el archivo Excel con el stock", type=["xlsx"])

if archivo is not None:
    df = pd.read_excel(archivo)
    df = analizar_stock(df)
    st.write("### Datos analizados:")
    st.dataframe(df)
    
    # Generar Excel con fecha y hora
    excel_bytes, excel_filename = generar_excel(df)
    st.download_button("Descargar Informe en Excel", data=excel_bytes, file_name=excel_filename, mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
