# --- LÓGICA EXCLUSIVA BOTÓN 4 (INFORME) ---
if btn_4 or st.session_state.get('inf_activo', False):
    st.session_state.inf_activo = True
    st.markdown("---")
    st.subheader("🚀 Procesador Exclusivo de Informe")
    
    archivo_inf = st.file_uploader("Subir planilla para INFORME (Debe ser fecha de mañana)", type=["xlsx"], key="u_inf")
    
    if archivo_inf:
        df_inf_raw = pd.read_excel(archivo_inf)
        df_inf_clean, fecha_inf_tit = logic_clientes.motor_limpieza(df_inf_raw)
        
        # 1. Calculamos "Mañana" en Argentina
        fecha_ar = datetime.utcnow() - timedelta(hours=3)
        manana_obj = (fecha_ar + timedelta(days=1)).date()
        
        # 2. Normalizamos la fecha detectada del Excel para que sea comparable
        # Esto convierte "11-03-2026" o "11/03/26" en un objeto fecha real
        try:
            # Reemplazamos barras por guiones para estandarizar
            fecha_limpia = fecha_inf_tit.replace("/", "-")
            # Intentamos leer el formato (ajusta si tu motor_limpieza da el año con 2 o 4 cifras)
            formato = "%d-%m-%Y" if len(fecha_limpia.split("-")[-1]) == 4 else "%d-%m-%y"
            fecha_detectada_obj = datetime.strptime(fecha_limpia, formato).date()
            
            # 3. COMPARACIÓN FINAL
            if fecha_detectada_obj == manana_obj:
                st.success(f"✅ Fecha confirmada: {fecha_detectada_obj.strftime('%d/%m/%Y')}")
                obs = st.text_area("📝 OBSERVACIONES:", placeholder="Escriba aquí...")
                if st.button("GENERAR PDF INFORME"):
                    pdf_bytes = logic_informe.generar_pdf_informe(df_inf_clean, obs)
                    st.download_button("📥 DESCARGAR INFORME", pdf_bytes, f"Informe_{fecha_inf_tit}.pdf")
            else:
                st.error("⚠️ Informe solo procesa pedidos del día siguiente.")
                st.info(f"Detectado: {fecha_detectada_obj.strftime('%d/%m/%Y')} | Requerido: {manana_obj.strftime('%d/%m/%Y')}")
        
        except Exception as e:
            st.error(f"Error al procesar la fecha del archivo: {fecha_inf_tit}")
            st.info("Asegúrate de que el Excel tenga la fecha en la celda correspondiente.")
