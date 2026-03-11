import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import logic_clientes, logic_faltantes, logic_domicilios, logic_informe
import os

# --- CONFIGURACIÓN ---
st.set_page_config(
    page_title="Central Logística T268",
    page_icon="🛒",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- FECHA ARGENTINA (UTC-3) ---
fecha_ar_ahora = datetime.utcnow() - timedelta(hours=3)
hoy_ar = fecha_ar_ahora.date()
manana_ar_obj = hoy_ar + timedelta(days=1)
manana_txt = manana_ar_obj.strftime("%d/%m/%Y")

# --- CSS MODERNO: TEMA OSCURO CON EFECTOS NEON ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700;800;900&display=swap');
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700;900&display=swap');
    
    .stApp {
        background: linear-gradient(135deg, #0a0a0f 0%, #1a1a2e 50%, #16213e 100%);
        font-family: 'Inter', sans-serif;
    }
    
    .header-container {
        background: linear-gradient(145deg, rgba(26, 26, 46, 0.95), rgba(22, 33, 62, 0.95));
        border-radius: 20px;
        padding: 25px 35px;
        margin-bottom: 25px;
        border: 1px solid rgba(0, 150, 255, 0.3);
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.4);
        backdrop-filter: blur(20px);
        position: relative;
    }
    
    .title-main {
        color: #ffffff;
        font-family: 'Orbitron', sans-serif;
        font-weight: 900;
        font-size: 2.4em;
        margin: 0;
        text-transform: uppercase;
        letter-spacing: 3px;
        text-shadow: 0 0 20px rgba(0, 150, 255, 0.5);
    }
    
    /* BOTONES NEON */
    div.stButton > button {
        background: linear-gradient(145deg, rgba(30, 30, 50, 0.9), rgba(20, 20, 40, 0.9)) !important;
        border-radius: 16px !important;
        height: 5em !important;
        font-weight: 700 !important;
        color: white !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        transition: all 0.3s ease !important;
    }
    
    button[key="top_1"] { border-color: rgba(76, 175, 80, 0.5) !important; }
    button[key="top_2"] { border-color: rgba(30, 136, 229, 0.5) !important; }
    button[key="top_3"] { border-color: rgba(255, 179, 0, 0.5) !important; }
    button[key="top_4"] { border-color: rgba(244, 81, 30, 0.5) !important; }

    div.stButton > button:hover { transform: translateY(-3px) !important; border-color: white !important; }

    .glass-card {
        background: linear-gradient(145deg, rgba(26, 26, 46, 0.8), rgba(22, 33, 62, 0.6));
        border-radius: 20px;
        padding: 25px;
        border: 1px solid rgba(255, 255, 255, 0.1);
        backdrop-filter: blur(20px);
        margin-bottom: 20px;
    }
    
    .card-title {
        color: #ffffff;
        font-weight: 700;
        text-transform: uppercase;
        margin-bottom: 20px;
        display: flex;
        align-items: center;
    }

    /* Ocultar elementos de Streamlit */
    #MainMenu, footer, header {visibility: hidden;}
    </style>
""", unsafe_allow_html=True)

# --- HEADER MODERNO ---
st.markdown(f"""
    <div class="header-container">
        <div style="display: flex; align-items: center; justify-content: space-between;">
            <div>
                <h1 class="title-main">Central Logística T268</h1>
                <p style="color: rgba(255,255,255,0.7); margin-top:8px;">
                    Rosario - Gestión de Ventas Online <span style="background: #0066ff; padding: 4px 12px; border-radius: 20px; font-size: 0.8em;">{hoy_ar.strftime("%d/%m/%Y")}</span>
                </p>
            </div>
            <img src="https://upload.wikimedia.org/wikipedia/commons/thumb/5/5b/Carrefour_logo.svg/200px-Carrefour_logo.svg.png" style="height: 50px; filter: brightness(0) invert(1);">
        </div>
    </div>
""", unsafe_allow_html=True)

# --- BOTONES SUPERIORES ---
b1, b2, b3, b4, b5 = st.columns(5)
with b1: btn_1 = st.button("👥 CLIENTES", key="top_1", use_container_width=True)
with b2: btn_2 = st.button("📋 FALTANTES", key="top_2", use_container_width=True)
with b3: btn_3 = st.button("🚚 DOMICILIOS", key="top_3", use_container_width=True)
with b4: btn_4 = st.button("📊 INFORME", key="top_4", use_container_width=True)
with b5: st.link_button("🌐 PLANILLA MEC", "https://docs.google.com/spreadsheets/d/1v0Rls8fg_uIGfhA1t3CzINq3VfAUvPY3DY8_m_ZSmM8/edit#gid=0", use_container_width=True)

# --- CUERPO ---
col_izq, col_der = st.columns([1, 1], gap="large")

with col_izq:
    # --- TARJETA 1: CARGA CDP ---
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.markdown('<div class="card-title">📂 CARGAR EXCEL CDP (OPERACIONES)</div>', unsafe_allow_html=True)
    archivo_cdp = st.file_uploader("Subir CDP", type=["xlsx"], label_visibility="collapsed", key="cdp_upload")
    
    if archivo_cdp:
        df_raw = pd.read_excel(archivo_cdp)
        df_clean, fecha_tit = logic_clientes.motor_limpieza(df_raw)
        st.success(f"ARCHIVO LISTO: {fecha_tit}")
        
        # PROCESAMIENTO DE BOTONES 1, 2, 3
        if btn_1:
            pdf = logic_clientes.generar_pdf_clientes(df_clean, fecha_tit)
            st.download_button("📥 DESCARGAR PDF CLIENTES", bytes(pdf), f"Clientes_{fecha_tit}.pdf", use_container_width=True)
        if btn_2:
            pdf = logic_faltantes.generar_pdf_faltantes(df_clean, fecha_tit)
            st.download_button("📥 DESCARGAR PDF FALTANTES", bytes(pdf), f"Faltantes_{fecha_tit}.pdf", use_container_width=True)
        if btn_3:
            pdf = logic_domicilios.generar_pdf_domicilios(df_clean, fecha_tit)
            st.download_button("📥 DESCARGAR PDF RUTAS", bytes(pdf), f"Rutas_{fecha_tit}.pdf", use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

    # --- TARJETA 2: INFORME ---
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.markdown(f'<div class="card-title">📝 INFORME PARA MAÑANA ({manana_txt})</div>', unsafe_allow_html=True)
    archivo_inf = st.file_uploader("Subir CDP Mañana", type=["xlsx"], key="inf_upload", label_visibility="collapsed")
    obs = st.text_area("Observaciones:", height=80, placeholder="Novedades del turno aquí...")
    
    if btn_4:
        if archivo_inf:
            df_inf_raw = pd.read_excel(archivo_inf)
            df_inf_clean, fecha_inf_tit = logic_clientes.motor_limpieza(df_inf_raw)
            pdf_bytes = logic_informe.generar_pdf_informe(df_inf_clean, obs)
            st.download_button("📥 DESCARGAR REPORTE FINAL", pdf_bytes, f"Informe_{fecha_inf_tit}.pdf", use_container_width=True)
        else:
            st.warning("⚠️ Cargue el CDP de mañana primero.")
    st.markdown('</div>', unsafe_allow_html=True)

with col_der:
    # --- TARJETA 3: PANEL ---
    st.markdown('<div class="glass-card" style="min-height: 480px;">', unsafe_allow_html=True)
    st.markdown('<div class="card-title">📈 PANEL DE VISUALIZACIÓN</div>', unsafe_allow_html=True)
    
    if archivo_cdp:
        total_pedidos = len(df_clean)
        st.metric("PEDIDOS PROCESADOS", f"{total_pedidos}", delta="T268 Rosario")
        chart_data = pd.DataFrame({'Pedidos': [total_pedidos]}, index=['Hoy'])
        st.bar_chart(chart_data, color="#00d4ff")
    else:
        st.info("Suba un archivo para ver métricas reales.")
        st.area_chart(np.random.randint(40, 100, 10), color="#0066ff")
    st.markdown('</div>', unsafe_allow_html=True)

# --- FOOTER ---
st.markdown('<p style="text-align: center; color: rgba(255,255,255,0.3); font-size: 0.8em;">Central Logística T268 | Carrefour Online</p>', unsafe_allow_html=True)
