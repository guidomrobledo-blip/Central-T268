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

# 1. CARGA DE ARCHIVO (Siempre al principio)
uploaded_file = st.file_uploader("Sube el Excel de CDP", type=["xlsx"])

st.markdown("---")

# 2. PANEL DE BOTONES (VISIBLES SIEMPRE)
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

# 3. LÓGICA DE PROCESAMIENTO
if uploaded_file:
    df = pd.read_excel(uploaded_file)
    
    # --- EJECUCIÓN SEGÚN BOTÓN ---
    if btn_1:
        descargar_clientes(df)
    
    if btn_2:
        descargar_faltantes(df)
        
    if btn_3:
        descargar_domicilios(df)
        
    if btn_4:
        # VALIDACIÓN DE FECHA PARA INFORME
        # Asumiendo que la columna se llama 'Fecha'
        if 'Fecha' in df.columns:
            fecha_excel = pd.to_datetime(df['Fecha']).dt.date.iloc[0]
            hoy = datetime.now().date()
            manana = hoy + timedelta(days=1)
            
            if fecha_excel == manana:
                descargar_informe(df)
            else:
                st.error("⚠️ Informe solo procesa pedidos del día siguiente.")
                st.info(f"Fecha en Excel: {fecha_excel} | Se requiere: {manana}")
        else:
            # Si no hay columna fecha, dejamos pasar o avisamos
            st.warning("No se detectó columna 'Fecha' para validar. Procesando...")
            descargar_informe(df)
            
    if btn_5:
        st.success("Planilla MEC lista para configurar.")

else:
    # Si tocan botones sin haber subido el archivo
    if btn_1 or btn_2 or btn_3 or btn_4 or btn_5:
        st.warning("⚠️ Por favor, sube primero el archivo Excel del CDP.")
