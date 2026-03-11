import streamlit as st
import pandas as pd
import numpy as np
import pydeck as pdk
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

# --- CSS MEJORADO ---
st.markdown("""
    <style>
    .stApp { background-color: #f1f4f9; }
    
    /* Cabecera */
    .title-text {
        color: #003876;
        font-weight: 900;
        font-size: 2.5em;
        margin: 0;
        text-transform: uppercase;
    }
    
    /* Botones Cápsula con Colores de la Idea Original */
    div.stButton > button {
        border-radius: 50px !important;
        height: 3.5em !important;
        font-weight: bold !important;
        border: none !important;
        box-shadow: 0 4px 10px rgba(0,0,0,0.1) !important;
        transition: all 0.3s ease;
    }
    
    /* Colores específicos para emular idea_central-T268.jpg */
    button[key="top_1"] { border-bottom: 4px solid #4CAF50 !important; } /* Verde Clientes */
    button[key="top_2"] { border-bottom: 4px solid #2196F3 !important; } /* Azul Faltantes */
    button[key="top_3"] { border-bottom: 4px solid #FFC107 !important; } /* Amarillo Rutas */
    button[key="top_4"] { border-bottom: 4px solid #FF5722 !important; } /* Naranja Informe */

    .card-label {
        color: #003876;
        font-weight: bold;
        font-size: 1em;
        margin-bottom: 10px;
        display: block;
        text-transform: uppercase;
    }

    /* REHABILITAR MENÚ (Quitamos el visibility:hidden que lo borró) */
    header { visibility: visible !important; }
    </style>
""", unsafe_allow_html=True)

# --- CABECERA ---
with st.container():
    c_logo, c_title = st.columns([1, 4])
    with c_logo:
        # Probamos con el logo que tengas disponible
        logo_path = "carrefour+logo.png" if os.path.exists("carrefour+logo.png") else "logo.png.webp"
        if os.path.exists(logo_path):
            st.image(logo_path, width=180)
    with c_title:
        st.markdown('<h1 class="title-text">CENTRAL LOGÍSTICA T268</h1>', unsafe_allow_html=True)
        st.markdown(f"**VENTAS ONLINE ROSARIO** | Gestión Operativa del {hoy_ar.strftime('%d/%m/%Y')}")

st.write("")

# --- FILA DE BOTONES SUPERIORES ---
b1, b2, b3, b4, b5 = st.columns(5)
with b1: btn_1 = st.button("👥 Clientes", key="top_1", use_container_width=True)
with b2: btn_2 = st.button("📋 Faltantes", key="top_2", use_container_width=True)
with b3: btn_3 = st.button("🚚 Domicilios", key="top_3", use_container_width=True)
with b4: btn_4 = st.button("📊 Informe", key="top_4", use_container_width=True)
with b5: st.link_button("🌐 Planilla MEC", "https://docs.google.com/spreadsheets/d/1v0Rls8fg_uIGfhA1t3CzINq3VfAUvPY3DY8_m_ZSmM8/edit#gid=0", use_container_width=True)

st.divider()

# --- DASHBOARD EQUILIBRADO 50/50 ---
col_izq, col_der = st.columns([1, 1], gap="large")

with col_izq:
    st.markdown('<span class="card-label">📂 OPERACIONES Y CARGA</span>', unsafe_allow_html=True)
    archivo_cdp = st.file_uploader("Cargar CDP del día (Excel)", type=["xlsx"])
    
    if archivo_cdp:
        df_raw = pd.read_excel(archivo_cdp)
        df_clean, fecha_tit = logic_clientes.motor_limpieza(df_raw)
        st.success(f"CDP Cargado: {fecha_tit}")
        
        # Lógica de descarga según el botón superior presionado
        if btn_1:
            pdf = logic_clientes.generar_pdf_clientes(df_clean, fecha_tit)
            st.download_button("📥 DESCARGAR CLIENTES", bytes(pdf), f"Clientes_{fecha_tit}.pdf")
        if btn_2:
            pdf = logic_faltantes.generar_pdf_faltantes(df_clean, fecha_tit)
            st.download_button("📥 DESCARGAR FALTANTES", bytes(pdf), f"Faltantes_{fecha_tit}.pdf")
        if btn_3:
            pdf = logic_domicilios.generar_pdf_domicilios(df_clean, fecha_tit)
            st.download_button("📥 DESCARGAR RUTAS", bytes(pdf), f"Rutas_{fecha_tit}.pdf")

    st.markdown("---")
    st.markdown('<span class="card-label">📝 PROCESADOR DE INFORME (MAÑANA)</span>', unsafe_allow_html=True)
    archivo_inf = st.file_uploader(f"Subir CDP Mañana ({manana_txt})", type=["xlsx"])
    if archivo_inf:
        df_inf_raw = pd.read_excel(archivo_inf)
        df_inf_clean, fecha_inf_tit = logic_clientes.motor_limpieza(df_inf_raw)
        obs = st.text_area("Observaciones:", placeholder="Escriba aquí las novedades...")
        if st.button("GENERAR REPORTE", use_container_width=True):
            pdf_bytes = logic_informe.generar_pdf_informe(df_inf_clean, obs)
            st.download_button("📥 DESCARGAR INFORME", pdf_bytes, f"Informe_{fecha_inf_tit}.pdf")

with col_der:
    st.markdown('<span class="card-label">🗺️ NAVEGACIÓN Y MONITOREO ROSARIO</span>', unsafe_allow_html=True)
    
    # Buscador (Visual)
    direc = st.text_input("🔍 Buscar dirección:", placeholder="Ej: Bv. Oroño y Pellegrini")
    
    # MAPA: Cambiado a CartoDB Voyager (Más color, sin necesidad de Token)
    # Estilo 'voyager' es colorido y detallado.
    view_state = pdk.ViewState(
        latitude=-32.9442, 
        longitude=-60.6505, 
        zoom=12, 
        pitch=0
    )
    
    st.pydeck_chart(pdk.Deck(
        map_style='https://basemaps.cartocdn.com/gl/voyager-gl-style/style.json',
        initial_view_state=view_state,
        layers=[
            pdk.Layer(
                "ScatterplotLayer",
                data=[{"lng": -60.6505, "lat": -32.9442}],
                get_position='[lng, lat]',
                get_color='[0, 56, 118, 200]', # Azul Carrefour
                get_radius=300,
            )
        ]
    ))
    
    st.write("")
    st.markdown('<span class="card-label">📈 VOLUMEN DE PEDIDOS</span>', unsafe_allow_html=True)
    if archivo_cdp:
        count_data = pd.DataFrame({'Pedidos': [len(df_clean)]}, index=['Hoy'])
        st.bar_chart(count_data, color="#003876")
    else:
        st.info("Cargue un archivo para ver métricas.")
