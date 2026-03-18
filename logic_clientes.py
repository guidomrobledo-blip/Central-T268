def generar_pdf_clientes(df, fecha_tit):
    # --- PASO 1: DEFINIR LA LLAVE ÚNICA ---
    def crear_llave_visual(row):
        mod = str(row.get('MODALIDAD DE ENTREGA', ''))
        banda = str(row.get('BANDA HORARIA', ''))
        # Unificamos Drive y Sucursal bajo el mismo nombre
        if "Drive" in mod or "Sucursal" in mod:
            return f"Drive/Sucursal | {banda}", 1 
        return f"Domicilio | {banda}", 0 

    # Aplicamos la lógica de unificación
    df['LLAVE_ZOCALO'], df['ORDEN_PRIORIDAD'] = zip(*df.apply(crear_llave_visual, axis=1))
    
    # Ordenamos: primero Drive/Sucursal, luego Domicilio, y por Banda Horaria
    df = df.sort_values(by=['ORDEN_PRIORIDAD', 'BANDA HORARIA'], ascending=[False, True])

    pdf = PlanillaPDF(fecha_tit)
    pdf.add_page()
    widths = [28, 20, 32, 22, 22, 47, 25]
    ultima_llave = None
    resumen = {} # Diccionario para el informe final

    for _, row in df.iterrows():
        llave_actual = row['LLAVE_ZOCALO']
        
        # --- CONTEO PARA EL RESUMEN ---
        # Al usar LLAVE_ZOCALO, sumará Drive y Sucursal en la misma línea
        resumen[llave_actual] = resumen.get(llave_actual, 0) + 1

        # --- DIBUJAR ZÓCALO ---
        if llave_actual != ultima_llave:
            pdf.set_fill_color(64, 64, 64)
            pdf.set_text_color(255, 255, 255)
            pdf.set_font("Times", 'B', 11)
            # Imprime una sola franja gris para el grupo
            pdf.cell(sum(widths), 7, f"--- {llave_actual} ---", border=1, ln=True, align='C', fill=True)
            pdf.set_text_color(0, 0, 0)
            pdf.set_font("Times", '', 9.5)
            ultima_llave = llave_actual

        # Dibujo de las filas (se mantiene igual)
        pdf.cell(widths[0], 5, str(row['NUMERO PEDIDO']).replace(".0",""), border=1, align='C')
        pdf.cell(widths[1], 5, str(row['MODALIDAD DE ENTREGA'])[:10], border=1)
        pdf.cell(widths[2], 5, str(row['BANDA HORARIA'])[:18], border=1)
        pdf.cell(widths[3], 5, str(row['NOMBRE'])[:12], border=1)
        pdf.cell(widths[4], 5, str(row['APELLIDO'])[:12], border=1)
        pdf.cell(widths[5], 5, str(row['DIRECCIÓN'])[:31], border=1)
        pdf.cell(widths[6], 5, str(row['TEL. PARTICULAR'])[:13], border=1)
        pdf.ln()

    # --- INFORME FINAL (RESUMEN) ---
    if (pdf.h - pdf.get_y()) < 50: pdf.add_page()
    pdf.ln(10)
    pdf.set_font("Times", 'B', 10)
    pdf.cell(0, 6, "Informe de pedidos al momento", ln=True, align='R')
    pdf.set_font("Times", '', 9.5)
    
    for nombre, total in resumen.items():
        pdf.cell(0, 5, f"{nombre}: {total}", ln=True, align='R')
    
    pdf.set_font("Times", 'B', 10)
    pdf.cell(0, 8, f"TOTAL: {len(df)}", ln=True, align='R')

    return pdf.output(dest='S').encode('latin-1')
