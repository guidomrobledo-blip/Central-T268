def generar_pdf_clientes(df, fecha_tit):
    # 1. Agrupación física (mantenemos tu lógica de Drive/Sucursal juntos)
    def crear_llave_visual(row):
        mod = str(row.get('MODALIDAD DE ENTREGA', ''))
        banda = str(row.get('BANDA HORARIA', ''))
        if "Drive" in mod or "Sucursal" in mod:
            return f"Drive/Sucursal | {banda}", 1 
        return f"Domicilio | {banda}", 0 

    df['LLAVE_ZOCALO'], df['TIPO_ORDEN'] = zip(*df.apply(crear_llave_visual, axis=1))
    df = df.sort_values(by=['TIPO_ORDEN', 'BANDA HORARIA', 'MODALIDAD DE ENTREGA'], ascending=[False, True, True])

    font_size, row_height = 9.5, 5
    pdf = PlanillaPDF(fecha_tit)
    pdf.add_page()
    widths = [28, 20, 32, 22, 22, 47, 25]
    ultima_llave = None
    
    # IMPORTANTE: Diccionario para el resumen
    resumen = {}

    for _, row in df.iterrows():
        llave_actual = row['LLAVE_ZOCALO']
        
        # --- CAMBIO CLAVE AQUÍ ---
        # Sumamos al conteo usando la LLAVE (Drive/Sucursal | Banda) 
        # en lugar de la modalidad individual.
        resumen[llave_actual] = resumen.get(llave_actual, 0) + 1

        if llave_actual != ultima_llave:
            pdf.set_fill_color(64, 64, 64)
            pdf.set_text_color(255, 255, 255)
            pdf.set_font("Times", 'B', font_size + 2)
            pdf.cell(sum(widths), row_height + 1.5, f"--- {llave_actual} ---", border=1, ln=True, align='C', fill=True)
            pdf.set_text_color(0, 0, 0)
            pdf.set_font("Times", '', font_size)
            ultima_llave = llave_actual

        # Dibujo de filas
        pdf.cell(widths[0], row_height, str(row['NUMERO PEDIDO']).replace(".0",""), border=1, align='C')
        pdf.cell(widths[1], row_height, str(row['MODALIDAD DE ENTREGA'])[:10], border=1)
        pdf.cell(widths[2], row_height, str(row['BANDA HORARIA'])[:18], border=1)
        pdf.cell(widths[3], row_height, str(row['NOMBRE'])[:12], border=1)
        pdf.cell(widths[4], row_height, str(row['APELLIDO'])[:12], border=1)
        pdf.cell(widths[5], row_height, str(row['DIRECCIÓN'])[:31], border=1)
        pdf.cell(widths[6], row_height, str(row['TEL. PARTICULAR'])[:13], border=1)
        pdf.ln()

    # --- INFORME FINAL ---
    if (pdf.h - pdf.get_y()) < 45: pdf.add_page()
    pdf.ln(10)
    pdf.set_font("Times", 'B', font_size + 1)
    pdf.cell(0, 6, "Informe de pedidos al momento", ln=True, align='R')
    pdf.set_font("Times", '', font_size)
    
    # Imprimimos los totales usando las llaves unificadas
    for nombre_grupo, total in resumen.items():
        pdf.cell(0, 5, f"{nombre_grupo}: {total}", ln=True, align='R')
    
    pdf.set_font("Times", 'B', font_size + 1)
    pdf.cell(0, 8, f"TOTAL: {len(df)}", ln=True, align='R')

    return pdf.output(dest='S').encode('latin-1')
