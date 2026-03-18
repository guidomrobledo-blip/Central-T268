def generar_pdf_clientes(df, fecha_tit):
    # --- 1. CREAR LLAVE UNIFICADA ---
    def crear_llave_visual(row):
        mod = str(row.get('MODALIDAD DE ENTREGA', ''))
        banda = str(row.get('BANDA HORARIA', ''))
        
        if "Drive" in mod or "Sucursal" in mod:
            # Ambos comparten la misma LLAVE para el zócalo y el resumen
            return f"Drive/Sucursal | {banda}", 1 
        return f"Domicilio | {banda}", 0 

    df['LLAVE_ZOCALO'], df['PRIORIDAD'] = zip(*df.apply(crear_llave_visual, axis=1))

    # --- 2. ORDENAMIENTO CLAVE ---
    # Al ordenar por LLAVE_ZOCALO, todos los pedidos de la misma banda quedan juntos
    # sin importar si son Drive o Sucursal.
    df = df.sort_values(by=['PRIORIDAD', 'LLAVE_ZOCALO'], ascending=[False, True])

    pdf = PlanillaPDF(fecha_tit)
    pdf.add_page()
    widths = [28, 20, 32, 22, 22, 47, 25]
    ultima_llave = None
    resumen = {}

    for _, row in df.iterrows():
        llave_actual = row['LLAVE_ZOCALO']
        resumen[llave_actual] = resumen.get(llave_actual, 0) + 1

        # --- DIBUJAR ZÓCALO ÚNICO ---
        if llave_actual != ultima_llave:
            pdf.set_fill_color(64, 64, 64)
            pdf.set_text_color(255, 255, 255)
            pdf.set_font("Times", 'B', 11)
            pdf.cell(sum(widths), 7, f"--- {llave_actual} ---", border=1, ln=True, align='C', fill=True)
            pdf.set_text_color(0, 0, 0)
            pdf.set_font("Times", '', 9.5)
            ultima_llave = llave_actual

        # --- DIBUJAR FILA ---
        pdf.cell(widths[0], 5, str(row.get('NUMERO PEDIDO', '')).replace(".0",""), border=1, align='C')
        pdf.cell(widths[1], 5, str(row.get('MODALIDAD DE ENTREGA', ''))[:10], border=1)
        pdf.cell(widths[2], 5, str(row.get('BANDA HORARIA', ''))[:18], border=1)
        pdf.cell(widths[3], 5, str(row.get('NOMBRE', ''))[:12], border=1)
        pdf.cell(widths[4], 5, str(row.get('APELLIDO', ''))[:12], border=1)
        pdf.cell(widths[5], 5, str(row.get('DIRECCIÓN', ''))[:31], border=1)
        pdf.cell(widths[6], 5, str(row.get('TEL. PARTICULAR', ''))[:13], border=1)
        pdf.ln()

    # --- 3. INFORME FINAL (RESUMEN) ---
    if (pdf.h - pdf.get_y()) < 50: pdf.add_page()
    pdf.ln(10)
    pdf.set_font("Times", 'B', 10)
    pdf.cell(0, 6, "Informe de pedidos al momento", ln=True, align='R')
    pdf.set_font("Times", '', 9.5)
    
    # Aquí ya no habrá duplicados porque el diccionario usa las llaves unificadas
    for k, v in resumen.items():
        pdf.cell(0, 5, f"{k}: {v}", ln=True, align='R')
    
    pdf.cell(0, 8, f"TOTAL: {len(df)}", ln=True, align='R')

    return pdf.output(dest='S').encode('latin-1')
