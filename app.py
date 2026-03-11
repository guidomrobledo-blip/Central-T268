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

# --- CSS: FONDO LOGÍSTICO Y DISEÑO COMPACTO ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;700;900&display=swap');
    
    /* Fondo con Marca de Agua Logística */
    .stApp {
        background: linear-gradient(135deg, rgba(255,255,255,0.9) 0%, rgba(241,244,249,0.9) 100%), 
                    url('https://www.transparenttextures.com/patterns/cubes.png');
        font-family: 'Inter', sans-serif;
    }

    /* Cabecera Estilo Banner */
    .header-box {
        background-color: white;
        padding: 10px 25px;
        border-radius: 15px;
        box-shadow: 0 4px 15px rgba(0,56,118,0.1);
        border-left: 8px solid #003876;
        margin-bottom: 15px;
    }

    .title-main { color: #003876; font-weight: 900; font-size: 2.2em; margin: 0; text-transform: uppercase; }
    .subtitle-main { color: #555; font-size: 1em; margin: 0; }

    /* Botones Vedette (Estilo Cápsula Colorida) */
    div.stButton > button {
        border-radius: 12px !important;
        height: 4.5em !important;
        font-weight: 800 !important;
        font-size: 1em !important;
        text-transform: uppercase !important;
        border: none !important;
        color: white !important;
        box-shadow: 0 4px 12px rgba(0,0,0,0.15) !important;
        transition: all 0.2s ease;
    }

    /* Colores por botón según bosquejo */
    button[key="top_1"] { background: #4CAF50 !important; } /* Verde */
    button[key="top_2"] { background: #1E88E5 !important; } /* Azul */
    button[key="top_3"] { background: #FFB300 !important; } /* Amarillo */
    button[key="top_4"] { background: #F4511E !important; } /* Naranja */
    button[key="top_5"] { background: #37474F !important; } /* Gris Oscuro */

    div.stButton > button:hover { transform: scale(1.03); filter: brightness(1.1); }

    /* Contenedores de Carga */
    .section-card {
        background: rgba(255,255,255,0.8);
        padding: 15px;
        border-radius: 15px;
        border: 1px solid #e0e6ed;
        backdrop-filter: blur(5px);
    }
    
    .card-title {
        color: #003876;
        font-weight: 700;
        font-size: 0.9em;
        margin-bottom: 10px;
        display: block;
        text-transform: uppercase;
    }

    /* Reducción de espacios para "Single Screen" */
    .block-container { padding-top: 1rem !important; padding-bottom: 0rem !important; }
    iframe { height: 350px !important; }
    </style>
""", unsafe_allow_html=True)

# --- HEADER ---
with st.container():
    c_img, c_txt = st.columns([1, 5])
    with c_img:
        logo_path = "carrefour+logo.png" if os.path.exists("carrefour+logo.png") else "logo.png.webp"
        if os.path.exists(logo_path):
            st.image(logo_path, width=150)
    with c_txt:
        st.markdown(f'<div class="header-box"><p class="title-main">🛒 CENTRAL LOGÍSTICA T268</p><p class="subtitle-main">Rosario - Gestión de Ventas Online | {hoy_ar.strftime("%d/%m/%Y")}</p></div>', unsafe_allow_html=True)

# --- FILA DE BOTONES "VEDETTE" ---
st.write("")
b1, b2, b3, b4, b5 = st.columns(5)
with b1: btn_1 = st.button("👥 CLIENTES", key="top_1", use_container_width=True)
with b2: btn_2 = st.button("📋 FALTANTES", key="top_2", use_container_width=True)
with b3: btn_3 = st.button("🚚 DOMICILIOS", key="top_3", use_container_width=True)
with b4: btn_4 = st.button("📊 INFORME", key="top_4", use_container_width=True)
with b5: st.link_button("🌐 PLANILLA MEC", "https://docs.google.com/spreadsheets/d/1v0Rls8fg_uIGfhA1t3CzINq3VfAUvPY3DY8_m_ZSmM8/edit#gid=0", use_container_width=True)

# --- CUERPO PRINCIPAL ---
st.write("")
col_izq, col_der = st.columns([1, 1], gap="medium")

with col_izq:
    st.markdown('<div class="section-card">', unsafe_allow_html=True)
    st.markdown('<span class="card-title">📂 CARGAR EXCEL CDP (OPERACIONES)</span>', unsafe_allow_html=True)
    archivo_cdp = st.file_uploader("", type=["xlsx"], label_visibility="collapsed")
    
    if archivo_cdp:
        df_raw = pd.read_excel(archivo_cdp)
        df_clean, fecha_tit = logic_clientes.motor_limpieza(df_raw)
        st.success(f"CDP CARGADO: {fecha_tit}")
        
        # Lógica de descarga (Se activa al tocar el botón superior correspondiente)
        if btn_1:
            pdf = logic_clientes.generar_pdf_clientes(df_clean, fecha_tit)
            st.download_button("📥 DESCARGAR LISTA CLIENTES", bytes(pdf), f"Clientes_{fecha_tit}.pdf", use_container_width=True)
        if btn_2:
            pdf = logic_faltantes.generar_pdf_faltantes(df_clean, fecha_tit)
            st.download_button("📥 DESCARGAR LISTA FALTANTES", bytes(pdf), f"Faltantes_{fecha_tit}.pdf", use_container_width=True)
        if btn_3:
            pdf = logic_domicilios.generar_pdf_domicilios(df_clean, fecha_tit)
            st.download_button("📥 DESCARGAR RUTAS", bytes(pdf), f"Rutas_{fecha_tit}.pdf", use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

    st.write("")
    st.markdown('<div class="section-card">', unsafe_allow_html=True)
    st.markdown(f'<span class="card-title">📝 INFORME PARA MAÑANA ({manana_txt})</span>', unsafe_allow_html=True)
    archivo_inf = st.file_uploader("Subir CDP Mañana", type=["xlsx"], key="inf", label_visibility="collapsed")
    obs = st.text_area("Observaciones:", height=80, placeholder="Novedades del turno...")
    if btn_4 and archivo_inf:
        df_inf_raw = pd.read_excel(archivo_inf)
        df_inf_clean, fecha_inf_tit = logic_clientes.motor_limpieza(df_inf_raw)
        pdf_bytes = logic_informe.generar_pdf_informe(df_inf_clean, obs)
        st.download_button("📥 DESCARGAR REPORTE FINAL", pdf_bytes, f"Informe_{fecha_inf_tit}.pdf", use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

with col_der:
    st.markdown('<div class="section-card" style="height: 100%;">', unsafe_allow_html=True)
    st.markdown('<span class="card-title">📈 PANEL DE VISUALIZACIÓN DE VENTAS</span>', unsafe_allow_html=True)
    
    if archivo_cdp:
        # Métrica grande
        total_pedidos = len(df_clean)
        st.metric("TOTAL PEDIDOS HOY", f"{total_pedidos} Unidades", delta="En proceso")
        
        # Gráfico estético
        chart_data = pd.DataFrame({'Pedidos': [total_pedidos]}, index=['T268 Rosario'])
        st.bar_chart(chart_data, color="#003876")
        
        st.caption("Gráfico dinámico actualizado según el archivo CDP cargado.")
    else:
        st.info("Cargue un archivo CDP para visualizar las métricas del día.")
        # Simulación visual para no dejar el espacio en blanco (como en el bosquejo)
        st.line_chart(np.random.randn(10, 1), height=200)
    st.markdown('</div>', unsafe_allow_html=True)
