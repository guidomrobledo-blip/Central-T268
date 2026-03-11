import streamlit as st
import pandas as pd
import numpy as np
import pydeck as pdk
from datetime import datetime, timedelta
import logic_clientes, logic_faltantes, logic_domicilios, logic_informe
import os

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(
    page_title="Dashboard Carrefour Online T268",
    page_icon="🛒",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- FECHA ARGENTINA (UTC-3) ---
fecha_ar_ahora = datetime.utcnow() - timedelta(hours=3)
hoy_ar = fecha_ar_ahora.date()
manana_ar_obj = hoy_ar + timedelta(days=1)
manana_txt = manana_ar_obj.strftime("%d/%m/%Y")

# --- CSS AVANZADO (VISIBILIDAD TOTAL) ---
st.markdown("""
    <style>
    .stApp { background-color: #f0f2f6; }
    
    .header-box {
        background-color: white;
        padding: 15px 30px;
        border-radius: 15px;
        display: flex;
        align-items: center;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05);
        margin-bottom: 20px;
        border-bottom: 4px solid #003876;
    }
    
    .header-title { color: #003876 !important; font-size: 2em !important; font-weight: bold !important; margin: 0 !important; }
    .header-subtitle { color: #555 !important; font-size: 1.1em !important; margin: 0 !important; }

    .section-title {
        color: #1a202c !important;
        font-weight: bold !important;
        font-size: 1.2em !important;
        margin-bottom: 10px !important;
        display: block;
    }

    /* Estilo de Botones Oscuros */
    div.stButton > button {
        background-color: #1a202c !important;
        color: white !important;
        border-radius: 10px;
        height: 3.5em;
        font-weight: bold;
        border: none;
    }
    
    /* Estilo de Botón de Descarga (Verde para diferenciar) */
    div.stDownloadButton > button {
        background-color: #28a745 !important;
        color: white !important;
        border-radius: 10px;
        width: 100%;
    }
    </style>
""", unsafe_allow_html=True)

# --- CABECERA ---
with st.container():
    c_img, c_txt = st.columns([1, 5])
    with c_img:
        if os.path.exists("carrefour+logo.png"):
            st.image("carrefour+logo.png", width=120)
    with c_txt:
        st.markdown('<h1 class="header-title">Central Logística Carrefour Online</h1>', unsafe_allow_html=True)
        st.markdown(f'<p class="header-subtitle">Tienda 268 - Rosario | Panel Operativo</p>', unsafe_allow_html=True)

# --- COLUMNAS PRINCIPALES ---
col_izq, col_der = st.columns([1.3, 2])

with col_izq:
    st.markdown('<span class="section-title">📂 CARGA DE DATOS (DÍA ACTUAL)</span>', unsafe_allow_html=True)
    archivo_cdp = st.file_uploader("Subir CDP del Día", type=["xlsx"], key="main_up")
    
    st.markdown("---")
    st.markdown('<span class="section-title">🛠️ ACCIONES Y DESCARGAS</span>', unsafe_allow_html=True)
    
    # Procesamiento base si hay archivo
    if archivo_cdp:
        df_raw = pd.read_excel(archivo_cdp)
        df_clean, fecha_tit = logic_clientes.motor_limpieza(df_raw)
        
        # Grid de Botones con Funcionalidad corregida
        g1, g2 = st.columns(2)
        with g1:
            if st.button("👥 1. CLIENTES", use_container_width=True):
                pdf = logic_clientes.generar_pdf_clientes(df_clean, fecha_tit)
                st.download_button("📥 DESCARGAR CLIENTES", bytes(pdf), f"Clientes_{fecha_tit}.pdf")
        
        with g2:
            if st.button("🔍 2. FALTANTES", use_container_width=True):
                pdf = logic_faltantes.generar_pdf_faltantes(df_clean, fecha_tit)
                st.download_button("📥 DESCARGAR FALTANTES", bytes(pdf), f"Faltantes_{fecha_tit}.pdf")
        
        g3, g4 = st.columns(2)
        with g3:
            if st.button("🚚 3. DOMICILIOS", use_container_width=True):
                pdf = logic_domicilios.generar_pdf_domicilios(df_clean, fecha_tit)
                st.download_button("📥 DESCARGAR RUTAS", bytes(pdf), f"Rutas_{fecha_tit}.pdf")
        
        with g4:
            btn_informe = st.button("📊 4. INFORME", use_container_width=True)
            
        st.link_button("🌐 5. PLANILLA MEC", "https://docs.google.com/spreadsheets/d/1v0Rls8fg_uIGfhA1t3CzINq3VfAUvPY3DY8_m_ZSmM8/edit#gid=0", use_container_width=True)

    else:
        st.warning("⚠️ Sube el CDP para habilitar acciones.")

    # --- LÓGICA DEL INFORME (BOTÓN 4) ---
    if st.session_state.get('inf_activo', False) or (archivo_cdp and locals().get('btn_informe')):
        st.session_state.inf_activo = True
        st.markdown(f"""<div style="background-color:#fff3e0; padding:15px; border-radius:10px; border-left:5px solid #ff9800; margin-top:15px;">
            <p style="color:#e65100; font-weight:bold; margin:0;">🚀 Informe para mañana: {manana_txt}</p></div>""", unsafe_allow_html=True)
        
        archivo_inf = st.file_uploader("Subir CDP de Mañana", type=["xlsx"], key="inf_up")
        
        if archivo_inf:
            df_inf_raw = pd.read_excel(archivo_inf)
            df_inf_clean, fecha_inf_tit = logic_clientes.motor_limpieza(df_inf_raw)
            
            # Validación estricta de fecha
            try:
                f_norm = fecha_inf_tit.replace("/", "-")
                fmt = "%d-%m-%Y" if len(f_norm.split("-")[-1]) == 4 else "%d-%m-%y"
                fecha_det_obj = datetime.strptime(f_norm, fmt).date()
                
                if fecha_det_obj == manana_ar_obj:
                    st.success(f"✅ Fecha validada: {fecha_inf_tit}")
                    obs = st.text_area("📝 OBSERVACIONES:")
                    if st.button("GENERAR PDF FINAL", use_container_width=True):
                        pdf_inf = logic_informe.generar_pdf_informe(df_inf_clean, obs)
                        st.download_button("📥 DESCARGAR INFORME", pdf_inf, f"Informe_{fecha_inf_tit}.pdf")
                else:
                    st.error(f"Archivo incorrecto. Se detectó {fecha_inf_tit} pero se busca {manana_txt}.")
            except:
                st.error("Error al leer la fecha del archivo.")

with col_der:
    st.markdown('<span class="section-title">🗺️ MONITOREO GEOGRÁFICO (ROSARIO)</span>', unsafe_allow_html=True)
    
    view_state = pdk.ViewState(latitude=-32.9442, longitude=-60.6505, zoom=11, pitch=45)
    st.pydeck_chart(pdk.Deck(
        map_style='mapbox://styles/mapbox/light-v9',
        initial_view_state=view_state,
        layers=[pdk.Layer("ScatterplotLayer", data=[], get_position='[lng, lat]', get_radius=200)]
    ))
    
    st.markdown('<span class="section-title">📈 VOLUMEN DE PEDIDOS</span>', unsafe_allow_html=True)
    if archivo_cdp:
        # Gráfico basado en datos reales (conteo simple por Estado/Picking)
        if 'Estado' in df_clean.columns:
            st.bar_chart(df_clean['Estado'].value_counts())
        else:
            st.info("Gráfico disponible tras procesar el CDP.")
    else:
        st.info("Sin datos para graficar.")
