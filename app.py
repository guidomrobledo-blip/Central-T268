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

# --- CSS AVANZADO: REPLICANDO EL DISEÑO ORIGINAL ---
st.markdown("""
    <style>
    /* Fondo y tipografía */
    .stApp { background-color: #f1f4f9; }
    
    /* Cabecera */
    .header-container {
        display: flex;
        align-items: center;
        margin-bottom: 20px;
    }
    
    .title-text {
        color: #003876;
        font-weight: 900;
        font-size: 2.8em;
        margin: 0;
        line-height: 1;
        text-transform: uppercase;
    }
    
    /* Botones Superiores Estilo Cápsula */
    div.stButton > button {
        border-radius: 50px !important;
        height: 3.2em !important;
        font-weight: bold !important;
        border: none !important;
        box-shadow: 0 4px 10px rgba(0,0,0,0.1) !important;
        transition: all 0.3s ease;
        text-transform: uppercase;
        font-size: 0.85em !important;
    }
    
    /* Colores para los botones */
    div.stButton > button[key^="top_"] { background-color: white !important; color: #333 !important; }
    div.stButton > button[key^="top_"]:hover { background-color: #003876 !important; color: white !important; }

    /* Cards del Dashboard */
    .dashboard-card {
        background-color: white;
        padding: 25px;
        border-radius: 20px;
        box-shadow: 0 10px 25px rgba(0,0,0,0.05);
        margin-bottom: 20px;
        border: 1px solid #eef1f6;
    }
    
    .card-label {
        color: #003876;
        font-weight: bold;
        font-size: 1.1em;
        margin-bottom: 15px;
        display: block;
        text-transform: uppercase;
        letter-spacing: 1px;
    }

    /* Ocultar elementos estándar de Streamlit */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    </style>
""", unsafe_allow_html=True)

# --- CABECERA ---
with st.container():
    c_logo, c_title = st.columns([1, 4])
    with c_logo:
        if os.path.exists("carrefour+logo.png"):
            st.image("carrefour+logo.png", width=180)
    with c_title:
        st.markdown('<h1 class="title-text">CENTRAL LOGÍSTICA T268</h1>', unsafe_allow_html=True)
        st.markdown(f"**VENTAS ONLINE ROSARIO** | Gestión Operativa del {hoy_ar.strftime('%d/%m/%Y')}")

st.write("")

# --- FILA DE BOTONES SUPERIORES (SIMETRÍA ORIGINAL) ---
b1, b2, b3, b4, b5 = st.columns(5)
with b1: btn_1 = st.button("👥 Clientes", key="top_1", use_container_width=True)
with b2: btn_2 = st.button("📋 Faltantes", key="top_2", use_container_width=True)
with b3: btn_3 = st.button("🚚 Domicilios", key="top_3", use_container_width=True)
with b4: btn_4 = st.button("📊 Informe", key="top_4", use_container_width=True)
with b5: st.link_button("🌐 Planilla MEC", "https://docs.google.com/spreadsheets/d/1v0Rls8fg_uIGfhA1t3CzINq3VfAUvPY3DY8_m_ZSmM8/edit#gid=0", use_container_width=True)

st.divider()

# =========================================================
# --- DASHBOARD PRINCIPAL (PROPORCIÓN 50/50) ---
# =========================================================
col_izq, col_der = st.columns([1, 1], gap="large")

with col_izq:
    st.markdown('<span class="card-label">📂 OPERACIONES Y CARGA</span>', unsafe_allow_html=True)
    with st.container():
        archivo_cdp = st.file_uploader("Cargar CDP del día (Excel)", type=["xlsx"], key="main_cdp")
        
        if archivo_cdp:
            df_raw = pd.read_excel(archivo_cdp)
            df_clean, fecha_tit = logic_clientes.motor_limpieza(df_raw)
            st.success(f"CDP Cargado: {fecha_tit}")
            
            # Descargas anidadas a los botones superiores
            if btn_1:
                pdf = logic_clientes.generar_pdf_clientes(df_clean, fecha_tit)
                st.download_button("📥 DESCARGAR LISTA CLIENTES", bytes(pdf), f"Clientes_{fecha_tit}.pdf")
            if btn_2:
                pdf = logic_faltantes.generar_pdf_faltantes(df_clean, fecha_tit)
                st.download_button("📥 DESCARGAR LISTA FALTANTES", bytes(pdf), f"Faltantes_{fecha_tit}.pdf")
            if btn_3:
                pdf = logic_domicilios.generar_pdf_domicilios(df_clean, fecha_tit)
                st.download_button("📥 DESCARGAR RUTAS", bytes(pdf), f"Rutas_{fecha_tit}.pdf")

    st.markdown("---")
    st.markdown('<span class="card-label">📝 PROCESADOR DE INFORME (MAÑANA)</span>', unsafe_allow_html=True)
    with st.container():
        archivo_inf = st.file_uploader(f"Subir CDP para Mañana ({manana_txt})", type=["xlsx"], key="inf_up")
        if archivo_inf:
            df_inf_raw = pd.read_excel(archivo_inf)
            df_inf_clean, fecha_inf_tit = logic_clientes.motor_limpieza(df_inf_raw)
            obs = st.text_area("Observaciones del turno:", height=100)
            if st.button("GENERAR REPORTE FINAL", use_container_width=True):
                pdf_bytes = logic_informe.generar_pdf_informe(df_inf_clean, obs)
                st.download_button("📥 DESCARGAR INFORME", pdf_bytes, f"Informe_{fecha_inf_tit}.pdf")

with col_der:
    st.markdown('<span class="card-label">🗺️ NAVEGACIÓN Y MONITOREO</span>', unsafe_allow_html=True)
    
    # BUSCADOR DE DIRECCIONES
    direc = st.text_input("🔍 Buscar dirección en Rosario:", placeholder="Ej: Av. Pellegrini 1250")
    
    # MAPA CON MÁS COLOR Y CONTRASTE
    view_state = pdk.ViewState(
        latitude=-32.9442, 
        longitude=-60.6505, 
        zoom=12.5, 
        pitch=40
    )
    
    st.pydeck_chart(pdk.Deck(
        map_style='mapbox://styles/mapbox/streets-v11', # Estilo con color y calles claras
        initial_view_state=view_state,
        layers=[
            pdk.Layer(
                "ScatterplotLayer",
                data=[{"lng": -60.6505, "lat": -32.9442}],
                get_position='[lng, lat]',
                get_color='[200, 30, 0, 160]',
                get_radius=250,
            )
        ]
    ))
    
    st.markdown('<span class="card-label">📈 VOLUMEN DE PEDIDOS</span>', unsafe_allow_html=True)
    if archivo_cdp:
        # Gráfico real funcional
        count_data = pd.DataFrame({'Total': [len(df_clean)]}, index=['Pedidos Hoy'])
        st.bar_chart(count_data, color="#003876")
        st.metric("Total Unidades", len(df_clean))
    else:
        st.info("A la espera de datos del CDP...")
