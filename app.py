%%writefile app.py
import streamlit as st
import pandas as pd
import logic_clientes, logic_faltantes, logic_domicilios, logic_informe

st.set_page_config(page_title="Central T268", layout="wide")

st.markdown("<style>div.stButton > button:first-child, div.stLinkButton > a {height: 3em; font-weight: bold; display: flex; align-items: center; justify-content: center; text-decoration: none;}</style>", unsafe_allow_html=True)

st.title("🛒 Central Logística T268")

if 'mostrar_informe' not in st.session_state:
    st.session_state.mostrar_informe = False

archivo = st.file_uploader("Cargar Excel CDP", type=["xlsx"])

if archivo:
    df_raw = pd.read_excel(archivo)
    df_clean, fecha_tit = logic_clientes.motor_limpieza(df_raw)

    st.divider()
    c1, c2, c3, c4, c5 = st.columns(5)

    with c1:
        if st.button("🟢 1. CLIENTES", use_container_width=True):
            st.session_state.mostrar_informe = False
            pdf = logic_clientes.generar_pdf_clientes(df_clean, fecha_tit)
            st.download_button("📥 Descargar", bytes(pdf), f"Clientes_{fecha_tit}.pdf")

    with c2:
        if st.button("🔵 2. FALTANTES", use_container_width=True):
            st.session_state.mostrar_informe = False
            pdf = logic_faltantes.generar_pdf_faltantes(df_clean, fecha_tit)
            st.download_button("📥 Descargar", bytes(pdf), f"Faltantes_{fecha_tit}.pdf")

    with c3:
        if st.button("🟡 3. DOMICILIOS", use_container_width=True):
            st.session_state.mostrar_informe = False
            pdf = logic_domicilios.generar_pdf_domicilios(df_clean, fecha_tit)
            st.download_button("📥 Descargar", bytes(pdf), f"Ruta_{fecha_tit}.pdf")

    with c4:
        if st.button("🟠 4. INFORME", use_container_width=True):
            st.session_state.mostrar_informe = True

    with c5:
        # Botón 5: Ahora es un Link Button funcional
        st.link_button("🌐 5. PLANILLA MEC",
                       "https://docs.google.com/spreadsheets/d/1v0Rls8fg_uIGfhA1t3CzINq3VfAUvPY3DY8_m_ZSmM8/edit?gid=0#gid=0",
                       use_container_width=True)

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
