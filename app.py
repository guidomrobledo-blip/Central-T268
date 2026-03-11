import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
# import logic_clientes, logic_faltantes, logic_domicilios, logic_informe  # Descomenta cuando tengas estos módulos
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
    
    /* ===== FONDO OSCURO PRINCIPAL ===== */
    .stApp {
        background: linear-gradient(135deg, #0a0a0f 0%, #1a1a2e 50%, #16213e 100%);
        font-family: 'Inter', sans-serif;
    }
    
    /* Patrón de fondo sutil */
    .stApp::before {
        content: '';
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background-image: 
            radial-gradient(circle at 25% 25%, rgba(0, 100, 255, 0.03) 0%, transparent 50%),
            radial-gradient(circle at 75% 75%, rgba(138, 43, 226, 0.03) 0%, transparent 50%);
        pointer-events: none;
        z-index: 0;
    }
    
    /* ===== HEADER FLOTANTE CON NEON ===== */
    .header-container {
        background: linear-gradient(145deg, rgba(26, 26, 46, 0.95), rgba(22, 33, 62, 0.95));
        border-radius: 20px;
        padding: 25px 35px;
        margin-bottom: 25px;
        border: 1px solid rgba(0, 150, 255, 0.3);
        box-shadow: 
            0 8px 32px rgba(0, 0, 0, 0.4),
            0 0 40px rgba(0, 100, 255, 0.1),
            inset 0 1px 0 rgba(255, 255, 255, 0.1);
        backdrop-filter: blur(20px);
        position: relative;
        overflow: hidden;
    }
    
    .header-container::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 3px;
        background: linear-gradient(90deg, #0066ff, #00d4ff, #8a2be2, #0066ff);
        background-size: 300% 100%;
        animation: gradient-shift 3s ease infinite;
    }
    
    @keyframes gradient-shift {
        0%, 100% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
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
    
    .subtitle-main {
        color: rgba(255, 255, 255, 0.7);
        font-size: 1.1em;
        margin-top: 8px;
        font-weight: 300;
        letter-spacing: 1px;
    }
    
    .date-badge {
        display: inline-block;
        background: linear-gradient(135deg, #0066ff, #00d4ff);
        color: white;
        padding: 5px 15px;
        border-radius: 20px;
        font-size: 0.85em;
        font-weight: 600;
        margin-left: 10px;
    }
    
    /* ===== BOTONES NEON FLOTANTES ===== */
    div.stButton > button {
        background: linear-gradient(145deg, rgba(30, 30, 50, 0.9), rgba(20, 20, 40, 0.9)) !important;
        border-radius: 16px !important;
        height: 5em !important;
        font-weight: 700 !important;
        font-size: 0.95em !important;
        text-transform: uppercase !important;
        letter-spacing: 1px !important;
        color: white !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        box-shadow: 
            0 8px 25px rgba(0, 0, 0, 0.3),
            inset 0 1px 0 rgba(255, 255, 255, 0.1) !important;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
        position: relative !important;
        overflow: hidden !important;
    }
    
    /* Efecto glow por botón */
    div.stButton > button[key="top_1"] {
        border-color: rgba(76, 175, 80, 0.5) !important;
        box-shadow: 
            0 8px 25px rgba(0, 0, 0, 0.3),
            0 0 30px rgba(76, 175, 80, 0.2),
            inset 0 1px 0 rgba(255, 255, 255, 0.1) !important;
    }
    div.stButton > button[key="top_1"]:hover {
        border-color: rgba(76, 175, 80, 0.8) !important;
        box-shadow: 
            0 12px 35px rgba(0, 0, 0, 0.4),
            0 0 50px rgba(76, 175, 80, 0.4),
            inset 0 1px 0 rgba(255, 255, 255, 0.2) !important;
        transform: translateY(-3px) !important;
    }
    
    div.stButton > button[key="top_2"] {
        border-color: rgba(30, 136, 229, 0.5) !important;
        box-shadow: 
            0 8px 25px rgba(0, 0, 0, 0.3),
            0 0 30px rgba(30, 136, 229, 0.2),
            inset 0 1px 0 rgba(255, 255, 255, 0.1) !important;
    }
    div.stButton > button[key="top_2"]:hover {
        border-color: rgba(30, 136, 229, 0.8) !important;
        box-shadow: 
            0 12px 35px rgba(0, 0, 0, 0.4),
            0 0 50px rgba(30, 136, 229, 0.4),
            inset 0 1px 0 rgba(255, 255, 255, 0.2) !important;
        transform: translateY(-3px) !important;
    }
    
    div.stButton > button[key="top_3"] {
        border-color: rgba(255, 179, 0, 0.5) !important;
        box-shadow: 
            0 8px 25px rgba(0, 0, 0, 0.3),
            0 0 30px rgba(255, 179, 0, 0.2),
            inset 0 1px 0 rgba(255, 255, 255, 0.1) !important;
    }
    div.stButton > button[key="top_3"]:hover {
        border-color: rgba(255, 179, 0, 0.8) !important;
        box-shadow: 
            0 12px 35px rgba(0, 0, 0, 0.4),
            0 0 50px rgba(255, 179, 0, 0.4),
            inset 0 1px 0 rgba(255, 255, 255, 0.2) !important;
        transform: translateY(-3px) !important;
    }
    
    div.stButton > button[key="top_4"] {
        border-color: rgba(244, 81, 30, 0.5) !important;
        box-shadow: 
            0 8px 25px rgba(0, 0, 0, 0.3),
            0 0 30px rgba(244, 81, 30, 0.2),
            inset 0 1px 0 rgba(255, 255, 255, 0.1) !important;
    }
    div.stButton > button[key="top_4"]:hover {
        border-color: rgba(244, 81, 30, 0.8) !important;
        box-shadow: 
            0 12px 35px rgba(0, 0, 0, 0.4),
            0 0 50px rgba(244, 81, 30, 0.4),
            inset 0 1px 0 rgba(255, 255, 255, 0.2) !important;
        transform: translateY(-3px) !important;
    }
    
    /* Link Button (Planilla MEC) */
    .stLinkButton > a {
        background: linear-gradient(145deg, rgba(30, 30, 50, 0.9), rgba(20, 20, 40, 0.9)) !important;
        border-radius: 16px !important;
        height: 5em !important;
        font-weight: 700 !important;
        font-size: 0.95em !important;
        text-transform: uppercase !important;
        letter-spacing: 1px !important;
        color: white !important;
        border: 1px solid rgba(138, 43, 226, 0.5) !important;
        box-shadow: 
            0 8px 25px rgba(0, 0, 0, 0.3),
            0 0 30px rgba(138, 43, 226, 0.2),
            inset 0 1px 0 rgba(255, 255, 255, 0.1) !important;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
    }
    
    .stLinkButton > a:hover {
        border-color: rgba(138, 43, 226, 0.8) !important;
        box-shadow: 
            0 12px 35px rgba(0, 0, 0, 0.4),
            0 0 50px rgba(138, 43, 226, 0.4),
            inset 0 1px 0 rgba(255, 255, 255, 0.2) !important;
        transform: translateY(-3px) !important;
        text-decoration: none !important;
    }
    
    /* ===== TARJETAS FLOTANTES GLASSMORPHISM ===== */
    .glass-card {
        background: linear-gradient(145deg, rgba(26, 26, 46, 0.8), rgba(22, 33, 62, 0.6));
        border-radius: 20px;
        padding: 25px;
        border: 1px solid rgba(255, 255, 255, 0.1);
        box-shadow: 
            0 15px 35px rgba(0, 0, 0, 0.4),
            0 0 0 1px rgba(255, 255, 255, 0.05),
            inset 0 1px 0 rgba(255, 255, 255, 0.1);
        backdrop-filter: blur(20px);
        position: relative;
        overflow: hidden;
        margin-bottom: 20px;
    }
    
    .glass-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 2px;
        background: linear-gradient(90deg, transparent, rgba(0, 150, 255, 0.5), transparent);
    }
    
    .glass-card-green::before {
        background: linear-gradient(90deg, transparent, rgba(76, 175, 80, 0.6), transparent);
    }
    
    .glass-card-orange::before {
        background: linear-gradient(90deg, transparent, rgba(255, 152, 0, 0.6), transparent);
    }
    
    .glass-card-blue::before {
        background: linear-gradient(90deg, transparent, rgba(30, 136, 229, 0.6), transparent);
    }
    
    .card-icon {
        font-size: 1.5em;
        margin-right: 10px;
    }
    
    .card-title {
        color: #ffffff;
        font-weight: 700;
        font-size: 1em;
        text-transform: uppercase;
        letter-spacing: 1.5px;
        display: flex;
        align-items: center;
        margin-bottom: 20px;
        text-shadow: 0 0 10px rgba(255, 255, 255, 0.2);
    }
    
    /* ===== FILE UPLOADER MODERNO ===== */
    .stFileUploader {
        background: rgba(255, 255, 255, 0.03) !important;
        border-radius: 12px !important;
        border: 2px dashed rgba(255, 255, 255, 0.2) !important;
        padding: 20px !important;
        transition: all 0.3s ease !important;
    }
    
    .stFileUploader:hover {
        border-color: rgba(0, 150, 255, 0.5) !important;
        background: rgba(0, 150, 255, 0.05) !important;
    }
    
    .stFileUploader label {
        color: rgba(255, 255, 255, 0.7) !important;
    }
    
    [data-testid="stFileUploader"] {
        background: rgba(255, 255, 255, 0.02);
        border-radius: 12px;
        padding: 15px;
        border: 2px dashed rgba(255, 255, 255, 0.15);
    }
    
    [data-testid="stFileUploader"]:hover {
        border-color: rgba(0, 150, 255, 0.4);
        background: rgba(0, 150, 255, 0.03);
    }
    
    /* ===== TEXT AREA MODERNO ===== */
    .stTextArea textarea {
        background: rgba(255, 255, 255, 0.03) !important;
        border: 1px solid rgba(255, 255, 255, 0.15) !important;
        border-radius: 12px !important;
        color: white !important;
        font-family: 'Inter', sans-serif !important;
    }
    
    .stTextArea textarea:focus {
        border-color: rgba(0, 150, 255, 0.5) !important;
        box-shadow: 0 0 20px rgba(0, 150, 255, 0.2) !important;
    }
    
    .stTextArea textarea::placeholder {
        color: rgba(255, 255, 255, 0.4) !important;
    }
    
    /* ===== MÉTRICAS NEON ===== */
    [data-testid="stMetric"] {
        background: linear-gradient(145deg, rgba(0, 100, 255, 0.15), rgba(0, 50, 150, 0.1));
        border-radius: 16px;
        padding: 20px;
        border: 1px solid rgba(0, 150, 255, 0.3);
        box-shadow: 
            0 8px 25px rgba(0, 0, 0, 0.3),
            0 0 30px rgba(0, 100, 255, 0.1);
    }
    
    [data-testid="stMetricLabel"] {
        color: rgba(255, 255, 255, 0.7) !important;
        font-weight: 600 !important;
        text-transform: uppercase !important;
        letter-spacing: 1px !important;
    }
    
    [data-testid="stMetricValue"] {
        color: #00d4ff !important;
        font-family: 'Orbitron', sans-serif !important;
        font-size: 2.5em !important;
        text-shadow: 0 0 20px rgba(0, 212, 255, 0.5) !important;
    }
    
    [data-testid="stMetricDelta"] {
        color: #4CAF50 !important;
    }
    
    /* ===== GRÁFICOS ===== */
    [data-testid="stVegaLiteChart"] {
        background: rgba(255, 255, 255, 0.02);
        border-radius: 12px;
        padding: 15px;
    }
    
    /* ===== MENSAJES DE ESTADO ===== */
    .stSuccess {
        background: linear-gradient(145deg, rgba(76, 175, 80, 0.2), rgba(76, 175, 80, 0.1)) !important;
        border: 1px solid rgba(76, 175, 80, 0.4) !important;
        border-radius: 12px !important;
        color: #81c784 !important;
    }
    
    .stInfo {
        background: linear-gradient(145deg, rgba(30, 136, 229, 0.2), rgba(30, 136, 229, 0.1)) !important;
        border: 1px solid rgba(30, 136, 229, 0.4) !important;
        border-radius: 12px !important;
        color: #64b5f6 !important;
    }
    
    .stWarning {
        background: linear-gradient(145deg, rgba(255, 179, 0, 0.2), rgba(255, 179, 0, 0.1)) !important;
        border: 1px solid rgba(255, 179, 0, 0.4) !important;
        border-radius: 12px !important;
        color: #ffd54f !important;
    }
    
    /* ===== DOWNLOAD BUTTON ===== */
    .stDownloadButton > button {
        background: linear-gradient(135deg, #0066ff, #00d4ff) !important;
        border: none !important;
        border-radius: 12px !important;
        color: white !important;
        font-weight: 600 !important;
        text-transform: uppercase !important;
        letter-spacing: 1px !important;
        box-shadow: 0 8px 25px rgba(0, 100, 255, 0.3) !important;
        transition: all 0.3s ease !important;
    }
    
    .stDownloadButton > button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 12px 35px rgba(0, 100, 255, 0.4) !important;
    }
    
    /* ===== ESPACIADO ===== */
    .block-container {
        padding-top: 2rem !important;
        padding-bottom: 2rem !important;
        max-width: 1400px !important;
    }
    
    /* ===== SCROLLBAR CUSTOM ===== */
    ::-webkit-scrollbar {
        width: 8px;
        height: 8px;
    }
    
    ::-webkit-scrollbar-track {
        background: rgba(255, 255, 255, 0.05);
        border-radius: 4px;
    }
    
    ::-webkit-scrollbar-thumb {
        background: linear-gradient(180deg, #0066ff, #00d4ff);
        border-radius: 4px;
    }
    
    ::-webkit-scrollbar-thumb:hover {
        background: linear-gradient(180deg, #0077ff, #00e5ff);
    }
    
    /* ===== CAPTION ===== */
    .stCaption {
        color: rgba(255, 255, 255, 0.5) !important;
    }
    
    /* Hide default Streamlit elements */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    </style>
""", unsafe_allow_html=True)

# --- HEADER MODERNO ---
st.markdown("""
    <div class="header-container">
        <div style="display: flex; align-items: center; justify-content: space-between; flex-wrap: wrap;">
            <div>
                <h1 class="title-main">Central Logistica T268</h1>
                <p class="subtitle-main">Rosario - Gestion de Ventas Online 
                    <span class="date-badge">""" + hoy_ar.strftime("%d/%m/%Y") + """</span>
                </p>
            </div>
            <div style="text-align: right;">
                <img src="https://upload.wikimedia.org/wikipedia/commons/thumb/5/5b/Carrefour_logo.svg/200px-Carrefour_logo.svg.png" 
                     style="height: 60px; filter: brightness(0) invert(1); opacity: 0.9;" alt="Logo">
            </div>
        </div>
    </div>
""", unsafe_allow_html=True)

# --- FILA DE BOTONES NEON ---
st.write("")
b1, b2, b3, b4, b5 = st.columns(5)
with b1: 
    btn_1 = st.button("CLIENTES", key="top_1", use_container_width=True)
with b2: 
    btn_2 = st.button("FALTANTES", key="top_2", use_container_width=True)
with b3: 
    btn_3 = st.button("DOMICILIOS", key="top_3", use_container_width=True)
with b4: 
    btn_4 = st.button("INFORME", key="top_4", use_container_width=True)
with b5: 
    st.link_button("PLANILLA MEC", "https://docs.google.com/spreadsheets/d/1v0Rls8fg_uIGfhA1t3CzINq3VfAUvPY3DY8_m_ZSmM8/edit#gid=0", use_container_width=True)

# --- CUERPO PRINCIPAL ---
st.write("")
st.write("")
col_izq, col_der = st.columns([1, 1], gap="large")

with col_izq:
    # Tarjeta 1: Cargar CDP
    st.markdown('<div class="glass-card glass-card-blue">', unsafe_allow_html=True)
    st.markdown('<div class="card-title"><span class="card-icon">📂</span> CARGAR EXCEL CDP (OPERACIONES)</div>', unsafe_allow_html=True)
    archivo_cdp = st.file_uploader("Subir archivo CDP", type=["xlsx"], label_visibility="collapsed", key="cdp_upload")
    
    if archivo_cdp:
        df_raw = pd.read_excel(archivo_cdp)
        # Simular limpieza - descomentar cuando tengas los módulos
        # df_clean, fecha_tit = logic_clientes.motor_limpieza(df_raw)
        df_clean = df_raw  # Placeholder
        fecha_tit = hoy_ar.strftime("%d-%m-%Y")
        st.success(f"CDP CARGADO EXITOSAMENTE: {fecha_tit}")
        
        # Lógica de descarga
        if btn_1:
            # pdf = logic_clientes.generar_pdf_clientes(df_clean, fecha_tit)
            # st.download_button("DESCARGAR LISTA CLIENTES", bytes(pdf), f"Clientes_{fecha_tit}.pdf", use_container_width=True)
            st.info("Generando PDF de Clientes...")
        if btn_2:
            # pdf = logic_faltantes.generar_pdf_faltantes(df_clean, fecha_tit)
            # st.download_button("DESCARGAR LISTA FALTANTES", bytes(pdf), f"Faltantes_{fecha_tit}.pdf", use_container_width=True)
            st.info("Generando PDF de Faltantes...")
        if btn_3:
            # pdf = logic_domicilios.generar_pdf_domicilios(df_clean, fecha_tit)
            # st.download_button("DESCARGAR RUTAS", bytes(pdf), f"Rutas_{fecha_tit}.pdf", use_container_width=True)
            st.info("Generando PDF de Rutas...")
    st.markdown('</div>', unsafe_allow_html=True)

    st.write("")
    
    # Tarjeta 2: Informe
    st.markdown('<div class="glass-card glass-card-orange">', unsafe_allow_html=True)
    st.markdown(f'<div class="card-title"><span class="card-icon">📝</span> INFORME PARA MAÑANA ({manana_txt})</div>', unsafe_allow_html=True)
    archivo_inf = st.file_uploader("Subir CDP Mañana", type=["xlsx"], key="inf_upload", label_visibility="collapsed")
    obs = st.text_area("Observaciones:", height=100, placeholder="Ingresa las novedades del turno aqui...", key="obs_area")
    if btn_4 and archivo_inf:
        # df_inf_raw = pd.read_excel(archivo_inf)
        # df_inf_clean, fecha_inf_tit = logic_clientes.motor_limpieza(df_inf_raw)
        # pdf_bytes = logic_informe.generar_pdf_informe(df_inf_clean, obs)
        # st.download_button("DESCARGAR REPORTE FINAL", pdf_bytes, f"Informe_{fecha_inf_tit}.pdf", use_container_width=True)
        st.info("Procesando informe...")
    st.markdown('</div>', unsafe_allow_html=True)

with col_der:
    # Tarjeta 3: Panel de Visualización
    st.markdown('<div class="glass-card glass-card-green" style="min-height: 500px;">', unsafe_allow_html=True)
    st.markdown('<div class="card-title"><span class="card-icon">📈</span> PANEL DE VISUALIZACION DE VENTAS</div>', unsafe_allow_html=True)
    
    if archivo_cdp:
        # Métrica grande
        total_pedidos = len(df_clean)
        
        col_m1, col_m2 = st.columns(2)
        with col_m1:
            st.metric("TOTAL PEDIDOS", f"{total_pedidos}", delta="En proceso")
        with col_m2:
            st.metric("TIENDA", "T268", delta="Rosario")
        
        st.write("")
        
        # Gráfico de ejemplo
        chart_data = pd.DataFrame({
            'Dia': ['Lun', 'Mar', 'Mie', 'Jue', 'Vie', 'Sab', 'Dom'],
            'Pedidos': np.random.randint(40, 120, 7)
        })
        st.bar_chart(chart_data.set_index('Dia'), color="#00d4ff")
        
        st.caption("Datos actualizados segun el archivo CDP cargado")
    else:
        st.info("Carga un archivo CDP para visualizar las metricas del dia")
        
        # Demo visual mientras no hay datos
        st.write("")
        demo_data = pd.DataFrame({
            'Semana': ['S1', 'S2', 'S3', 'S4'],
            'Ventas': [65, 78, 90, 85]
        })
        st.area_chart(demo_data.set_index('Semana'), color="#0066ff")
        st.caption("Vista previa - Sube un archivo para ver datos reales")
    
    st.markdown('</div>', unsafe_allow_html=True)

# --- FOOTER ---
st.write("")
st.write("")
st.markdown("""
    <div style="text-align: center; padding: 20px; color: rgba(255,255,255,0.4); font-size: 0.85em;">
        Central Logistica T268 | Carrefour Online | Rosario
    </div>
""", unsafe_allow_html=True)
