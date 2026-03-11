import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import logic_clientes, logic_faltantes, logic_domicilios, logic_informe

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(
    page_title="Central Carrefour Online T268",
    page_icon="🛒",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- AJUSTE DE FECHA ARGENTINA (UTC-3) ---
fecha_ar_ahora = datetime.utcnow() - timedelta(hours=3)
hoy_ar = fecha_ar_ahora.date()
manana_ar_obj = hoy_ar + timedelta(days=1)
manana_txt = manana_ar_obj.strftime("%d/%m/%Y")

# --- CSS PROFESIONAL (ESTILO CARREFOUR ONLINE) ---
st.markdown("""
    <style>
    /* Fondo general */
    .stApp { background-color: #f4f7f6; }

    /* Cabecera Blanca para Logo Nítido */
    .header-box {
        background-color: white;
        padding: 20px 30px;
        border-radius: 15px;
        display: flex;
        align-items: center;
        box-shadow: 0 4px 12px rgba(0,0,0,0.08);
        margin-bottom: 25px;
        border-left: 8px solid #003876;
    }
    
    .header-text-container {
        margin-left: 25px;
    }
    
    .header-title {
        color: #003876 !important;
        font-size: 2.2em !important;
        font-weight: bold !important;
        margin: 0 !important;
        line-height: 1.2;
    }
    
    .header-subtitle {
        color: #555 !important;
        font-size: 1.1em !important;
        margin: 0 !important;
    }

    /* Botones Estilo Oscuro 'Premium' con Texto Blanco */
    div.stButton > button {
        background-color: #1a202c !important;
        color: white !important;
        border-radius: 12px;
        height: 3.8em;
        width: 100%;
        border: none;
        font-weight: bold;
        font-size: 1.05em;
        transition: all 0.3s ease;
        box-shadow: 2px 2px 5px rgba(0,0,0,0.1);
    }
    
    div.stButton > button:hover {
        background-color: #2d3748 !important;
        transform: translateY(-2px);
        box-shadow: 4px 8px 15px rgba(0,0,0,0.15);
    }

    /* Estilo de la Tarjeta del Informe (Botón 4) */
    .info-card {
        background-color: #fff9f0;
        border-left: 6px solid #ff9800;
        padding: 20px;
        border-radius: 15px;
        margin-top: 20px;
        box-shadow: 0 2px 10px rgba(0,0,0,0.05);
    }
    
    .info-card-title {
        color: #e65100;
        font-weight: bold;
        font-size: 1.4em;
        margin-top: 0;
    }
    </style>
""", unsafe_allow_html=True)

# --- INICIALIZAR ESTADOS DE SESIÓN ---
if 'inf_activo' not in st.session_state:
    st.session_state.inf_activo = False

# =========================================================
# --- CABECERA CORPORATIVA ---
# =========================================================
logo_carrefour = "https://upload.wikimedia.org/wikipedia/en/thumb/5/5b/Carrefour_logo.svg/1024px-Carrefour_logo.svg.png"

st.markdown(f"""
    <div class="header-box">
        <img src="{logo_carrefour}" width="90">
        <div class="header-text-container">
            <h1 class="header-title">Central Logística Carrefour Online</h1>
            <p class="header-subtitle">Tienda 268 - Rosario, Santa Fe</p>
        </div>
    </div>
""", unsafe_allow_html=True)

# =========================================================
# --- CARGADOR DE ARCHIVO CDP (GENERAL) ---
# =========================================================
st.subheader("📂 CARGAR EXCEL CDP (Operaciones del Día)")
archivo_cdp = st.file_uploader("", type=["xlsx"], key="main_up", help="Sube el archivo CDP para procesar CLIENTES, FALTANTES o RUTAS.")

st.divider()

# =========================================================
# --- PANEL DE BOTONES ---
# =========================================================
c1, c2, c3, c4, c5 = st.columns(5)

with c1: btn_1 = st.button("👥 1. CLIENTES", use_container_width=True)
with c2: btn_2 = st.button("🔍 2. FALTANTES", use_container_width=True)
with c3: btn_3 = st.button("🚚 3. DOMICILIOS", use_container_width=True)
with c4: btn_4 = st.button("📊 4. INFORME", use_container_width=True)
with c5: st.link_button("🌐 5. PLANILLA MEC", "https://docs.google.com/spreadsheets/d/1v0Rls8fg_uIGfhA1t3CzINq3VfAUvPY3DY8_m_ZSmM8/edit#gid=0", use_container_width=True)

# --- LÓGICA BOTONES 1, 2 Y 3 ---
if archivo_cdp:
    df_raw = pd.read_excel(archivo_cdp)
    df_clean, fecha_tit = logic_clientes.motor_limpieza(df_raw)

    if btn_1:
        with c1:
            pdf = logic_clientes.generar_pdf_clientes(df_clean, fecha_tit)
            st.download_button("📥 DESCARGAR", bytes(pdf), f"Clientes_{fecha_tit}.pdf", key="dl_1")
    
    if btn_2:
        with c2:
            pdf = logic_faltantes.generar_pdf_faltantes(df_clean, fecha_tit)
            st.download_button("📥 DESCARGAR", bytes(pdf), f"Faltantes_{fecha_tit}.pdf", key="dl_2")
            
    if btn_3:
        with c3:
            pdf = logic_domicilios.generar_pdf_domicilios(df_clean, fecha_tit)
            st.download_button("📥 DESCARGAR", bytes(pdf), f"Ruta_{fecha_tit}.pdf", key="dl_3")

# =========================================================
# --- SECCIÓN INFORME (BOTÓN 4) ---
# =========================================================
if btn_4:
    st.session_state.inf_activo = True

if st.session_state.inf_activo:
    st.markdown(f"""
        <div class="info-card">
            <h3 class="info-card-title">🚀 Procesador de Informe (Mañana: {manana_txt})</h3>
            <p style="color: #666;">Sube el archivo CDP exclusivo para el informe del día siguiente.</p>
        </div>
    """, unsafe_allow_html=True)
    
    archivo_inf = st.file_uploader("Subir planilla para INFORME", type=["xlsx"], key="inf_up")
    
    if archivo_inf:
        df_inf_raw = pd.read_excel(archivo_inf)
        df_inf_clean, fecha_inf_tit = logic_clientes.motor_limpieza(df_inf_raw)
        
        try:
            f_norm = fecha_inf_tit.replace("/", "-")
            formato = "%d-%m-%Y" if len(f_norm.split("-")[-1]) == 4 else "%d-%m-%y"
            fecha_detectada_obj = datetime.strptime(f_norm, formato).date()
            
            if fecha_detectada_obj == manana_ar_obj:
                st.success(f"✅ Fecha confirmada: {fecha_detectada_obj.strftime('%d/%m/%Y')}")
                obs = st.text_area("📝 OBSERVACIONES:", placeholder="Escriba aquí las notas del informe...")
                
                if st.button("GENERAR PDF INFORME", use_container_width=True):
                    pdf_bytes = logic_informe.generar_pdf_informe(df_inf_clean, obs)
                    st.download_button("📥 DESCARGAR INFORME", pdf_bytes, f"Informe_{fecha_inf_tit}.pdf", key="dl_inf_final")
            else:
                st.error(f"⚠️ El archivo detectado es del {fecha_detectada_obj.strftime('%d/%m/%Y')}. Se requiere el del día {manana_txt}.")
        
        except Exception as e:
            st.error(f"Error al procesar la fecha: {fecha_inf_tit}")

# Mensaje de advertencia
if (btn_1 or btn_2 or btn_3) and not archivo_cdp:
    st.warning("⚠️ Sube el archivo CDP arriba para habilitar la descarga.")
