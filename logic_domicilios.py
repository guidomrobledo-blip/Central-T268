import pandas as pd
from fpdf import FPDF
import os

class PDFLogistica(FPDF):
    def __init__(self, fecha_tit):
        super().__init__(orientation='P', unit='mm', format='A4')
        self.fecha_tit = fecha_tit
        self.set_margins(left=10, top=7, right=10)
        self.set_auto_page_break(False)

    def header(self):
        # Logos nivelados (y=7)
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

def generar_pdf_domicilios(df, fecha_tit):
    # Filtrado por Domicilio [cite: 1]
    df_logistica = df[df['MODALIDAD DE ENTREGA'].str.contains('Domicilio', case=False, na=False)].copy()

    if df_logistica.empty:
        pdf_v = FPDF()
        pdf_v.add_page()
        pdf_v.set_font("Arial", 'B', 15)
        pdf_v.cell(190, 50, "SIN PEDIDOS DE DOMICILIO", 0, 1, 'C')
        return bytes(pdf_v.output())

    # Ordenamiento por prioridad [cite: 1]
    prioridad_map = {
        "10:00 a 14:00": 1, "14:00 a 18:00": 2, "09:00 a 13:00": 3,
        "13:00 a 18:00": 4, "18:00 a 21:00": 5, "07:00 a 11:00": 6,
        "08:00 a 12:00": 7, "11:00 a 15:00": 8
    }
    df_logistica['Prioridad_L'] = df_logistica['BANDA HORARIA'].map(prioridad_map).fillna(99)
    df_logistica = df_logistica.sort_values('Prioridad_L')

    pdf = PDFLogistica(fecha_tit)
    pdf.add_page()

    # --- AJUSTE DINÁMICO CORREGIDO ---
    total_pedidos = len(df_logistica)
    num_bandas = len(df_logistica['BANDA HORARIA'].unique())
    
    # Reducimos el espacio utilitario para dejar un margen de seguridad al final de la hoja 
    espacio_disponible = 230 
    
    # Cada banda consume: Zócalo Azul + Encabezado Gris + Salto ln(2)
    # Calculamos h_celda restando el peso de los encabezados del total
    espacio_neto = espacio_disponible - (num_bandas * 15) 
    h_celda = max(5.0, min(10.5, espacio_neto / (total_pedidos + num_bandas)))
    
    # Fuente proporcional (ligeramente menor para evitar desbordes laterales) 
    f_size_datos = max(7.0, min(9.5, h_celda * 1.05))

    w_num, w_pedido, w_mod, w_banda, w_dir = 10, 32, 25, 33, 90

    for banda in df_logistica['BANDA HORARIA'].unique():
        df_banda = df_logistica[df_logistica['BANDA HORARIA'] == banda].reset_index(drop=True)

        # Zócalo Azul [cite: 1]
        pdf.set_fill_color(0, 70, 145)
        pdf.set_text_color(255, 255, 255)
        pdf.set_font('Arial', 'B', f_size_datos + 1.5)
        pdf.cell(0, h_celda + 1, f"--- Domicilio | {banda} ---", 1, 1, 'C', True)

        # Encabezado Gris [cite: 1]
        pdf.set_fill_color(220, 220, 220)
        pdf.set_text_color(0, 0, 0)
        pdf.set_font('Arial', 'B', f_size_datos - 1)
        pdf.cell(w_num, h_celda, '#', 1, 0, 'C', True)
        pdf.cell(w_pedido, h_celda, 'Nro PEDIDO', 1, 0, 'C', True)
        pdf.cell(w_mod, h_celda, 'MODALIDAD', 1, 0, 'C', True)
        pdf.cell(w_banda, h_celda, 'BANDA HORARIA', 1, 0, 'C', True)
        pdf.cell(w_dir, h_celda, 'DIRECCIÓN', 1, 1, 'C', True)

        # Filas de Datos [cite: 1]
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
