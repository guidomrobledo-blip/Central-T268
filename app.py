import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
# Importamos las librerías de lógica que ya tienes funcionando
import logic_clientes, logic_faltantes, logic_domicilios, logic_informe

# --- CONFIGURACIÓN DE PÁGINA (Pestaña del Navegador) ---
st.set_page_config(
    page_title="Central Carrefour Online T268",
    page_icon="🛒", # Icono de carrito en la pestaña
    layout="wide",   # Usar todo el ancho de la pantalla
    initial_sidebar_state="collapsed" # Ocultar barra lateral por defecto
)

# --- CONFIGURACIÓN DE FECHA ARGENTINA (UTC-3) ---
# Esto asegura que "hoy" y "mañana" coincidan con tu reloj en Rosario
fecha_ar_ahora = datetime.utcnow() - timedelta(hours=3)
hoy_ar = fecha_ar_ahora.date()
manana_ar_obj = hoy_ar + timedelta(days=1)
manana_txt = manana_ar_obj.strftime("%d/%m/%Y")

# --- DISEÑO PROFESIONAL (CSS CUSTOM) ---
# Aquí definimos estilos para que la app no parezca la estándar de Streamlit
st.markdown("""
    <style>
    /* 1. Fondo general y tipografía base */
    .stApp {
        background-color: #f4f7f6; /* Un gris muy tenue, limpio */
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    }

    /* 2. Estilo de la Cabecera (Logo y Título) */
    .header-container {
        display: flex;
        align-items: center;
        background-color: white;
        padding: 15px 25px;
        border-radius: 15px;
        margin-bottom: 25px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.03);
    }
    
    .header-logo {
        width: 130px; /* Ajuste para el logo de Carrefour */
        margin-right: 20px;
    }
    
    .header-text-container {
        display: flex;
        flex-direction: column;
    }
    
    .header-title {
        color: #003876; /* Azul Carrefour */
        font-size: 2.2em;
        font-weight: bold;
        margin: 0;
    }
    
    .header-subtitle {
        color: #757575;
        font-size: 1.1em;
        margin: 0;
        margin-top: -5px;
    }

    /* 3. Estilo de los Botones Principales (Sombras, bordes, hover) */
    div.stButton > button {
        border-radius: 12px;
        height: 3.8em;
        width: 100%;
        border: 1px solid #e0e0e0;
        transition: all 0.3s ease; /* Efecto suave */
        box-shadow: 2px 2px 5px rgba(0,0,0,0.04);
        font-weight: bold;
        font-size: 1.05em;
    }
    
    /* Efecto "levantado" al pasar el mouse */
    div.stButton > button:hover {
        transform: translateY(-3px);
        box-shadow: 5px 5px 12px rgba(0,0,0,0.08);
        border: 1px solid #d0d0d0;
    }

    /* 4. Estilo de las "Cards" (Contenedores de carga y visualización) */
    .css-1r6slb0, .stFileUploader, .stTextArea { /* Selectores internos de Streamlit */
        background-color: white;
        padding: 20px;
        border-radius: 15px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.02);
        border: 1px solid #eaeaea;
    }
    
    /* Títulos dentro de las Cards */
    .card-title {
        color: #333;
        font-weight: bold;
        font-size: 1.3em;
        margin-bottom: 15px;
    }

    /* 5. Estilo especial para la tarjeta del Informe (Botón 4) */
    .info-card {
        background-color: #fff9f0; /* Un naranja muy tenue */
        border-left: 6px solid #ff9800; /* Borde naranja fuerte */
        padding: 20px;
        border-radius: 15px;
        margin-top: 20px;
    }
    
    .info-card-title {
        color: #e65100;
        font-weight: bold;
        font-size: 1.4em;
        margin-top: 0;
    }
    </style>
""", unsafe_allow_html=True)

# --- INICIALIZAR ESTADOS DE SESIÓN (Para persistencia) ---
if 'inf_activo' not in st.session_state:
    st.session_state.inf_activo = False

# =========================================================
# --- SECCIÓN 1: CABECERA CORPORATIVA CON LOGO ---
# =========================================================
with st.container():
    # Usamos una URL pública y segura del logo de Carrefour. 
    # Si tienes el archivo local, úsalo con st.image() normal.
    logo_url = "https://upload.wikimedia.org/wikipedia/en/thumb/5/5b/Carrefour_logo.svg/1200px-Carrefour_logo.svg.png"
    
    st.markdown(f"""
        <div class="header-container">
            <img src="{logo_url}" class="header-logo">
            <div class="header-text-container">
                <h1 class="header-title">Central Logística T268</h1>
                <p class="header-subtitle">Gestión de Ventas Online - Rosario, AR</p>
            </div>
        </div>
    """, unsafe_allow_html=True)

# =========================================================
# --- SECCIÓN 2: CARGADOR DE ARCHIVO PRINCIPAL (CDP) ---
# =========================================================
# Usamos columnas para centrar el cargador
_, col_cargador, _ = st.columns([1, 2, 1])

with col_cargador:
    st.markdown('<p class="card-title">📂 CARGAR EXCEL CDP (Operaciones del Día)</p>', unsafe_allow_html=True)
    archivo_cdp = st.file_uploader("", type=["xlsx"], key="main_uploader", help="Sube el archivo CDP de ventas online para procesar las opciones 1, 2 o 3.")

