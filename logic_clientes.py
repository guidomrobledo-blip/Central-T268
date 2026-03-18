def motor_limpieza(df):
    """Limpia y prepara los datos evitando errores de tipo Nonetype."""
    # 1. Blindaje inicial contra celdas vacías (NaN)
    df = df.fillna('')
    df.columns = [str(c).strip() for c in df.columns]
    
    # Extraer fecha para el título
    fecha_tit_str = "S/D"
    if 'FECHA ENTREGA' in df.columns and not df.empty:
        try:
            fecha_raw = df['FECHA ENTREGA'].iloc[0]
            f_dt = pd.to_datetime(fecha_raw)
            fecha_tit_str = f_dt.strftime('%d/%m/%Y')
        except:
            fecha_tit_str = str(fecha_raw)

    def procesar_apellido_ajustado(texto):
        texto = str(texto).strip()
        if not texto: return ""
        partes = texto.split()
        excepciones = ['DA', 'DE', 'DI', 'DO', 'DU', 'LA', 'DEL', 'DAS', 'DOS']
        resultado, i = [], 0
        while i < len(partes) and len(resultado) < 2:
            pal_upper = partes[i].upper()
            if pal_upper in excepciones and i + 1 < len(partes):
                resultado.append(f"{partes[i].title()} {partes[i+1].title()}")
                i += 2
            else:
                resultado.append(partes[i].title()); i += 1
        return " ".join(resultado)

    def formatear_direccion_pro(row):
        calle = str(row.get('CALLE', '')).strip().title()
        dicc = {"Avenida": "Av.", "Boulevard": "Bv.", "Cortada": "Cda.", "Pasaje": "Pje."}
        for k, v in dicc.items(): calle = calle.replace(k, v)
        nro = str(row.get('NUMERO', '')).strip()
        nro_str = f" {nro}" if nro.lower() != 'nan' and nro != '' else ""
        return f"{calle}{nro_str}".strip()

    # Aplicar limpiezas forzando a string
    df['NOMBRE'] = df['NOMBRE CLIENTE'].apply(lambda n: str(n).split()[0].title() if str(n).strip() else "")
    df['APELLIDO'] = df['APELLIDO CLIENTE'].apply(procesar_apellido_ajustado)
    df['DIRECCIÓN'] = df.apply(formatear_direccion_pro, axis=1)
    
    return df, fecha_tit_str

def generar_pdf_clientes(df, fecha_tit):
    # --- LÓGICA DE ORDENAMIENTO SOLICITADO ---
    def crear_llave_visual(row):
        mod = str(row.get('MODALIDAD DE ENTREGA', ''))
        banda = str(row.get('BANDA HORARIA', ''))
        
        # Prioridad 1: Domicilio | Prioridad 2: Drive/Sucursal
        if "Drive" in mod or "Sucursal" in mod:
            return f"Drive/Sucursal | {banda}", 2 
        return f"Domicilio | {banda}", 1 

    df['LLAVE_ZOCALO'], df['ORDEN_TIPO'] = zip(*df.apply(crear_llave_visual, axis=1))
    
    # Ordenar: Domicilios (1) primero, luego Drive/Sucursal (2), ambos por horario
    df = df.sort_values(by=['ORDEN_TIPO', 'BANDA HORARIA'], ascending=[True, True])

    pdf = PlanillaPDF(fecha_tit)
    pdf.add_page()
    widths = [28, 20, 32, 22, 22, 47, 25]
    ultima_llave = None
    resumen_unificado = {}

    for _, row in df.iterrows():
        llave_actual = row['LLAVE_ZOCALO']
        resumen_unificado[llave_actual] = resumen_unificado.get(llave_actual, 0) + 1

        if llave_actual != ultima_llave:
            pdf.set_fill_color(64, 64, 64)
            pdf.set_text_color(255, 255, 255)
            pdf.set_font("Times", 'B', 11)
            pdf.cell(sum(widths), 7, f"--- {llave_actual} ---", border=1, ln=True, align='C', fill=True)
            pdf.set_text_color(0, 0, 0)
            pdf.set_font("Times", '', 9.5)
            ultima_llave = llave_actual

        pdf.cell(widths[0], 5, str(row.get('NUMERO PEDIDO', '')).replace(".0",""), border=1, align='C')
        pdf.cell(widths[1], 5, str(row.get('MODALIDAD DE ENTREGA', ''))[:10], border=1)
        pdf.cell(widths[2], 5, str(row.get('BANDA HORARIA', ''))[:18], border=1)
        pdf.cell(widths[3], 5, str(row.get('NOMBRE', ''))[:12], border=1)
        pdf.cell(widths[4], 5, str(row.get('APELLIDO', ''))[:12], border=1)
        pdf.cell(widths[5], 5, str(row.get('DIRECCIÓN', ''))[:31], border=1)
        tel = str(row.get('TEL. PARTICULAR', '')).split('.')[0]
        pdf.cell(widths[6], 5, tel[:13], border=1)
        pdf.ln()

    # Informe final respetando el orden de la tabla
    if (pdf.h - pdf.get_y()) < 45: pdf.add_page()
    pdf.ln(10)
    pdf.set_font("Times", 'B', 10)
    pdf.cell(0, 6, "Informe de pedidos al momento", ln=True, align='R')
    pdf.set_font("Times", '', 9.5)
    
    for k, v in resumen_unificado.items():
        pdf.cell(0, 4.5, f"{k}: {v}", ln=True, align='R')
    
    pdf.set_font("Times", 'B', 10)
    pdf.cell(0, 8, f"TOTAL: {len(df)}", ln=True, align='R')

    return pdf.output()
