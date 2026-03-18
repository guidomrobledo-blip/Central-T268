import pandas as pd
import re
from datetime import datetime, timedelta
from fpdf import FPDF
import os

def motor_limpieza(df):
    """Limpia y prepara los datos básicos."""
    # Llenamos vacíos con texto vacío para evitar errores de tipo Nonetype
    df = df.fillna('')
    df.columns = [str(c).strip() for c in df.columns]
    
    # Extraer fecha para el título
    fecha_raw = df['FECHA ENTREGA'].iloc[0] if 'FECHA ENTREGA' in df.columns else "S/D"
    try:
        f_dt = pd.to_datetime(fecha_raw)
        fecha_tit_str = f_dt.strftime('%d/%m/%Y')
    except:
        fecha_tit_str = str(fecha_raw)

    def procesar_apellido_ajustado(texto):
        if not texto: return ""
        partes = str(texto).split()
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

    # Aplicar limpiezas
    df['NOMBRE'] = df['NOMBRE CLIENTE'].apply(lambda n: str(n).split()[0].title() if n else "")
    df['APELLIDO'] = df['APELLIDO CLIENTE'].apply(procesar_apellido_ajustado)
    df['DIRECCIÓN'] = df.apply(formatear_direccion_pro, axis=1)
    
    return df, fecha_tit_str

class PlanillaPDF(FPDF):
    def __init__(self, fecha_tit):
        super().__init__(orientation='P', unit='mm', format='A4')
        self.fecha_tit = fecha_tit
        self.set_margins(left=7, top=10, right=7)
        self.set_auto_page_break(auto=True, margin=8)

    def header(self):
        if os.path.exists('carrefour+logo.png'):
            self.image('carrefour+logo.png', x=7, y=8, w=55)
        self.set_font("Times", 'B', 11)
        self.set_xy(100, 10)
        self.multi_cell(100, 5, f"Planilla operativa de Pedidos\nEntrega del día: {self.fecha_tit}\nTienda: [268]", align='R')
        self.ln(6)
        self.set_fill_color(240, 240, 240)
        self.set_font("Times", 'B', 9)
        cols = ["Nro PEDIDO", "MODALIDAD", "BANDA HORARIA", "NOMBRE", "APELLIDO", "DIRECCIÓN", "TELÉFONO"]
        widths = [28, 20, 32, 22, 22, 47, 25]
        for i, col in enumerate(cols):
            self.cell(widths[i], 7.5, col, border=1, fill=True, align='C')
        self.ln()

def generar_pdf_clientes(df, fecha_tit):
    # --- UNIFICACIÓN DE CRITERIOS ---
    def crear_llave_visual(row):
        mod = str(row.get('MODALIDAD DE ENTREGA', ''))
        banda = str(row.get('BANDA HORARIA', ''))
        if "Drive" in mod or "Sucursal" in mod:
            return f"Drive/Sucursal | {banda}", 1 
        return f"Domicilio | {banda}", 0 

    df['LLAVE_ZOCALO'], df['TIPO_ORDEN'] = zip(*df.apply(crear_llave_visual, axis=1))
    
    # Ordenamiento físico para evitar zócalos repetidos
    df = df.sort_values(by=['TIPO_ORDEN', 'BANDA HORARIA', 'MODALIDAD DE ENTREGA'], ascending=[False, True, True])

    font_size, row_height = 9.5, 5
    pdf = PlanillaPDF(fecha_tit)
    pdf.add_page()
    widths = [28, 20, 32, 22, 22, 47, 25]
    ultima_llave = None
    resumen_unificado = {}

    for _, row in df.iterrows():
        llave_actual = row['LLAVE_ZOCALO']
        
        # Conteo para el resumen final (usando la llave unificada)
        resumen_unificado[llave_actual] = resumen_unificado.get(llave_actual, 0) + 1

        # Dibujar Zócalo solo si cambia la LLAVE VISUAL
        if llave_actual != ultima_llave:
            pdf.set_fill_color(64, 64, 64)
            pdf.set_text_color(255, 255, 255)
            pdf.set_font("Times", 'B', font_size + 2)
            pdf.cell(sum(widths), row_height + 1.5, f"--- {llave_actual} ---", border=1, ln=True, align='C', fill=True)
            pdf.set_text_color(0, 0, 0)
            pdf.set_font("Times", '', font_size)
            ultima_llave = llave_actual

        # Filas de datos (usamos .get para evitar errores si falta una columna)
        pdf.cell(widths[0], row_height, str(row.get('NUMERO PEDIDO', '')).replace(".0",""), border=1, align='C')
        pdf.cell(widths[1], row_height, str(row.get('MODALIDAD DE ENTREGA', ''))[:10], border=1)
        pdf.cell(widths[2], row_height, str(row.get('BANDA HORARIA', ''))[:18], border=1)
        pdf.cell(widths[3], row_height, str(row.get('NOMBRE', ''))[:12], border=1)
        pdf.cell(widths[4], row_height, str(row.get('APELLIDO', ''))[:12], border=1)
        pdf.cell(widths[5], row_height, str(row.get('DIRECCIÓN', ''))[:31], border=1)
        pdf.cell(widths[6], row_height, str(row.get('TEL. PARTICULAR', '')).split('.')[0][:13], border=1)
        pdf.ln()

    # Informe final unificado
    if (pdf.h - pdf.get_y()) < 45: pdf.add_page()
    pdf.ln(10)
    pdf.set_font("Times", 'B', font_size + 1)
    pdf.cell(0, 6, "Informe de pedidos al momento", ln=True, align='R')
    pdf.set_font("Times", '', font_size)
    
    for k, v in resumen_unificado.items():
        pdf.cell(0, 4.5, f"{k}: {v}", ln=True, align='R')
    
    pdf.set_font("Times", 'B', font_size + 1)
    pdf.cell(0, 8, f"TOTAL: {len(df)}", ln=True, align='R')

    # EL ARREGLO PARA EL ERROR: errors='ignore' para caracteres no soportados
    return pdf.output(dest='S').encode('latin-1', errors='ignore')
