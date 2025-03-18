import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from fpdf import FPDF
import io

# Función para realizar el análisis de stock
def analizar_stock(df):
    # Análisis ABC y Rotación
    df["Rotación 30 días"] = df["Stock"] / df["30 Días"]
    df["Categoría ABC"] = pd.cut(df["Stock"].cumsum() / df["Stock"].sum(),
                                  bins=[0, 0.8, 0.95, 1], labels=["A", "B", "C"])
    df["Clasificación Rotación"] = df["Rotación 30 días"].apply(
        lambda x: "Alta" if x <= 0.5 else "Media" if x <= 1.5 else "Baja")
    
    # Análisis de Espacio por Pallets
    df["Pallets"] = df["Stock"] / df["CajasPalet"]
    
    return df

# Función para generar el informe en PDF
def generar_pdf(df):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, "Informe de Análisis de Stock", ln=True, align="C")
    pdf.ln(10)
    
    # Análisis ABC y Rotación
    fig, ax = plt.subplots(figsize=(8, 6))
    pd.crosstab(df["Categoría ABC"], df["Clasificación Rotación"]).plot(kind="bar", stacked=True, ax=ax)
    plt.savefig("grafico_abc_rotacion.png")
    pdf.image("grafico_abc_rotacion.png", x=10, w=180)
    pdf.multi_cell(0, 7, "Conclusión: La mayoría del stock de Categoría A tiene alta rotación y debe ubicarse en zonas accesibles.")
    
    pdf_output = io.BytesIO()
    pdf.output(pdf_output, dest='S')
    return pdf_output.getvalue()

# Función para generar el Excel con los cálculos
def generar_excel(df):
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, sheet_name="Análisis de Stock", index=False)
    return output.getvalue()

# Interfaz Streamlit
st.title("Análisis de Stock y Layout de Cámara Frigorífica")

# Subir archivo Excel
archivo = st.file_uploader("Sube el archivo Excel con el stock", type=["xlsx"])

if archivo is not None:
    df = pd.read_excel(archivo)
    df = analizar_stock(df)
    st.write("### Datos analizados:")
    st.dataframe(df)
    
    # Generar PDF
    pdf_bytes = generar_pdf(df)
    st.download_button("Descargar Informe en PDF", pdf_bytes, "Informe_Stock.pdf", "application/pdf")
    
    # Generar Excel
    excel_bytes = generar_excel(df)
    st.download_button("Descargar Informe en Excel", excel_bytes, "Analisis_Stock.xlsx", "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
