import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import logic_clientes, logic_faltantes, logic_domicilios, logic_informe

st.set_page_config(page_title="Central T268", layout="wide")

# Estilos de botones
st.markdown("<style>div.stButton > button:first-child, div.stLinkButton > a {height: 3em; font-weight: bold; display: flex; align-items: center; justify-content: center; text-decoration: none;}</style>", unsafe_allow_html=True)

st.title("🛒 Central Logística T268")

# --- SECCIÓN GENERAL (1, 2, 3) ---
archivo_cdp = st.file_uploader("📂 CARGAR EXCEL CDP (Para Clientes, Faltantes y Rutas)", type=["xlsx"])

st.divider()

# Panel de Botones Siempre Visibles
c1, c2, c3, c4, c5 = st.columns(5)

with c1:
    btn_1 = st.button("🟢 1. CLIENTES", use_container_width=True)
with c2:
    btn_2 = st.button("🔵 2. FALTANTES", use_container_width=True)
with c3:
    btn_3 = st.button("🟡 3. DOMICILIOS", use_container_width=True)
with c4:
    btn_4 = st.button("🟠 4. INFORME", use_container_width=True)
with c5:
    st.link_button("🌐 5. PLANILLA MEC", 
                   "https://docs.google.com/spreadsheets/d/1v0Rls8fg_uIGfhA1t3CzINq3VfAUvPY3DY8_m_ZSmM8/edit?gid=0#gid=0", 
                   use_container_width=True)

# --- LÓGICA DE BOTONES 1, 2 y 3 ---
if archivo_cdp:
    df_raw = pd.read_excel(archivo_cdp)
    df_clean, fecha_tit = logic_clientes.motor_limpieza(df_raw)

    if btn_1:
        with c1:
            pdf = logic_clientes.generar_pdf_clientes(df_clean, fecha_tit)
            st.download_button("📥 Descargar", bytes(pdf), f"Clientes_{fecha_tit}.pdf", key="dl_1")
    
    if btn_2:
        with c2:
            pdf = logic_faltantes.generar_pdf_faltantes(df_clean, fecha_tit)
            st.download_button("📥 Descargar", bytes(pdf), f"Faltantes_{fecha_tit}.pdf", key="dl_2")
            
    if btn_3:
        with c3:
            pdf = logic_domicilios.generar_pdf_domicilios(df_clean, fecha_tit)
            st.download_button("📥 Descargar", bytes(pdf), f"Ruta_{fecha_tit}.pdf", key="dl_3")

# --- LÓGICA EXCLUSIVA BOTÓN 4 (INFORME) ---
if btn_4 or st.session_state.get('inf_activo', False):
    st.session_state.inf_activo = True
    st.markdown("---")
    st.subheader("🚀 Procesador Exclusivo de Informe")
    
    archivo_inf = st.file_uploader("Subir planilla para INFORME (Debe ser fecha de mañana)", type=["xlsx"], key="u_inf")
    
    if archivo_inf:
        df_inf_raw = pd.read_excel(archivo_inf)
        # Usamos tu motor de limpieza para sacar la fecha
        df_inf_clean, fecha_inf_tit = logic_clientes.motor_limpieza(df_inf_raw)
        
        # Validación de Fecha (Hoy + 1)
        hoy = datetime.now().date()
        manana = (hoy + timedelta(days=1)).strftime("%d-%m-%Y")
        
        if fecha_inf_tit == manana:
            st.success(f"✅ Fecha correcta: {fecha_inf_tit}. Puedes proceder.")
            obs = st.text_area("📝 OBSERVACIONES:", placeholder="Escriba aquí...")
            if st.button("GENERAR PDF INFORME"):
                pdf_bytes = logic_informe.generar_pdf_informe(df_inf_clean, obs)
                st.download_button("📥 DESCARGAR INFORME", pdf_bytes, f"Informe_{fecha_inf_tit}.pdf")
        else:
            st.error("⚠️ Informe solo procesa pedidos del día siguiente.")
            st.info(f"Fecha detectada: {fecha_inf_tit} | Se requiere: {manana}")

# Mensajes de advertencia
if (btn_1 or btn_2 or btn_3) and not archivo_cdp:
    st.warning("⚠️ Sube el archivo en el cargador superior para las opciones 1, 2 o 3.")
