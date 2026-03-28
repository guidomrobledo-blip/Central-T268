from fpdf import FPDF
from datetime import datetime

class DomiciliosPDF(FPDF):

    def header(self):
        self.set_font("Arial", "B", 12)
        self.cell(0, 8, self.titulo, ln=True, align="C")
        self.ln(2)

    def footer(self):
        # 🔒 Pie fijo (referencia visual del margen)
        self.set_y(-12)
        self.set_font("Arial", "I", 7)
        self.cell(0, 5, f"Página {self.page_no()}", align="C")


def generar_pdf_domicilios(df, tienda, fecha_str):

    pdf = DomiciliosPDF(orientation='P', unit='mm', format='A4')
    pdf.set_auto_page_break(auto=False)  # 🔒 control manual TOTAL
    pdf.set_margins(left=7, top=10, right=7)

    pdf.titulo = f"Domicilios por visitar hoy: {fecha_str}\nTienda: [{tienda}]"

    pdf.add_page()

    # 🔧 CONFIGURACIÓN CLAVE
    h_celda = 5
    limite_inferior = 297 - 12   # 👉 AJUSTÁ ESTE VALOR A GUSTO (10–15 ideal)

    # Agrupar por banda
    bandas = df["BANDA HORARIA"].unique()

    for banda in bandas:

        df_banda = df[df["BANDA HORARIA"] == banda]

        # 🔒 Control antes de iniciar banda
        if pdf.get_y() + (h_celda * 3) > limite_inferior:
            pdf.add_page()

        # 🧾 Título de banda
        pdf.set_font("Arial", "B", 9)
        pdf.cell(0, 6, f"--- Domicilio | {banda} ---", ln=True)

        # 🧾 Encabezado tabla
        pdf.set_font("Arial", "B", 8)
        pdf.cell(10, 6, "#", border=1)
        pdf.cell(30, 6, "Nro Pedido", border=1)
        pdf.cell(30, 6, "Modalidad", border=1)
        pdf.cell(35, 6, "Banda Horaria", border=1)
        pdf.cell(0, 6, "Dirección", border=1, ln=True)

        # 🔢 Numeración por banda
        contador = 1

        for _, row in df_banda.iterrows():

            # 🧠 CONTROL REAL DEL MARGEN (clave)
            if pdf.get_y() + h_celda > limite_inferior:
                pdf.add_page()

                # 🔁 Repetir banda (continuación)
                pdf.set_font("Arial", "B", 9)
                pdf.cell(0, 6, f"--- Domicilio | {banda} --- (continúa)", ln=True)

                # 🔁 Repetir encabezado
                pdf.set_font("Arial", "B", 8)
                pdf.cell(10, 6, "#", border=1)
                pdf.cell(30, 6, "Nro Pedido", border=1)
                pdf.cell(30, 6, "Modalidad", border=1)
                pdf.cell(35, 6, "Banda Horaria", border=1)
                pdf.cell(0, 6, "Dirección", border=1, ln=True)

            # 🧾 Fila
            pdf.set_font("Arial", "", 8)
            pdf.cell(10, h_celda, str(contador), border=1)
            pdf.cell(30, h_celda, str(row["Nro Pedido"]), border=1)
            pdf.cell(30, h_celda, "Domicilio", border=1)
            pdf.cell(35, h_celda, banda, border=1)
            pdf.cell(0, h_celda, str(row["Dirección"]), border=1, ln=True)

            contador += 1

        pdf.ln(2)

    # Guardar
    nombre_archivo = f"Domicilios_{fecha_str.replace('/', '_')}.pdf"
    pdf.output(nombre_archivo)

    return nombre_archivo
