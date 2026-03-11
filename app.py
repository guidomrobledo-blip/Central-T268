import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import logic_clientes, logic_faltantes, logic_domicilios, logic_informe

# --- CONFIGURACIÓN DE FECHA ARGENTINA (UTC-3) ---
# Esto asegura que "hoy" y "mañana" coincidan con tu reloj en Rosario
fecha_ar_ahora = datetime.utcnow() - timedelta(hours=3)
hoy_ar = fecha_ar_ahora.date()
manana_ar_obj = hoy_ar + timedelta(days=1)
manana_txt = manana_ar_obj.strftime("%d/%m/%Y")

st.set_page_config(page_title="Central T268", layout="wide")

# Estilo para botones y diseño
st.markdown("""
    <style>
    div.stButton > button:first-child, div.stLinkButton > a {
        height: 3em; 
        font-weight: bold; 
        display: flex; 
        align-items: center; 
        justify-content: center; 
        text-decoration: none;
    }
    </style>
""", unsafe_allow_html=True)

st.title("🛒 Central Logística T268")

# Inicializar estados de sesión para que los cargadores no desaparezcan
if 'inf_activo' not in st.session_state:
    st.session_state.inf_activo = False

# --- SECCIÓN GENERAL (Botones 1, 2, 3) ---
st.subheader("📂 Procesamiento General")
archivo_cdp = st.file_uploader("Cargar Excel CDP para CLIENTES, FALTANTES o RUTAS", type=["xlsx"], key="main_uploader")

st.divider()

# --- PANEL DE BOTONES (Siempre visibles) ---
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

# --- LÓGICA DE BOTONES 1, 2 Y 3 (Usan el cargador principal) ---
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

# --- LÓGICA BOTÓN 4 (Cargador Exclusivo e Independiente) ---
if btn_4:
    st.session_state.inf_activo = True

if st.session_state.inf_activo:
    st.markdown("---")
    st.subheader("🚀 Procesador Exclusivo de Informe (Día Siguiente)")
    
    archivo_inf = st.file_uploader("Subir planilla para INFORME", type=["xlsx"], key="u_inf")
    
    if archivo_inf:
        df_inf_raw = pd.read_excel(archivo_inf)
        df_inf_clean, fecha_inf_tit = logic_clientes.motor_limpieza(df_inf_raw)
        
        # NORMALIZACIÓN Y VALIDACIÓN DE FECHA
        try:
            # Reemplazamos "/" por "-" para procesar uniformemente
            f_norm = fecha_inf_tit.replace("/", "-")
            # Detectamos si el año viene con 2 o 4 dígitos
            formato = "%d-%m-%Y" if len(f_norm.split("-")[-1]) == 4 else "%d-%m-%y"
            fecha_detectada_obj = datetime.strptime(f_norm, formato).date()
            
            if fecha_detectada_obj == manana_ar_obj:
                st.success(f"✅ Fecha confirmada: {fecha_detectada_obj.strftime('%d/%m/%Y')}")
                obs = st.text_area("📝 OBSERVACIONES PARA EL INFORME:", placeholder="Escriba aquí...")
                
                if st.button("GENERAR PDF INFORME", use_container_width=True):
                    pdf_bytes = logic_informe.generar_pdf_informe(df_inf_clean, obs)
                    st.download_button("📥 DESCARGAR INFORME", pdf_bytes, f"Informe_{fecha_inf_tit}.pdf", key="dl_inf_final")
            else:
                st.error("⚠️ Informe solo procesa pedidos del día siguiente.")
                st.info(f"Fecha en archivo: {fecha_detectada_obj.strftime('%d/%m/%Y')} | Requerida: {manana_txt}")
        
        except Exception as e:
            st.error(f"No se pudo validar la fecha: {fecha_inf_tit}")

# Mensajes de advertencia por falta de archivo
if (btn_1 or btn_2 or btn_3) and not archivo_cdp:
    st.warning("⚠️ Sube el archivo en el cargador superior para procesar las opciones 1, 2 o 3.")
