import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import logic_clientes, logic_faltantes, logic_domicilios, logic_informe

st.set_page_config(page_title="Central T268", layout="wide")

st.markdown("<style>div.stButton > button:first-child, div.stLinkButton > a {height: 3em; font-weight: bold; display: flex; align-items: center; justify-content: center; text-decoration: none;}</style>", unsafe_allow_html=True)

st.title("🛒 Central Logística T268")

if 'mostrar_informe' not in st.session_state:
    st.session_state.mostrar_informe = False

# 📁 CARGA DE ARCHIVO (Siempre visible arriba)
archivo = st.file_uploader("Cargar Excel CDP", type=["xlsx"])

st.divider()

# 🕹️ PANEL DE BOTONES (Siempre visibles)
c1, c2, c3, c4, c5 = st.columns(5)

with c1:
    btn_1 = st.button("🟢 1. CLIENTES", use_container_width=True)
with c2:
    btn_2 = st.button("🔵 2. FALTANTES", use_container_width=True)
with c3:
    btn_3 = st.button("🟡 3. DOMICILIOS", use_container_width=True)
with col4_informe := c4: # Usamos un contenedor para el botón 4
    btn_4 = st.button("🟠 4. INFORME", use_container_width=True)
with c5:
    st.link_button("🌐 5. PLANILLA MEC", 
                   "https://docs.google.com/spreadsheets/d/1v0Rls8fg_uIGfhA1t3CzINq3VfAUvPY3DY8_m_ZSmM8/edit?gid=0#gid=0", 
                   use_container_width=True)

# ⚙️ LÓGICA DE PROCESAMIENTO
if archivo:
    df_raw = pd.read_excel(archivo)
    df_clean, fecha_tit = logic_clientes.motor_limpieza(df_raw)

    if btn_1:
        st.session_state.mostrar_informe = False
        pdf = logic_clientes.generar_pdf_clientes(df_clean, fecha_tit)
        st.download_button("📥 Descargar Clientes", bytes(pdf), f"Clientes_{fecha_tit}.pdf")

    if btn_2:
        st.session_state.mostrar_informe = False
        pdf = logic_faltantes.generar_pdf_faltantes(df_clean, fecha_tit)
        st.download_button("📥 Descargar Faltantes", bytes(pdf), f"Faltantes_{fecha_tit}.pdf")

    if btn_3:
        st.session_state.mostrar_informe = False
        pdf = logic_domicilios.generar_pdf_domicilios(df_clean, fecha_tit)
        st.download_button("📥 Descargar Ruta", bytes(pdf), f"Ruta_{fecha_tit}.pdf")

    if btn_4:
        # VALIDACIÓN DE FECHA: Mañana = Hoy + 1
        hoy = datetime.now().date()
        manana = hoy + timedelta(days=1)
        
        # Intentamos convertir la fecha que extrajo tu motor_limpieza
        try:
            # fecha_tit suele venir como string 'DD-MM-AAAA' según tu lógica
            fecha_archivo = datetime.strptime(fecha_tit, "%d-%m-%Y").date()
            
            if fecha_archivo == manana:
                st.session_state.mostrar_informe = True
            else:
                st.error("⚠️ El Informe solo procesa pedidos del día siguiente.")
                st.info(f"Fecha en archivo: {fecha_tit} | Requerida: {manana.strftime('%d-%m-%Y')}")
                st.session_state.mostrar_informe = False
        except:
            # Si falla la conversión, permitimos por seguridad pero avisamos
            st.warning("No se pudo validar la fecha automáticamente.")
            st.session_state.mostrar_informe = True

    if st.session_state.mostrar_informe:
        st.info("Configuración del Informe de Estado")
        obs = st.text_area("📝 Escriba las OBSERVACIONES:", placeholder="Escriba aquí...")
        pdf_bytes = logic_informe.generar_pdf_informe(df_clean, obs)
        st.download_button(
            label="🚀 GENERAR Y DESCARGAR INFORME",
            data=pdf_bytes,
            file_name=f"Informe_{fecha_tit}.pdf",
            mime="application/pdf",
            use_container_width=True
        )
else:
    # Si alguien presiona un botón de proceso sin haber cargado el Excel
    if btn_1 or btn_2 or btn_3 or btn_4:
        st.warning("⚠️ Primero debes cargar el archivo Excel del CDP.")
