def generar_pdf_clientes(df, fecha_tit):
    # 1. Definir la lógica de visualización y el NUEVO ORDEN
    def crear_llave_visual(row):
        mod = str(row.get('MODALIDAD DE ENTREGA', ''))
        banda = str(row.get('BANDA HORARIA', ''))
        
        # Invertimos prioridades: Domicilio (1) va primero que Drive/Sucursal (2)
        if "Drive" in mod or "Sucursal" in mod:
            return f"Drive/Sucursal | {banda}", 2 
        return f"Domicilio | {banda}", 1 

    # Aplicamos la llave y la prioridad
    df['LLAVE_ZOCALO'], df['PRIORIDAD_TIPO'] = zip(*df.apply(crear_llave_visual, axis=1))
    
    # 2. ORDENAMIENTO: Por prioridad (1 a 2) y luego por Banda Horaria
    df = df.sort_values(by=['PRIORIDAD_TIPO', 'BANDA HORARIA'], ascending=[True, True])

    pdf = PlanillaPDF(fecha_tit)
    pdf.add_page()
    widths = [28, 20, 32, 22, 22, 47, 25]
    ultima_llave = None
    resumen_unificado = {}

    for _, row in df.iterrows():
        llave_actual = row['LLAVE_ZOCALO']
        
        # Conteo para el informe final (Unificado)
        resumen_unificado[llave_actual] = resumen_unificado.get(llave_actual, 0) + 1

        # Dibujar Zócalo solo si cambia la LLAVE
        if llave_actual != ultima_llave:
            pdf.set_fill_color(64, 64, 64)
            pdf.set_text_color(255, 255, 255)
            pdf.set_font("Times", 'B', 11)
            pdf.cell(sum(widths), 7, f"--- {llave_actual} ---", border=1, ln=True, align='C', fill=True)
            pdf.set_text_color(0, 0, 0)
            pdf.set_font("Times", '', 9.5)
            ultima_llave = llave_actual

        # Filas de datos
        pdf.cell(widths[0], 5, str(row.get('NUMERO PEDIDO', '')).replace(".0",""), border=1, align='C')
        pdf.cell(widths[1], 5, str(row.get('MODALIDAD DE ENTREGA', ''))[:10], border=1)
        pdf.cell(widths[2], 5, str(row.get('BANDA HORARIA', ''))[:18], border=1)
        pdf.cell(widths[3], 5, str(row.get('NOMBRE', ''))[:12], border=1)
        pdf.cell(widths[4], 5, str(row.get('APELLIDO', ''))[:12], border=1)
        pdf.cell(widths[5], 5, str(row.get('DIRECCIÓN', ''))[:31], border=1)
        tel = str(row.get('TEL. PARTICULAR', '')).split('.')[0]
        pdf.cell(widths[6], 5, tel[:13], border=1)
        pdf.ln()

    # Informe final (Respeta el mismo orden unificado)
    if (pdf.h - pdf.get_y()) < 45: pdf.add_page()
    pdf.ln(10)
    pdf.set_font("Times", 'B', 10)
    pdf.cell(0, 6, "Informe de pedidos al momento", ln=True, align='R')
    pdf.set_font("Times", '', 9.5)
    
    for k, v in resumen_unificado.items():
        pdf.cell(0, 4.5, f"{k}: {v}", ln=True, align='R')
    
    pdf.set_font("Times", 'B', 10)
    pdf.cell(0, 8, f"TOTAL: {len(df)}", ln=True, align='R')

    # Retorno directo para fpdf2
    return pdf.output()
