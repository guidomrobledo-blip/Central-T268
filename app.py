import streamlit as st
import pandas as pd
import numpy as np
import pydeck as pdk
from datetime import datetime, timedelta
import logic_clientes, logic_faltantes, logic_domicilios, logic_informe
import os
import requests
import json

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

# --- GEOCODIFICACIÓN ROSARIO EXCLUSIVA ---
def geocodificar_rosario(direccion):
    """
    Geocodifica una dirección restringida a Rosario, Santa Fe
    Retorna: (latitud, longitud) o None si no encuentra
    """
    if not direccion or len(direccion.strip()) < 3:
        return None
    
    try:
        # Añadimos "Rosario, Santa Fe, Argentina" para restringir la búsqueda
        direccion_completa = f"{direccion}, Rosario, Santa Fe, Argentina"
        
        url = f"https://nominatim.openstreetmap.org/search?format=json&q={direccion_completa}&countrycodes=ar&addressdetails=1"
        response = requests.get(url, headers={"User-Agent": "CentralLogisticaT268/1.0"})
        data = response.json()
        
        if data and len(data) > 0:
            # Verificamos que el resultado sea de Rosario
            display_name = data[0].get("display_name", "")
            if "Rosario" in display_name:
                return {
                    "lat": float(data[0]["lat"]),
                    "lon": float(data[0]["lon"]),
                    "display_name": display_name
                }
    except Exception as e:
        st.error(f"Error al geocodificar: {str(e)}")
    
    return None

# --- CSS MEJORADO ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700;900&display=swap');
    
    .stApp { 
        background-color: #f8fafc; 
        font-family: 'Inter', sans-serif;
    }
    
    .title-text {
        color: #003876;
        font-weight: 900;
        font-size: 2.5em;
        margin: 0;
        text-transform: uppercase;
        letter-spacing: -1px;
    }
    
    .date-text {
        color: #64748b;
        font-weight: 500;
        font-size: 1em;
        margin-top: 5px;
    }
    
    div.stButton > button {
        border-radius: 50px !important;
        height: 3.5em !important;
        font-weight: bold !important;
        border: none !important;
        box-shadow: 0 4px 10px rgba(0,0,0,0.1) !important;
        transition: all 0.3s ease;
        font-family: 'Inter', sans-serif;
    }
    
    button[key="top_1"] { border-bottom: 4px solid #4CAF50 !important; }
    button[key="top_2"] { border-bottom: 4px solid #2196F3 !important; }
    button[key="top_3"] { border-bottom: 4px solid #FFC107 !important; }
    button[key="top_4"] { border-bottom: 4px solid #FF5722 !important; }

    div.stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 15px rgba(0,0,0,0.15) !important;
    }

    .card-label {
        color: #003876;
        font-weight: 700;
        font-size: 1.1em;
        margin-bottom: 15px;
        display: block;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        border-left: 4px solid #003876;
        padding-left: 10px;
    }

    .stTextInput > div > div > input {
        border-radius: 8px !important;
        border: 1px solid #cbd5e1 !important;
        padding: 10px !important;
    }
    
    .stFileUploader {
        border-radius: 8px !important;
        border: 1px dashed #cbd5e1 !important;
        background-color: #ffffff !important;
    }
    
    .stSuccess {
        background-color: #d1fae5 !important;
        border-left: 4px solid #10b981 !important;
        padding: 10px !important;
        border-radius: 4px !important;
    }
    
    .deckgl-view {
        border-radius: 12px !important;
        overflow: hidden !important;
        box-shadow: 0 4px 10px rgba(0,0,0,0.1) !important;
    }
    
    .stBarChart {
        border-radius: 8px !important;
        overflow: hidden !important;
    }
    
    hr { border: 1px solid #e2e8f0; margin: 2rem 0; }
    
    /* Mensaje de búsqueda */
    .search-result {
        background-color: #dbeafe;
        border-left: 4px solid #3b82f6;
        padding: 10px;
        border-radius: 4px;
        margin-top: 10px;
        font-size: 0.9em;
    }
    
    .search-error {
        background-color: #fee2e2;
        border-left: 4px solid #ef4444;
        padding: 10px;
        border-radius: 4px;
        margin-top: 10px;
        font-size: 0.9em;
    }
    
    .search-info {
        background-color: #fef3c7;
        border-left: 4px solid #f59e0b;
        padding: 10px;
        border-radius: 4px;
        margin-top: 10px;
        font-size: 0.9em;
    }
    </style>
""", unsafe_allow_html=True)

# --- CABECERA ---
with st.container():
    c_logo, c_title = st.columns([1, 4])
    with c_logo:
        logo_path = "carrefour+logo.png" if os.path.exists("carrefour+logo.png") else "logo.png.webp"
        if os.path.exists(logo_path):
            st.image(logo_path, width=180)
    with c_title:
        st.markdown('<h1 class="title-text">CENTRAL LOGÍSTICA T268</h1>', unsafe_allow_html=True)
        st.markdown(f'<p class="date-text">VENTAS ONLINE ROSARIO | Gestión Operativa del {hoy_ar.strftime("%d/%m/%Y")}</p>', unsafe_allow_html=True)

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
    
    # --- BUSCADOR DE DIRECCIONES (ROSARIO EXCLUSIVO) ---
    st.markdown("**🔍 Buscar Dirección en Rosario**")
    st.markdown('<div class="search-info">📍 Solo direcciones de Rosario, Santa Fe</div>', unsafe_allow_html=True)
    direc = st.text_input("", placeholder="Ej: Bv. Oroño 1234, Rosario", key="map_search")
    
    # Estado para guardar la ubicación encontrada
    if 'map_location' not in st.session_state:
        st.session_state.map_location = None
    
    # Al presionar Enter (el input de Streamlit lo detecta automáticamente)
    if direc and st.session_state.map_location != direc:
        st.session_state.map_location = direc
        result = geocodificar_rosario(direc)
        
        if result:
            st.session_state.map_coords = {
                "lat": result["lat"],
                "lon": result["lon"]
            }
            st.markdown(f'<div class="search-result">✅ {result["display_name"]}</div>', unsafe_allow_html=True)
        else:
            st.markdown(f'<div class="search-error">❌ No se encontró esa dirección en Rosario. Intenta ser más específico (ej: "Bv. Oroño y Pellegrini")</div>', unsafe_allow_html=True)
            st.session_state.map_coords = None

    # --- MAPA ---
    # Configuración inicial
    if st.session_state.get("map_coords"):
        view_state = pdk.ViewState(
            latitude=st.session_state.map_coords["lat"],
            longitude=st.session_state.map_coords["lon"],
            zoom=15,  # Zoom más cercano para ver calles
            pitch=0
        )
    else:
        view_state = pdk.ViewState(
            latitude=-32.9442, 
            longitude=-60.6505, 
            zoom=12, 
            pitch=0
        )
    
    # Capa de puntos (marcador de ubicación)
    if st.session_state.get("map_coords"):
        data = [{"lng": st.session_state.map_coords["lon"], "lat": st.session_state.map_coords["lat"]}]
    else:
        data = [{"lng": -60.6505, "lat": -32.9442}]
    
    st.pydeck_chart(pdk.Deck(
        map_style='https://basemaps.cartocdn.com/gl/voyager-gl-style/style.json',
        initial_view_state=view_state,
        layers=[
            pdk.Layer(
                "ScatterplotLayer",
                data=data,
                get_position='[lng, lat]',
                get_color='[0, 56, 118, 200]',
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
