import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
from logic_clientes import descargar_clientes
from logic_faltantes import descargar_faltantes
from logic_domicilios import descargar_domicilios
from logic_informe import descargar_informe

st.set_page_config(page_title="Central Logística T268", layout="wide")

st.title("🛒 Central Logística T268")
st.markdown("---")

# 📁 CARGA DE ARCHIVO (Siempre arriba)
uploaded_file = st.file_uploader("Sube el Excel de CDP", type=["xlsx"])

st.markdown("---")

# 🕹️ PANEL DE BOTONES (Siempre visibles)
st.subheader("Acciones Disponibles")
col1, col2, col3, col4, col5 = st.columns(5)

with col1:
    btn_1 = st.button("1. CLIENTES", use_container_width=True)
with col2:
    btn_2 = st.button("2. FALTANTES", use_container_width=True)
with col3:
    btn_3 = st.button("3. DOMICILIOS", use_container_width=True)
with col4:
    btn_4 = st.button("4. INFORME", use_container_width=True)
with col5:
    btn_5 = st.button("5. PLANILLA MEC", use_container_width=True)

# ⚙️ LÓGICA DE PROCESAMIENTO
if uploaded_file:
    df = pd.read_excel(uploaded_file)
    
    if btn_1:
        descargar_clientes(df)
    
    if btn_2:
        descargar_faltantes(df)
        
    if btn_3:
        descargar_domicilios(df)
        
    if btn_4:
        # Aquí aplicaremos la lógica de fecha en el siguiente paso
        descargar_informe(df)
        
    if btn_5:
        st.success("Planilla MEC procesada (pendiente de lógica específica)")

else:
    # Si alguien toca un botón sin subir archivo
    if btn_1 or btn_2 or btn_3 or btn_4 or btn_5:
        st.warning("⚠️ Primero debes subir el archivo Excel del CDP.")
