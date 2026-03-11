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

# --- CSS PROFESIONAL Y VISIBILIDAD ---
st.markdown("""
    <style>
    .stApp { background-color: #f8f9fa; }
    
    .header-box {
        background-color: white;
        padding: 15px 30px;
        border-radius: 15px;
        display: flex;
        align-items: center;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05);
        margin-bottom: 20px;
        border-bottom: 5px solid #003876;
    }
    
    .header-title { color: #003876 !important; font-size: 2.2em !important; font-weight: bold !important; margin: 0 !important; }
    .header-subtitle { color: #333 !important; font-size: 1.1em !important; margin: 0 !important; }

    .section-title {
        color: #1a202c !important;
        font-weight: bold !important;
        font-size: 1.2em !important;
        margin-bottom: 12px !important;
        display: block;
        border-bottom: 2px solid #e2e8f0;
        padding-bottom: 5px;
    }

    /* Botones de Acción */
    div.stButton > button {
        background-color: #1a202c !important;
        color: white !important;
        border-radius: 10px;
        height: 3.5em;
        font-weight: bold;
        border: none;
        transition: 0.3s ease;
    }
    
    div.stButton > button:hover {
        background-color: #003876 !important;
        transform: translateY(-2px);
    }

    /* Botón de Descarga */
    div.stDownloadButton > button {
        background-color: #28a745 !important;
        color: white !important;
        border-radius: 10px;
        font-weight: bold;
        width: 100%;
    }
    </style>
""", unsafe_allow_html=True)

# --- CABECERA ---
with st.container():
    c_img, c_txt = st.columns([1, 5])
    with c_img:
        if os.path.exists("carrefour+logo.png"):
            st.image("carrefour+logo.png", width=130)
    with c_txt:
        st.markdown('<h1 class="header-title">Central Logística Carrefour Online</h1>', unsafe_allow_html=True)
        st.markdown(f'<p class="header-subtitle">Tienda 268 - Rosario | Sistema de Gestión de Ventas</p>', unsafe_allow_html=True)

# --- VARIABLES DE ESTADO ---
if 'historico_pedidos' not in st.session_state:
    st.session_state.historico_pedidos = {}

# --- LAYOUT PRINCIPAL ---
col_izq, col_der = st.columns([1.3, 2])

with col_izq:
    st.markdown('<span class="section-title">📂 CARGA DE PLANILLAS</span>', unsafe_allow_html=True)
    archivo_cdp = st.file_uploader("Subir CDP del Día (Excel)", type=["xlsx"], key="main_up")
    
    st.markdown("---")
    st.markdown('<span class="section-title">🛠️ PROCESAMIENTO</span>', unsafe_allow_html=True)
    
    if archivo_cdp:
        df_raw = pd.read_excel(archivo_cdp)
        df_clean, fecha_tit = logic_clientes.motor_limpieza(df_raw)
        
        # Guardar conteo para el gráfico
        st.session_state.historico_pedidos[fecha_tit] = len(df_clean)
        
        # Botones de Funciones
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
        st.info("Suba un archivo CDP para comenzar.")

    # --- SECCIÓN INFORME (BOTÓN 4) ---
    if st.session_state.get('inf_activo', False) or (archivo_cdp and locals().get('btn_informe')):
        st.session_state.inf_activo = True
        st.markdown(f"""<div style="background-color:#fff3e0; padding:15px; border-radius:10px; border-left:5px solid #ff9800; margin-top:15px;">
            <p style="color:#e65100; font-weight:bold; margin:0;">🚀 Generar Informe para: {manana_txt}</p></div>""", unsafe_allow_html=True)
        
        archivo_inf = st.file_uploader("Subir CDP de Mañana", type=["xlsx"], key="inf_up")
        if archivo_inf:
            df_inf_raw = pd.read_excel(archivo_inf)
            df_inf_clean, fecha_inf_tit = logic_clientes.motor_limpieza(df_inf_raw)
            
            # Validación de fecha de Rosario
            try:
                f_norm = fecha_inf_tit.replace("/", "-")
                fmt = "%d-%m-%Y" if len(f_norm.split("-")[-1]) == 4 else "%d-%m-%y"
                f_obj = datetime.strptime(f_norm, fmt).date()
                
                if f_obj == manana_ar_obj:
                    st.success(f"Archivo correcto: {fecha_inf_tit}")
                    obs = st.text_area("Observaciones del Informe:")
                    if st.button("CREAR PDF INFORME", use_container_width=True):
                        pdf_inf = logic_informe.generar_pdf_informe(df_inf_clean, obs)
                        st.download_button("📥 DESCARGAR INFORME", pdf_inf, f"Informe_{fecha_inf_tit}.pdf")
                else:
                    st.error(f"Se requiere fecha {manana_txt}. Detectada: {fecha_inf_tit}")
            except:
                st.error("Error en formato de fecha.")

with col_der:
    st.markdown('<span class="section-title">🗺️ UBICACIÓN OPERATIVA (ROSARIO)</span>', unsafe_allow_html=True)
    
    # Mapa Corregido (Style OpenStreetMap - No requiere API Key)
    view_state = pdk.ViewState(latitude=-32.9442, longitude=-60.6505, zoom=12, pitch=0)
    st.pydeck_chart(pdk.Deck(
        map_style=None, # Usa estilo por defecto de Pydeck/OSM
        initial_view_state=view_state,
        layers=[]
    ))
    
    st.markdown('<span class="section-title">📈 VOLUMEN REAL DE PEDIDOS</span>', unsafe_allow_html=True)
    
    if st.session_state.historico_pedidos:
        # Gráfico simple de total de pedidos por fecha subida
        chart_data = pd.DataFrame(
            list(st.session_state.historico_pedidos.items()),
            columns=['Fecha', 'Total Pedidos']
        ).set_index('Fecha')
        
        st.bar_chart(chart_data)
        
        # Métrica destacada
        total_hoy = list(st.session_state.historico_pedidos.values())[-1]
        st.metric("Pedidos Cargados Hoy", f"{total_hoy} unidades")
    else:
        st.info("El gráfico mostrará el conteo de filas una vez procesado el CDP.")
