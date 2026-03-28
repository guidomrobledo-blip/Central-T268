from fpdf import FPDF

class DomiciliosPDF(FPDF):

    def header(self):
        self.set_font("Arial", "B", 12)
        self.cell(0, 8, self.titulo, ln=True, align="C")
        self.ln(2)

    def footer(self):
        self.set_y(-12)
        self.set_font("Arial", "I", 7)
        self.cell(0, 5, f"Página {self.page_no()}", align="C")


def generar_pdf_domicilios(df, fecha_str):

    pdf = DomiciliosPDF(orientation='P', unit='mm', format='A4')
    pdf.set_auto_page_break(auto=False)
    pdf.set_margins(left=7, top=10, right=7)

    pdf.titulo = f"Domicilios por visitar hoy: {fecha_str}"

    pdf.add_page()

    h_celda = 5
    limite_inferior = 297 - 12

    bandas = df["BANDA HORARIA"].unique()

    for banda in bandas:

        df_banda = df[df["BANDA HORARIA"] == banda]

        if pdf.get_y() + (h_celda * 3) > limite_inferior:
            pdf.add_page()

        pdf.set_font("Arial", "B", 9)
        pdf.cell(0, 6, f"--- Domicilio | {banda} ---", ln=True)

        pdf.set_font("Arial", "B", 8)
        pdf.cell(10, 6, "#", border=1)
        pdf.cell(30, 6, "Nro Pedido", border=1)
        pdf.cell(30, 6, "Modalidad", border=1)
        pdf.cell(35, 6, "Banda Horaria", border=1)
        pdf.cell(0, 6, "Dirección", border=1, ln=True)

        contador = 1

        for _, row in df_banda.iterrows():

            if pdf.get_y() + h_celda > limite_inferior:
                pdf.add_page()

                pdf.set_font("Arial", "B", 9)
                pdf.cell(0, 6, f"--- Domicilio | {banda} --- (continúa)", ln=True)

                pdf.set_font("Arial", "B", 8)
                pdf.cell(10, 6, "#", border=1)
                pdf.cell(30, 6, "Nro Pedido", border=1)
                pdf.cell(30, 6, "Modalidad", border=1)
                pdf.cell(35, 6, "Banda Horaria", border=1)
                pdf.cell(0, 6, "Dirección", border=1, ln=True)

            pdf.set_font("Arial", "", 8)
            pdf.cell(10, h_celda, str(contador), border=1)
            pdf.cell(30, h_celda, str(row.get("Nro Pedido", "")), border=1)
            pdf.cell(30, h_celda, "Domicilio", border=1)
            pdf.cell(35, h_celda, str(banda), border=1)
            pdf.cell(0, h_celda, str(row.get("Dirección", "")), border=1, ln=True)

            contador += 1

        pdf.ln(2)

    # 🔥 CLAVE PARA STREAMLIT
    pdf_bytes = pdf.output(dest='S').encode('latin-1')
    return pdf_bytes
