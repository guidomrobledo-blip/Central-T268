import pandas as pd
import re
from datetime import datetime, timedelta
from fpdf import FPDF
import os


def motor_limpieza(df):
    df.columns = [str(c).strip() for c in df.columns]
    fecha_raw = df['FECHA ENTREGA'].iloc[0] if 'FECHA ENTREGA' in df.columns else "S/D"
    try:
        f_dt = pd.to_datetime(fecha_raw)
        fecha_tit_str = f_dt.strftime('%d/%m/%Y')
    except:
        fecha_tit_str = str(fecha_raw)

    def procesar_apellido_ajustado(texto):
        if pd.isna(texto) or str(texto).strip() == "": return ""
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
        dicc = {
            "Avenida": "Av.", "Boulevard": "Bv.", "Cortada": "Cda.",
            "Diagonal": "Diag.", "Pasaje": "Pje.", "Entre Rios": "E. Ríos",
            "Sargento": "Sgto.", "General": "Gral.", "Doctor": "Dr.",
            "Presidente": "Pres.", "Republica": "Rep.", "Batalla": "Bat.",
            "Manuel Belgrano": "M. Belgrano", "Carlos Pellegrini": "C. Pellegrini",
            "Jorge Newbery": "J. Newbery", "Juan Jose Paso": "J.J. Paso",
            "Juan Manuel De Rosas": "J.M. de Rosas", "Martin Rodriguez": "M. Rodriguez",
            "Ovidio": "Ov."
        }
        for k, v in dicc.items(): calle = calle.replace(k, v)
        calle = re.sub(r'Pellegrini|Pelegrini', 'Pellegrini', calle, flags=re.IGNORECASE)
        nro = str(row.get('NUMERO', '')).strip()
        nro_str = f" {nro}" if nro.lower() != 'nan' and nro != '' else ""
        depto_raw = str(row.get('DEPTO', '')).upper().strip()
        excluir = ["DR", "NAN", "@ SC @ NRO @ DPTO", "@ SC", "@ NRO", "@ DPTO"]
        corchete = ""
        if depto_raw and not any(x == depto_raw for x in excluir):
            if any(pb in depto_raw for pb in ["PLANTA BAJA", "P.B", "P/B", "PB"]): corchete = " [P/B]"
            elif any(pa in depto_raw for pa in ["PLANTA ALTA", "P.ALTA", "P.A", "PLANTA.A", "PA"]): corchete = " [P/A]"
            else:
                piso_match = re.search(r'(?:PISO|P|PSO|P\.)\s*(\d+)', depto_raw)
                dpto_match = re.search(r'(?:DEPTO|DEPARTAMENTO|DPTO|DPT|D\.|D)\s*([A-Z0-9]+)', depto_raw)
                piso, dpto = (piso_match.group(1) if piso_match else ""), (dpto_match.group(1) if dpto_match else "")
                if not piso and not dpto:
                    partes = re.findall(r'([A-Z0-9]+)', depto_raw)
                    if len(partes) >= 2: piso, dpto = partes[0], partes[1]
                    elif len(partes) == 1: dpto = partes[0]
                if piso and dpto: corchete = f" [{piso} - {dpto}]" if piso != dpto else f" [{piso}]"
                elif piso: corchete = f" [{piso}]"
                elif dpto: corchete = f" [{dpto}]"
        return f"{calle}{nro_str}{corchete}".strip()

    df['DIRECCIÓN'] = df.apply(formatear_direccion_pro, axis=1)
    df['NOMBRE'] = df['NOMBRE CLIENTE'].apply(lambda n: str(n).split()[0].title() if pd.notna(n) else "")
    df['APELLIDO'] = df['APELLIDO CLIENTE'].apply(procesar_apellido_ajustado)

    mapping = {
        "Domicilio | 10:00 a 14:00": 1, "Domicilio | 14:00 a 18:00": 2,
        "Drive | 09:00 a 13:00": 3, "Sucursal | 09:00 a 13:00": 4,
        "Drive | 13:00 a 18:00": 5, "Sucursal | 13:00 a 18:00": 6,
        "Drive | 18:00 a 21:00": 7, "Sucursal | 18:00 a 21:00": 8
    }

    df['Prioridad'] = df.apply(lambda r: mapping.get(f"{r['MODALIDAD DE ENTREGA']} | {r['BANDA HORARIA']}", 99), axis=1)

    return df.sort_values('Prioridad'), fecha_tit_str


# =========================
# PLANILLA 1 (ORIGINAL)
# =========================
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


# =========================
# PLANILLA 2 (SEGURIDAD)
# =========================
class PlanillaPDF_Seguridad(FPDF):
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
        self.multi_cell(100, 5, f"Planilla CONTROL SEGURIDAD\nEntrega del día: {self.fecha_tit}\nTienda: [268]", align='R')

        self.ln(6)
        self.set_fill_color(220, 220, 220)
        self.set_font("Times", 'B', 9)

        cols = ["Nro PEDIDO", "MODALIDAD", "BANDA", "NOMBRE", "APELLIDO", "DIRECCIÓN", "PICKER", "#"]

        # 🔧 Ajuste de anchos (total ≈ 196)
        widths = [28, 20, 18, 22, 22, 47, 30, 9]

        for i, col in enumerate(cols):
            self.cell(widths[i], 7.5, col, border=1, fill=True, align='C')
        self.ln()


# =========================
# GENERADOR PLANILLA 1
# =========================
def generar_pdf_clientes(df, fecha_tit):
    pdf = PlanillaPDF(fecha_tit)
    pdf.add_page()

    widths = [28, 20, 32, 22, 22, 47, 25]

    for _, row in df.iterrows():
        pdf.cell(widths[0], 5, str(row['NUMERO PEDIDO']).replace(".0", ""), border=1)
        pdf.cell(widths[1], 5, str(row['MODALIDAD DE ENTREGA'])[:10], border=1)
        pdf.cell(widths[2], 5, str(row['BANDA HORARIA'])[:18], border=1)
        pdf.cell(widths[3], 5, str(row['NOMBRE'])[:12], border=1)
        pdf.cell(widths[4], 5, str(row['APELLIDO'])[:12], border=1)
        pdf.cell(widths[5], 5, str(row['DIRECCIÓN'])[:31], border=1)
        pdf.cell(widths[6], 5, str(row['TEL. PARTICULAR'])[:13], border=1)
        pdf.ln()

    return bytes(pdf.output())


# =========================
# GENERADOR PLANILLA 2
# =========================
def generar_pdf_clientes_seguridad(df, fecha_tit):
    pdf = PlanillaPDF_Seguridad(fecha_tit)
    pdf.add_page()

    widths = [28, 20, 18, 22, 22, 47, 30, 9]

    for _, row in df.iterrows():
        pdf.cell(widths[0], 5, str(row['NUMERO PEDIDO']).replace(".0", ""), border=1)
        pdf.cell(widths[1], 5, str(row['MODALIDAD DE ENTREGA'])[:10], border=1)
        pdf.cell(widths[2], 5, str(row['BANDA HORARIA'])[:12], border=1)
        pdf.cell(widths[3], 5, str(row['NOMBRE'])[:12], border=1)
        pdf.cell(widths[4], 5, str(row['APELLIDO'])[:12], border=1)
        pdf.cell(widths[5], 5, str(row['DIRECCIÓN'])[:31], border=1)

        # columnas manuales vacías
        pdf.cell(widths[6], 5, "", border=1)  # PICKER
        pdf.cell(widths[7], 5, "", border=1)  # #

        pdf.ln()

    return bytes(pdf.output())
