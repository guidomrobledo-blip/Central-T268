def generar_pdf_clientes(df, fecha_tit):
    # --- PASO 1: UNIFICACIÓN TOTAL DE CRITERIOS ---
    def crear_llave_visual(row):
        mod = str(row.get('MODALIDAD DE ENTREGA', ''))
        banda = str(row.get('BANDA HORARIA', ''))
        # Si es retiro (Drive o Sucursal), usamos una etiqueta única
        if "Drive" in mod or "Sucursal" in mod:
            return f"Drive/Sucursal | {banda}", 1 
        # Si es Domicilio, mantenemos su etiqueta
        return f"Domicilio | {banda}", 0 

    # Creamos las columnas auxiliares para agrupar de verdad
    df['LLAVE_ZOCALO'], df['PRIORIDAD_GRUPO'] = zip(*df.apply(crear_llave_visual, axis=1))
    
    # ORDENAMIENTO CRÍTICO: Agrupamos por la nueva llave para que no salgan zócalos repetidos
    df = df.sort_values(by=['PRIORIDAD_GRUPO', 'BANDA HORARIA'], ascending=[False, True])

    pdf = PlanillaPDF(fecha_tit)
    pdf.add_page()
    widths = [28, 20, 32, 22, 22, 47, 25]
    ultima_llave = None
    resumen_unificado = {} # Aquí guardaremos el conteo final

    for _, row in df.iterrows():
        llave_actual = row['LLAVE_ZOCALO']
        
        # --- CONTEO PARA EL INFORME FINAL ---
        resumen_unificado[llave_actual] = resumen_unificado.get(llave_actual, 0) + 1

        # --- DIBUJAR ZÓCALO GRIS (Solo si la llave cambia) ---
        if llave_actual != ultima_llave:
            pdf.set_fill_color(64, 64, 64)
            pdf.set_text_color(255, 255, 255)
            pdf.set_font("Times", 'B', 11)
            # Imprime una sola franja para Drive/Sucursal juntos
            pdf.cell(sum(widths), 7, f"--- {llave_actual} ---", border=1, ln=True, align='C', fill=True)
            pdf.set_text_color(0, 0, 0)
            pdf.set_font("Times", '', 9.5)
            ultima_llave = llave_actual

        # --- DIBUJO DE FILAS ---
        pdf.cell(widths[0], 5, str(row.get('NUMERO PEDIDO', '')).replace(".0",""), border=1, align='C')
        pdf.cell(widths[1], 5, str(row.get('MODALIDAD DE ENTREGA', ''))[:10], border=1)
        pdf.cell(widths[2], 5, str(row.get('BANDA HORARIA', ''))[:18], border=1)
        pdf.cell(widths[3], 5, str(row.get('NOMBRE', ''))[:12], border=1)
        pdf.cell(widths[4], 5, str(row.get('APELLIDO', ''))[:12], border=1)
        pdf.cell(widths[5], 5, str(row.get('DIRECCIÓN', ''))[:31], border=1)
        pdf.cell(widths[6], 5, str(row.get('TEL. PARTICULAR', ''))[:13], border=1)
        pdf.ln()

    # --- INFORME FINAL UNIFICADO ---
    if (pdf.h - pdf.get_y()) < 50: pdf.add_page()
    pdf.ln(10)
    pdf.set_font("Times", 'B', 10)
    pdf.cell(0, 6, "Informe de pedidos al momento", ln=True, align='R')
    pdf.set_font("Times", '', 9.5)
    
    # Imprimimos el resumen usando la llave unificada
    for nombre_grupo, total in resumen_unificado.items():
        pdf.cell(0, 5, f"{nombre_grupo}: {total}", ln=True, align='R')
    
    pdf.set_font("Times", 'B', 10)
    pdf.cell(0, 8, f"TOTAL: {len(df)}", ln=True, align='R')

    return pdf.output(dest='S').encode('latin-1')
