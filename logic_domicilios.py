import pandas as pd
from fpdf import FPDF
import os

class PDFLogistica(FPDF):
    def __init__(self, fecha_tit):
        super().__init__(orientation='P', unit='mm', format='A4')
        self.fecha_tit = fecha_tit
        self.set_margins(left=10, top=7, right=10)
        # Establecemos el salto automático a 10mm (1cm) para proteger el pie de página
        self.set_auto_page_break(auto=True, margin=10)

    def header(self):
        if os.path.exists("carrefour+logo.png"):
            self.image("carrefour+logo.png", 10, 7, 45)
        if os.path.exists("imagen_5.png"):
            self.image("imagen_5.png", 63, 2, 30)

        self.set_font('Arial', 'B', 13)
        self.set_text_color(40, 40, 40)
        self.set_xy(100, 7)
        info_header = f"Domicilios por visitar hoy: {self.fecha_tit}\nTienda: [268]"
        self.multi_cell(100, 6, info_header, 0, 'R')
        self.ln(10)

    # Agregamos el pie de página fijo de 1cm
    def footer(self):
        self.set_y(-10) 
        self.set_font('Arial', 'I', 8)
        self.set_text_color(128, 128, 128)
        # Texto opcional para visualizar el límite del borde
        self.cell(0, 5, 'CENTRAL DE ARMADO T268 | CARREFOUR ONLINE | ROSARIO', 0, 0, 'C')

def generar_pdf_domicilios(df, fecha_tit):
    df_logistica = df[df['MODALIDAD DE ENTREGA'].str.contains('Domicilio', case=False, na=False)].copy()

    if df_logistica.empty:
        pdf_v = FPDF()
        pdf_v.add_page()
        pdf_v.set_font("Arial", 'B', 15)
        pdf_v.cell(190, 50, "SIN PEDIDOS DE DOMICILIO", 0, 1, 'C')
        return bytes(pdf_v.output())

    prioridad_map = {
        "10:00 a 14:00": 1, "14:00 a 18:00": 2, "09:00 a 13:00": 3,
        "13:00 a 18:00": 4, "18:00 a 21:00": 5, "07:00 a 11:00": 6,
        "08:00 a 12:00": 7, "11:00 a 15:00": 8
    }
    df_logistica['Prioridad_L'] = df_logistica['BANDA HORARIA'].map(prioridad_map).fillna(99)
    df_logistica = df_logistica.sort_values('Prioridad_L')

    pdf = PDFLogistica(fecha_tit)
    pdf.add_page()

    # --- AJUSTE DINÁMICO CON BORDE DE SEGURIDAD ---
    total_pedidos = len(df_logistica)
    num_bandas = len(df_logistica['BANDA HORARIA'].unique())
    
    # Bajamos de 245 a 235 para garantizar el borde de 1cm (10mm) abajo
    espacio_util = 235 
    
    # El cálculo ahora considera el espacio de los zócalos (num_bandas * 10) 
    # dentro del margen de 235mm
    h_celda = max(5.5, min(12, (espacio_util - (num_bandas * 10)) / total_pedidos))
    f_size_datos = max(7.5, min(10.5, h_celda * 1.1))

    w_num, w_pedido, w_mod, w_banda, w_dir = 10, 32, 25, 33, 90

    for banda in df_logistica['BANDA HORARIA'].unique():
        df_banda = df_logistica[df_logistica['BANDA HORARIA'] == banda].reset_index(drop=True)

        pdf.set_fill_color(0, 70, 145)
        pdf.set_text_color(255, 255, 255)
        pdf.set_font('Arial', 'B', f_size_datos + 2)
        pdf.cell(0, h_celda + 1, f"--- Domicilio | {banda} ---", 1, 1, 'C', True)

        pdf.set_fill_color(220, 220, 220)
        pdf.set_text_color(0, 0, 0)
        pdf.set_font('Arial', 'B', f_size_datos - 1)
        pdf.cell(w_num, h_celda, '#', 1, 0, 'C', True)
        pdf.cell(w_pedido, h_celda, 'Nro PEDIDO', 1, 0, 'C', True)
        pdf.cell(w_mod, h_celda, 'MODALIDAD', 1, 0, 'C', True)
        pdf.cell(w_banda, h_celda, 'BANDA HORARIA', 1, 0, 'C', True)
        pdf.cell(w_dir, h_celda, 'DIRECCIÓN', 1, 1, 'C', True)

        for i, row in df_banda.iterrows():
            fill = (i % 2 == 1)
            pdf.set_fill_color(245, 245, 245)
            pdf.set_font('Arial', '', f_size_datos)
            pdf.cell(w_num, h_celda, str(i+1), 1, 0, 'C', fill)
            
            pdf.set_font('Arial', 'B', f_size_datos)
            pdf.cell(w_pedido, h_celda, str(row['NUMERO PEDIDO']).replace(".0",""), 1, 0, 'C', fill)

            pdf.set_font('Arial', '', f_size_datos)
            valor_original = str(row['MODALIDAD DE ENTREGA'])
            pdf.cell(w_mod, h_celda, valor_original[:15], 1, 0, 'C', fill)
            pdf.cell(w_banda, h_celda, str(row['BANDA HORARIA']), 1, 0, 'C', fill)

            dir_texto = str(row['DIRECCIÓN'])[:65]
            pdf.cell(w_dir, h_celda, dir_texto, 1, 1, 'L', fill)

        pdf.ln(2)

    return bytes(pdf.output())
