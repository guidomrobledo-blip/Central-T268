import pandas as pd
import re
from datetime import datetime, timedelta
from fpdf import FPDF
import os

def motor_limpieza(df):
    """Limpia y prepara los datos básicos."""
    df.columns = [str(c).strip() for c in df.columns]
    
    fecha_raw = df['FECHA ENTREGA'].iloc[0] if 'FECHA ENTREGA' in df.columns else "S/D"
    try:
        f_dt = pd.to_datetime(fecha_raw)
        fecha_tit_str = f_dt.strftime('%d/%m/%Y')
    except:
        fecha_tit_str = str(fecha_raw)

    def procesar_apellido_ajustado(texto):
        if pd.isna(texto) or str(texto).strip() == "":
            return ""
        partes = str(texto).split()
        excepciones = ['DA', 'DE', 'DI', 'DO', 'DU', 'LA', 'DEL', 'DAS', 'DOS']
        resultado, i = [], 0
        while i < len(partes) and len(resultado) < 2:
            pal_upper = partes[i].upper()
            if pal_upper in excepciones and i + 1 < len(partes):
                resultado.append(f"{partes[i].title()} {partes[i+1].title()}")
                i += 2
            else:
                resultado.append(partes[i].title())
                i += 1
        return " ".join(resultado)

    def formatear_direccion_pro(row):
        calle = str(row.get('CALLE', '')).strip().title()
        dicc = {"Avenida": "Av.", "Boulevard": "Bv.", "Cortada": "Cda.", "Pasaje": "Pje."}
        for k, v in dicc.items():
            calle = calle.replace(k, v)
        nro = str(row.get('NUMERO', '')).strip()
        nro_str = f" {nro}" if nro.lower() != 'nan' and nro != '' else ""
        return f"{calle}{nro_str}".strip()

    df['NOMBRE'] = df['NOMBRE CLIENTE'].apply(lambda n: str(n).split()[0].title() if pd.notna(n) else "")
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
        self.multi_cell(
            100, 5,
            f"Planilla operativa de Pedidos\nEntrega del día: {self.fecha_tit}\nTienda: [268]",
            align='R'
        )

        self.ln(6)

        self.set_fill_color(240, 240, 240)
        self.set_font("Times", 'B', 9)

        cols = ["Nro PEDIDO", "MODALIDAD", "BANDA HORARIA", "NOMBRE", "APELLIDO", "DIRECCIÓN", "TELÉFONO"]
        widths = [28, 20, 32, 22, 22, 47, 25]

        for i, col in enumerate(cols):
            self.cell(widths[i], 7.5, col, border=1, fill=True, align='C')
        self.ln()


def generar_pdf_clientes(df, fecha_tit):

    def crear_llave_visual(row):
        mod = str(row.get('MODALIDAD DE ENTREGA', ''))
        banda = str(row.get('BANDA HORARIA', ''))

        if "Drive" in mod or "Sucursal" in mod:
            return f"Drive/Sucursal | {banda}", 1
        return f"Domicilio | {banda}", 0

    df['LLAVE_ZOCALO'], df['TIPO_ORDEN'] = zip(*df.apply(crear_llave_visual, axis=1))

    def obtener_hora_orden(banda):
        match = re.search(r'(\d{2}):(\d{2})', str(banda))
        if match:
            return int(match.group(1)) * 60 + int(match.group(2))
        return 9999

    df['HORA_ORDEN'] = df['BANDA HORARIA'].apply(obtener_hora_orden)

    df = df.sort_values(
        by=['TIPO_ORDEN', 'HORA_ORDEN'],
        ascending=[True, True]
    )

    font_size, row_height = 9.5, 5

    while font_size > 6.5:
        pdf = PlanillaPDF(fecha_tit)
        pdf.add_page()

        widths = [28, 20, 32, 22, 22, 47, 25]
        ultima_llave = None
        resumen = {}

        for _, row in df.iterrows():
            llave_actual = row['LLAVE_ZOCALO']
            mod_real = str(row['MODALIDAD DE ENTREGA'])
            banda_real = str(row['BANDA HORARIA'])

            resumen[f"{mod_real} | {banda_real}"] = resumen.get(f"{mod_real} | {banda_real}", 0) + 1

            if llave_actual != ultima_llave:
                pdf.set_fill_color(64, 64, 64)
                pdf.set_text_color(255, 255, 255)
                pdf.set_font("Times", 'B', font_size + 2)

                pdf.cell(sum(widths), row_height + 1.5,
                         f"--- {llave_actual} ---",
                         border=1, ln=True, align='C', fill=True)

                pdf.set_text_color(0, 0, 0)
                pdf.set_font("Times", '', font_size)
                ultima_llave = llave_actual

            pdf.cell(widths[0], row_height, str(row['NUMERO PEDIDO']).replace(".0", ""), border=1, align='C')
            pdf.cell(widths[1], row_height, mod_real[:10], border=1)
            pdf.cell(widths[2], row_height, banda_real[:18], border=1)
            pdf.cell(widths[3], row_height, str(row['NOMBRE'])[:12], border=1)
            pdf.cell(widths[4], row_height, str(row['APELLIDO'])[:12], border=1)
            pdf.cell(widths[5], row_height, str(row['DIRECCIÓN'])[:31], border=1)
            pdf.cell(widths[6], row_height, str(row['TEL. PARTICULAR'])[:13], border=1)
            pdf.ln()

        # ===== INFORME FINAL =====

        if (pdf.h - pdf.get_y()) < 35:
            pdf.add_page()

        pdf.ln(5)

        hora_actual = datetime.now().strftime("%H:%M")

        pdf.set_font("Times", 'B', font_size + 1)
        pdf.cell(
            0,
            6,
            f"Resumen de Pedidos hasta el momento [{hora_actual}hs]",
            ln=True,
            align='R'
        )

        resumen_procesado = {}

        for k, v in resumen.items():
            try:
                modalidad, banda = k.split(" | ")
            except:
                continue

            if "domicilio" in modalidad.lower():
                mod_final = "Domicilios"
                tipo = 0
            else:
                mod_final = "Drive/Suc"
                tipo = 1

            match = re.search(r'(\d{2}):(\d{2})', banda)
            hora_orden = int(match.group(1)) * 60 + int(match.group(2)) if match else 9999

            resumen_procesado[(tipo, hora_orden, mod_final, banda)] = v

        resumen_ordenado = sorted(resumen_procesado.items(), key=lambda x: (x[0][0], x[0][1]))

        pdf.set_font("Times", '', font_size)

        for (_, _, mod_final, banda), cantidad in resumen_ordenado:
            pdf.cell(0, 4.5, f"{mod_final} | {banda}: [{cantidad}]", ln=True, align='R')

        pdf.set_font("Times", 'B', font_size + 1)
        pdf.cell(0, 8, f"TOTAL: [{len(df)}]", ln=True, align='R')

        if pdf.page_no() <= 15:
            break

        font_size -= 0.5

    return pdf.output()