st.markdown("<br>", unsafe_allow_html=True) # Espaciado

# =========================================================
# --- SECCIÓN 3: PANEL DE BOTONES PRINCIPALES ---
# =========================================================
st.markdown("---")
# Dibujamos las 5 columnas
c1, c2, c3, c4, c5 = st.columns(5)

# Definimos los iconos (puedes usar emojis o iconos de FontAwesome)
with c1: btn_1 = st.button("👥 1. CLIENTES", use_container_width=True)
with c2: btn_2 = st.button("🔍 2. FALTANTES", use_container_width=True)
with c3: btn_3 = st.button("🚚 3. DOMICILIOS", use_container_width=True)
with c4: btn_4 = st.button("📊 4. INFORME", use_container_width=True)
with c5:
    st.link_button("🌐 5. PLANILLA MEC", 
                   "https://docs.google.com/spreadsheets/d/1v0Rls8fg_uIGfhA1t3CzINq3VfAUvPY3DY8_m_ZSmM8/edit?gid=0#gid=0", 
                   use_container_width=True)

# --- LÓGICA DE PROCESAMIENTO (Botones 1, 2, 3) ---
# Esta parte se mantiene igual, solo ajustamos la ubicación de descarga
if archivo_cdp:
    # Usamos un st.spinner() para dar feedback visual de carga
    with st.spinner("Procesando datos del CDP..."):
        df_raw = pd.read_excel(archivo_cdp)
        df_clean, fecha_tit = logic_clientes.motor_limpieza(df_raw)

        # Ubicamos la descarga justo debajo del botón correspondiente
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

# =========================================================
# --- SECCIÓN 4: LÓGICA EXCLUSIVA DEL INFORME (BOTÓN 4) ---
# =========================================================
# Activamos la sección si se pulsa el botón o ya estaba activa
if btn_4:
    st.session_state.inf_activo = True

# Si está activo, mostramos la "Card" de Informe Especial
if st.session_state.inf_activo:
    st.markdown("---")
    
    # Abrimos el contenedor estilizado (Card)
    st.markdown(f"""
        <div class="info-card">
            <h3 class="info-card-title">🚀 Procesador Exclusivo de Informe (Día Siguiente)</h3>
            <p style="color: #666; margin-bottom: 20px;">Sube el archivo CDP con fecha de mañana ({manana_txt}) para generar el informe de estado.</p>
        </div>
    """, unsafe_allow_html=True)
    
    # Volvemos a usar columnas para centrar los elementos de carga
    _, col_inf, _ = st.columns([1, 2, 1])
    
    with col_inf:
        archivo_inf = st.file_uploader("", type=["xlsx"], key="u_inf")
        
        if archivo_inf:
            with st.spinner("Validando fecha del archivo..."):
                df_inf_raw = pd.read_excel(archivo_inf)
                df_inf_clean, fecha_inf_tit = logic_clientes.motor_limpieza(df_inf_raw)
                
                # NORMALIZACIÓN Y VALIDACIÓN DE FECHA (Mantenemos tu lógica segura)
                try:
                    # Reemplazamos "/" por "-" para procesar uniformemente
                    f_norm = fecha_inf_tit.replace("/", "-")
                    # Detectamos si el año viene con 2 o 4 dígitos
                    formato = "%d-%m-%Y" if len(f_norm.split("-")[-1]) == 4 else "%d-%m-%y"
                    fecha_detectada_obj = datetime.strptime(f_norm, formato).date()
                    
                    if fecha_detectada_obj == manana_ar_obj:
                        st.success(f"✅ Fecha confirmada: {fecha_detectada_obj.strftime('%d/%m/%Y')}")
                        obs = st.text_area("📝 OBSERVACIONES PARA EL INFORME:", placeholder="Escriba aquí las notas sobre el estado de la operación...", height=120)
                        
                        if st.button("GENERAR PDF INFORME FINAL", use_container_width=True):
                            with st.spinner("Generando PDF..."):
                                pdf_bytes = logic_informe.generar_pdf_informe(df_inf_clean, obs)
                                st.download_button("📥 DESCARGAR INFORME", pdf_bytes, f"Informe_{fecha_inf_tit}.pdf", key="dl_inf_final", use_container_width=True)
                    else:
                        st.error("⚠️ Informe solo procesa pedidos del día siguiente.")
                        st.info(f"Fecha en archivo: {fecha_detectada_obj.strftime('%d/%m/%Y')} | Requerida (Mañana AR): {manana_txt}")
                
                except Exception as e:
                    st.error(f"No se pudo validar la fecha del archivo: {fecha_inf_tit}. Asegúrate de que el formato sea DD/MM/AAAA.")
                    st.info(f"Error técnico: {str(e)}")

# --- MENSAJES DE ADVERTENCIA POR FALTA DE ARCHIVO (Al final) ---
# Usamos un st.warning() limpio
if (btn_1 or btn_2 or btn_3) and not archivo_cdp:
    st.markdown("<br>", unsafe_allow_html=True)
    st.warning("⚠️ Sube el archivo CDP en el cargador superior para procesar las opciones 1, 2 o 3.")
