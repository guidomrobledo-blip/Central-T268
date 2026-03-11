import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import logic_clientes, logic_faltantes, logic_domicilios, logic_informe

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(
    page_title="Central T268", 
    page_icon="🛒", 
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- CONFIGURACIÓN DE FECHA ARGENTINA (UTC-3) ---
fecha_ar_ahora = datetime.utcnow() - timedelta(hours=3)
hoy_ar = fecha_ar_ahora.date()
manana_ar_obj = hoy_ar + timedelta(days=1)
manana_txt = manana_ar_obj.strftime("%d/%m/%Y")

# --- ESTILOS CSS PERSONALIZADOS ---
st.markdown("""
    <style>
    /* Tipografía y Colores Generales */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap');
    body { font-family: 'Inter', sans-serif; }
    
    /* Títulos */
    h1 { color: #1f2937; font-weight: 700; }
    h2 { color: #374151; font-weight: 600; }
    h3 { color: #4b5563; font-weight: 600; }
    
    /* Botones Principales */
    div.stButton > button {
        background-color: #3b82f6;
        color: white;
        border: none;
        border-radius: 8px;
        padding: 0.5rem 1rem;
        font-weight: 600;
        transition: all 0.3s ease;
    }
    div.stButton > button:hover {
        background-color: #2563eb;
        transform: translateY(-2px);
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    
    /* Botones de Descarga */
    div.stDownloadButton > button {
        background-color: #10b981;
        color: white;
        border: none;
        border-radius: 8px;
        font-weight: 600;
    }
    div.stDownloadButton > button:hover {
        background-color: #059669;
    }
    
    /* Contenedores de Tarjetas */
    .card {
        background-color: #f9fafb;
        border-radius: 12px;
        padding: 1.5rem;
        border: 1px solid #e5e7eb;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        margin-bottom: 1rem;
    }
    
    /* Separadores */
    hr { border: 1px solid #e5e7eb; margin: 2rem 0; }
    
    /* Enlaces */
    a { color: #3b82f6; text-decoration: none; }
    a:hover { text-decoration: underline; }
    
    /* Mensajes */
    .success-box { background-color: #d1fae5; border-left: 4px solid #10b981; padding: 1rem; border-radius: 4px; }
    .error-box { background-color: #fee2e2; border-left: 4px solid #ef4444; padding: 1rem; border-radius: 4px; }
    .warning-box { background-color: #fef3c7; border-left: 4px solid #f59e0b; padding: 1rem; border-radius: 4px; }
    </style>
""", unsafe_allow_html=True)

# --- HEADER ---
st.title("🛒 Central Logística T268")
st.markdown("### Gestión de Procesos Diarios")

# --- INICIALIZAR ESTADO ---
if 'inf_activo' not in st.session_state:
    st.session_state.inf_activo = False

# --- TABS DE NAVEGACIÓN ---
tab1, tab2, tab3, tab4 = st.tabs(["📦 Procesamiento General", "📊 Informe Diario", "🔗 Enlaces", "ℹ️ Ayuda"])

# ==========================================
# TAB 1: PROCESAMIENTO GENERAL
# ==========================================
with tab1:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.subheader("📂 Carga de Archivo Principal")
    st.markdown("Sube el archivo Excel CDP para generar los reportes de Clientes, Faltantes y Domicilios.")
    
    archivo_cdp = st.file_uploader("Cargar Excel CDP", type=["xlsx"], key="main_uploader")
    st.markdown('</div>', unsafe_allow_html=True)
    
    if archivo_cdp:
        df_raw = pd.read_excel(archivo_cdp)
        df_clean, fecha_tit = logic_clientes.motor_limpieza(df_raw)
        
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.subheader("🚀 Generar Reportes")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("🟢 1. CLIENTES", use_container_width=True):
                pdf = logic_clientes.generar_pdf_clientes(df_clean, fecha_tit)
                st.download_button("📥 Descargar PDF", bytes(pdf), f"Clientes_{fecha_tit}.pdf", key="dl_1")
        
        with col2:
            if st.button("🔵 2. FALTANTES", use_container_width=True):
                pdf = logic_faltantes.generar_pdf_faltantes(df_clean, fecha_tit)
                st.download_button("📥 Descargar PDF", bytes(pdf), f"Faltantes_{fecha_tit}.pdf", key="dl_2")
        
        with col3:
            if st.button("🟡 3. DOMICILIOS", use_container_width=True):
                pdf = logic_domicilios.generar_pdf_domicilios(df_clean, fecha_tit)
                st.download_button("📥 Descargar PDF", bytes(pdf), f"Ruta_{fecha_tit}.pdf", key="dl_3")
        
        st.markdown('</div>', unsafe_allow_html=True)

# ==========================================
# TAB 2: INFORME DIARIO
# ==========================================
with tab2:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.subheader("📋 Procesador Exclusivo de Informe")
    st.markdown("Este módulo procesa pedidos del **día siguiente**.")
    
    archivo_inf = st.file_uploader("Subir planilla para INFORME", type=["xlsx"], key="u_inf")
    
    if archivo_inf:
        df_inf_raw = pd.read_excel(archivo_inf)
        df_inf_clean, fecha_inf_tit = logic_clientes.motor_limpieza(df_inf_raw)
        
        try:
            f_norm = fecha_inf_tit.replace("/", "-")
            formato = "%d-%m-%Y" if len(f_norm.split("-")[-1]) == 4 else "%d-%m-%y"
            fecha_detectada_obj = datetime.strptime(f_norm, formato).date()
            
            if fecha_detectada_obj == manana_ar_obj:
                st.markdown('<div class="success-box">', unsafe_allow_html=True)
                st.success(f"✅ Fecha confirmada: {fecha_detectada_obj.strftime('%d/%m/%Y')}")
                st.markdown('</div>')
                
                obs = st.text_area("📝 OBSERVACIONES PARA EL INFORME:", placeholder="Escriba aquí las observaciones...")
                
                if st.button("GENERAR PDF INFORME", use_container_width=True):
                    pdf_bytes = logic_informe.generar_pdf_informe(df_inf_clean, obs)
                    st.download_button("📥 DESCARGAR INFORME", pdf_bytes, f"Informe_{fecha_inf_tit}.pdf", key="dl_inf_final")
            else:
                st.markdown('<div class="error-box">', unsafe_allow_html=True)
                st.error("⚠️ Informe solo procesa pedidos del día siguiente.")
                st.info(f"Fecha en archivo: {fecha_detectada_obj.strftime('%d/%m/%Y')} | Requerida: {manana_txt}")
                st.markdown('</div>')
        
        except Exception as e:
            st.markdown('<div class="error-box">', unsafe_allow_html=True)
            st.error(f"No se pudo validar la fecha: {fecha_inf_tit}")
            st.markdown('</div>')
    
    st.markdown('</div>', unsafe_allow_html=True)

# ==========================================
# TAB 3: ENLACES
# ==========================================
with tab3:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.subheader("🔗 Herramientas Externas")
    
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("### 📄 Planilla MEC")
        st.link_button("🌐 Abrir Planilla", 
                       "https://docs.google.com/spreadsheets/d/1v0Rls8fg_uIGfhA1t3CzINq3VfAUvPY3DY8_m_ZSmM8/edit?gid=0#gid=0", 
                       use_container_width=True)
    with col2:
        st.markdown("### 📞 Contacto")
        st.markdown("Soporte Técnico: soporte@t268.com")
    
    st.markdown('</div>', unsafe_allow_html=True)

# ==========================================
# TAB 4: AYUDA
# ==========================================
with tab4:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.subheader("ℹ️ Guía de Uso")
    st.markdown("""
    1. **Procesamiento General:** Sube el archivo CDP y selecciona qué reporte deseas generar.
    2. **Informe Diario:** Solo procesa archivos con fecha del día siguiente.
    3. **Enlaces:** Accede a herramientas externas desde esta pestaña.
    """)
    st.markdown('</div>', unsafe_allow_html=True)
