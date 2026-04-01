from fpdf import FPDF
from datetime import datetime, timedelta
import os

from logic_clientes import motor_limpieza  # reutilizamos limpieza


class PlanillaPDFSeguridad(FPDF):
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
            f"Planilla CONTROL SEGURIDAD\nEntrega del día: {self.fecha_tit}\nTienda: [268]",
            align='R'
        )

        self.ln(6)
        self.set_fill_color(240, 240, 240)
        self.set_font("Times", 'B', 9)

        cols = [
            "Nro PEDIDO", "MODALIDAD", "BANDA",
            "NOMBRE", "APELLIDO", "DIRECCIÓN",
            "PICKER", "#"
        ]

        # Anchos ajustados (manteniendo ancho total)
        widths = [28, 20, 18, 22, 22, 47, 30, 10]

        for i, col in enumerate(cols):
            self.cell(widths[i], 7.5, col, border=1, fill=True, align='C')
        self.ln()


def generar_pdf_seguridad(df, fecha_tit):

    font_size, row_height = 9.5, 5

    while font_size > 6.5:
        pdf = PlanillaPDFSeguridad(fecha_tit)
        pdf.add_page()

        widths = [28, 20, 18, 22, 22, 47, 30, 10]

        ultima_llave = None
        ultima_modalidad = None
        ultima_banda = None

        resumen = {}

        df_render = df.copy()

        def orden_banda(banda):
            orden = {
                "10:00 a 14:00": 1,
                "14:00 a 18:00": 2,
                "09:00 a 13:00": 3,
                "13:00 a 18:00": 4,
                "18:00 a 21:00": 5
            }
            return orden.get(banda, 99)

        df_render['orden_banda'] = df_render['BANDA HORARIA'].apply(orden_banda)
        df_render['orden_tipo'] = df_render['MODALIDAD DE ENTREGA'].apply(
            lambda x: 0 if x == "Domicilio" else 1
        )

        df_render = df_render.sort_values(['orden_banda', 'orden_tipo'])

        def insertar_filas_vacias():
            for _ in range(3):
                if (pdf.h - pdf.get_y()) < 20:
                    pdf.add_page()
                for w in widths:
                    pdf.cell(w, row_height, "", border=1)
                pdf.ln()

        for _, row in df_render.iterrows():
            modalidad = row['MODALIDAD DE ENTREGA']
            banda = row['BANDA HORARIA']

            llave = f"Domicilio | {banda}" if modalidad == "Domicilio" else f"Drive/Sucursal | {banda}"
            llave_resumen = f"Domicilio | {banda}" if modalidad == "Domicilio" else f"Drive/Suc | {banda}"

            resumen[llave_resumen] = resumen.get(llave_resumen, 0) + 1

            if llave != ultima_llave:
                if (
                    ultima_modalidad == "Domicilio" and
                    ultima_banda in ["10:00 a 14:00", "14:00 a 18:00"]
                ):
                    insertar_filas_vacias()

                pdf.set_fill_color(64, 64, 64)
                pdf.set_text_color(255, 255, 255)
                pdf.set_font("Times", 'B', font_size + 2)

                pdf.cell(sum(widths), row_height + 1.5,
                         f"--- {llave} ---", border=1, ln=True, align='C', fill=True)

                pdf.set_text_color(0, 0, 0)
                pdf.set_font("Times", '', font_size)

                ultima_llave = llave
                ultima_modalidad = modalidad
                ultima_banda = banda

            pdf.cell(widths[0], row_height, str(row['NUMERO PEDIDO']).replace(".0", ""), border=1, align='C')
            pdf.cell(widths[1], row_height, str(modalidad)[:10], border=1)
            pdf.cell(widths[2], row_height, str(banda)[:12], border=1)
            pdf.cell(widths[3], row_height, str(row['NOMBRE'])[:12], border=1)
            pdf.cell(widths[4], row_height, str(row['APELLIDO'])[:12], border=1)
            pdf.cell(widths[5], row_height, str(row['DIRECCIÓN'])[:31], border=1)

            # Columnas nuevas (vacías para escritura manual)
            pdf.cell(widths[6], row_height, "", border=1)
            pdf.cell(widths[7], row_height, "", border=1)

            pdf.ln()

        if (
            ultima_modalidad == "Domicilio" and
            ultima_banda in ["10:00 a 14:00", "14:00 a 18:00"]
        ):
            insertar_filas_vacias()

        if (pdf.h - pdf.get_y()) < 35:
            pdf.add_page()

        pdf.ln(4)

        hora_arg = (datetime.utcnow() - timedelta(hours=3)).strftime("%H:%M")

        pdf.set_font("Times", 'B', font_size + 1.5)
        pdf.cell(0, 6, f"Informe de pedidos al momento [{hora_arg} hs]", ln=True, align='R')

        pdf.set_font("Times", '', font_size + 0.5)

        for b, t in resumen.items():
            pdf.cell(0, 4.5, f"{b}: [{t}]", ln=True, align='R')

        pdf.set_font("Times", 'B', font_size + 2)
        pdf.cell(0, 8, f"TOTAL: [{len(df)}]", ln=True, align='R')

        if pdf.page_no() <= 2:
            break

        font_size -= 0.5
        row_height -= 0.3

    return bytes(pdf.output())
