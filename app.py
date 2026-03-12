import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import logic_clientes, logic_faltantes, logic_domicilios, logic_informe
import os
import json
import hashlib

# --- CONFIGURACION ---
st.set_page_config(
    page_title="Central Logistica T268",
    page_icon="🛒",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- FECHA ARGENTINA (UTC-3) ---
fecha_ar_ahora = datetime.utcnow() - timedelta(hours=3)
hoy_ar = fecha_ar_ahora.date()
manana_ar_obj = hoy_ar + timedelta(days=1)
manana_txt = manana_ar_obj.strftime("%d/%m/%Y")

# --- ARCHIVO DE PERSISTENCIA PARA DATOS MENSUALES ---
DATA_FILE = "pedidos_mensuales.json"

# Diccionario para traducir dias de la semana
DIAS_SEMANA_ES = {
    0: "Lun", 1: "Mar", 2: "Mier", 3: "Jue", 4: "Vie", 5: "Sab", 6: "Dom"
}

def cargar_datos_mensuales():
    """Carga los datos del mes desde el archivo JSON. Reinicia si cambia de mes."""
    try:
        if os.path.exists(DATA_FILE):
            with open(DATA_FILE, "r") as f:
                datos = json.load(f)
            # Verificar si es el mismo mes
            mes_guardado = datos.get("mes", "")
            mes_actual = hoy_ar.strftime("%Y-%m")
            if mes_guardado != mes_actual:
                # Nuevo mes, reiniciar datos
                return {"mes": mes_actual, "pedidos_por_dia": {}, "archivos_procesados": []}
            return datos
        else:
            return {"mes": hoy_ar.strftime("%Y-%m"), "pedidos_por_dia": {}, "archivos_procesados": []}
    except Exception:
        return {"mes": hoy_ar.strftime("%Y-%m"), "pedidos_por_dia": {}, "archivos_procesados": []}

def guardar_datos_mensuales(datos):
    """Guarda los datos del mes en el archivo JSON."""
    try:
        with open(DATA_FILE, "w") as f:
            json.dump(datos, f)
    except Exception:
        pass

def obtener_hash_archivo(archivo_bytes):
    """Genera un hash unico para identificar archivos duplicados."""
    return hashlib.md5(archivo_bytes).hexdigest()

def extraer_fecha_entrega(df):
    """Extrae la fecha de la columna FECHA ENTREGA del DataFrame."""
    col_fecha = None
    for col in df.columns:
        if "FECHA" in str(col).upper() and "ENTREGA" in str(col).upper():
            col_fecha = col
            break
    
    if col_fecha is None:
        return None
    
    try:
        # Obtener el primer valor no nulo de la columna
        fecha_val = df[col_fecha].dropna().iloc[0]
        
        # Si ya es datetime
        if isinstance(fecha_val, (pd.Timestamp, datetime)):
            return fecha_val.date() if hasattr(fecha_val, 'date') else fecha_val
        
        # Si es string, intentar parsear
        fecha_str = str(fecha_val)
        for fmt in ["%d/%m/%Y", "%Y-%m-%d", "%d-%m-%Y", "%d.%m.%Y"]:
            try:
                return datetime.strptime(fecha_str, fmt).date()
            except ValueError:
                continue
        return None
    except Exception:
        return None

def registrar_pedidos_cdp(archivo_bytes, df):
    """Registra los pedidos del archivo CDP si no fue procesado antes."""
    datos = cargar_datos_mensuales()
    
    # Verificar si el archivo ya fue procesado
    archivo_hash = obtener_hash_archivo(archivo_bytes)
    if archivo_hash in datos["archivos_procesados"]:
        return datos, False  # Ya fue procesado, no registrar de nuevo
    
    # Extraer la fecha de entrega del Excel
    fecha_entrega = extraer_fecha_entrega(df)
    if fecha_entrega is None:
        return datos, False
    
    # Solo registrar si la fecha es del mes actual
    if fecha_entrega.strftime("%Y-%m") != datos["mes"]:
        return datos, False
    
    # Registrar los pedidos para esa fecha
    fecha_str = fecha_entrega.strftime("%Y-%m-%d")
    cantidad_pedidos = len(df)
    
    # Guardar la cantidad de pedidos para esa fecha
    datos["pedidos_por_dia"][fecha_str] = cantidad_pedidos
    datos["archivos_procesados"].append(archivo_hash)
    
    guardar_datos_mensuales(datos)
    return datos, True

def obtener_datos_semana(datos_mensuales, inicio_semana):
    """Obtiene los datos de pedidos para la semana especificada."""
    pedidos_semana = []
    dias_labels = []
    
    for i in range(7):
        dia = inicio_semana + timedelta(days=i)
        fecha_str = dia.strftime("%Y-%m-%d")
        dia_semana = DIAS_SEMANA_ES[dia.weekday()]
        dia_num = dia.day
        
        # Formato: "Lun-9", "Mar-10", etc.
        label = f"{dia_semana}-{dia_num}"
        dias_labels.append(label)
        
        # Obtener pedidos de ese dia (0 si no hay datos)
        pedidos = datos_mensuales.get("pedidos_por_dia", {}).get(fecha_str, 0)
        pedidos_semana.append(pedidos)
    
    return dias_labels, pedidos_semana

def calcular_total_mes(datos_mensuales):
    """Calcula el total de pedidos del mes (solo dias con datos)."""
    pedidos_por_dia = datos_mensuales.get("pedidos_por_dia", {})
    return sum(pedidos_por_dia.values())

# --- CSS MODERNO: TEMA OSCURO CON EFECTOS NEON INTENSOS ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700;800;900&display=swap');
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;500;600;700;800;900&display=swap');
    
    /* ===== FONDO OSCURO PRINCIPAL ===== */
    .stApp {
        background: linear-gradient(135deg, #05050a 0%, #0d0d1a 30%, #111125 60%, #0a1628 100%);
        font-family: 'Inter', sans-serif;
    }
    
    /* Patron de fondo con particulas sutiles */
    .stApp::before {
        content: '';
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background-image: 
            radial-gradient(circle at 20% 20%, rgba(0, 150, 255, 0.08) 0%, transparent 40%),
            radial-gradient(circle at 80% 80%, rgba(0, 255, 200, 0.05) 0%, transparent 40%),
            radial-gradient(circle at 50% 50%, rgba(255, 100, 50, 0.03) 0%, transparent 50%);
        pointer-events: none;
        z-index: 0;
    }
    
    /* ===== HEADER FLOTANTE CON NEON ===== */
    .header-container {
        background: linear-gradient(145deg, rgba(15, 15, 30, 0.95), rgba(10, 20, 40, 0.95));
        border-radius: 24px;
        padding: 30px 40px;
        margin-bottom: 30px;
        border: 1px solid rgba(0, 180, 255, 0.4);
        box-shadow: 
            0 10px 40px rgba(0, 0, 0, 0.5),
            0 0 60px rgba(0, 150, 255, 0.15),
            0 0 100px rgba(0, 150, 255, 0.05),
            inset 0 1px 0 rgba(255, 255, 255, 0.1);
        backdrop-filter: blur(20px);
        position: relative;
        overflow: hidden;
    }
    
    .header-container::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 3px;
        background: linear-gradient(90deg, #00d4ff, #00ff88, #ff6b35, #00d4ff);
        background-size: 300% 100%;
        animation: gradient-shift 4s ease infinite;
    }
    
    @keyframes gradient-shift {
        0%, 100% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
    }
    
    @keyframes neon-pulse {
        0%, 100% { opacity: 1; text-shadow: 0 0 20px currentColor, 0 0 40px currentColor, 0 0 60px currentColor; }
        50% { opacity: 0.8; text-shadow: 0 0 10px currentColor, 0 0 20px currentColor, 0 0 30px currentColor; }
    }
    
    @keyframes glow-pulse {
        0%, 100% { box-shadow: 0 0 20px currentColor, 0 0 40px currentColor; }
        50% { box-shadow: 0 0 30px currentColor, 0 0 60px currentColor; }
    }
    
    .title-main {
        color: #ffffff;
        font-family: 'Orbitron', sans-serif;
        font-weight: 900;
        font-size: 2.6em;
        margin: 0;
        text-transform: uppercase;
        letter-spacing: 4px;
        text-shadow: 
            0 0 10px rgba(0, 200, 255, 0.8),
            0 0 20px rgba(0, 200, 255, 0.6),
            0 0 40px rgba(0, 200, 255, 0.4),
            0 0 80px rgba(0, 200, 255, 0.2);
    }
    
    .subtitle-main {
        color: rgba(255, 255, 255, 0.75);
        font-size: 1.15em;
        margin-top: 10px;
        font-weight: 400;
        letter-spacing: 2px;
    }
    
    .date-badge {
        display: inline-block;
        background: linear-gradient(135deg, #0066ff, #00d4ff);
        color: white;
        padding: 6px 18px;
        border-radius: 25px;
        font-size: 0.9em;
        font-weight: 700;
        margin-left: 12px;
        box-shadow: 0 0 20px rgba(0, 150, 255, 0.5);
    }
    

    
    /* ===== BOTONES NEON FLOTANTES CON GLOW POSTERIOR ===== */
    div.stButton > button {
        background: linear-gradient(145deg, rgba(20, 20, 40, 0.95), rgba(10, 10, 25, 0.95)) !important;
        border-radius: 18px !important;
        height: 5.5em !important;
        font-weight: 800 !important;
        font-size: 1em !important;
        text-transform: uppercase !important;
        letter-spacing: 2px !important;
        color: white !important;
        border: 2px solid rgba(255, 255, 255, 0.15) !important;
        box-shadow: 
            0 10px 30px rgba(0, 0, 0, 0.5),
            inset 0 1px 0 rgba(255, 255, 255, 0.1) !important;
        transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1) !important;
        position: relative !important;
        overflow: visible !important;
    }
    
    /* BOTON CLIENTES - Verde Neon */
    div[data-testid="stHorizontalBlock"] > div:nth-child(1) div.stButton > button {
        border-color: rgba(0, 255, 136, 0.6) !important;
        box-shadow: 
            0 10px 30px rgba(0, 0, 0, 0.5),
            0 0 40px rgba(0, 255, 136, 0.3),
            0 0 80px rgba(0, 255, 136, 0.15),
            inset 0 1px 0 rgba(255, 255, 255, 0.1) !important;
        text-shadow: 0 0 10px rgba(0, 255, 136, 0.5);
    }
    div[data-testid="stHorizontalBlock"] > div:nth-child(1) div.stButton > button:hover {
        border-color: rgba(0, 255, 136, 1) !important;
        box-shadow: 
            0 15px 40px rgba(0, 0, 0, 0.6),
            0 0 60px rgba(0, 255, 136, 0.5),
            0 0 100px rgba(0, 255, 136, 0.3),
            0 0 140px rgba(0, 255, 136, 0.15),
            inset 0 1px 0 rgba(255, 255, 255, 0.2) !important;
        transform: translateY(-5px) scale(1.02) !important;
        text-shadow: 0 0 20px rgba(0, 255, 136, 0.8);
    }
    
    /* BOTON FALTANTES - Azul Neon */
    div[data-testid="stHorizontalBlock"] > div:nth-child(2) div.stButton > button {
        border-color: rgba(0, 180, 255, 0.6) !important;
        box-shadow: 
            0 10px 30px rgba(0, 0, 0, 0.5),
            0 0 40px rgba(0, 180, 255, 0.3),
            0 0 80px rgba(0, 180, 255, 0.15),
            inset 0 1px 0 rgba(255, 255, 255, 0.1) !important;
        text-shadow: 0 0 10px rgba(0, 180, 255, 0.5);
    }
    div[data-testid="stHorizontalBlock"] > div:nth-child(2) div.stButton > button:hover {
        border-color: rgba(0, 180, 255, 1) !important;
        box-shadow: 
            0 15px 40px rgba(0, 0, 0, 0.6),
            0 0 60px rgba(0, 180, 255, 0.5),
            0 0 100px rgba(0, 180, 255, 0.3),
            0 0 140px rgba(0, 180, 255, 0.15),
            inset 0 1px 0 rgba(255, 255, 255, 0.2) !important;
        transform: translateY(-5px) scale(1.02) !important;
        text-shadow: 0 0 20px rgba(0, 180, 255, 0.8);
    }
    
    /* BOTON DOMICILIOS - Naranja/Ambar Neon */
    div[data-testid="stHorizontalBlock"] > div:nth-child(3) div.stButton > button {
        border-color: rgba(255, 170, 0, 0.6) !important;
        box-shadow: 
            0 10px 30px rgba(0, 0, 0, 0.5),
            0 0 40px rgba(255, 170, 0, 0.3),
            0 0 80px rgba(255, 170, 0, 0.15),
            inset 0 1px 0 rgba(255, 255, 255, 0.1) !important;
        text-shadow: 0 0 10px rgba(255, 170, 0, 0.5);
    }
    div[data-testid="stHorizontalBlock"] > div:nth-child(3) div.stButton > button:hover {
        border-color: rgba(255, 170, 0, 1) !important;
        box-shadow: 
            0 15px 40px rgba(0, 0, 0, 0.6),
            0 0 60px rgba(255, 170, 0, 0.5),
            0 0 100px rgba(255, 170, 0, 0.3),
            0 0 140px rgba(255, 170, 0, 0.15),
            inset 0 1px 0 rgba(255, 255, 255, 0.2) !important;
        transform: translateY(-5px) scale(1.02) !important;
        text-shadow: 0 0 20px rgba(255, 170, 0, 0.8);
    }
    
    /* BOTON INFORME - Rojo/Coral Neon */
    div[data-testid="stHorizontalBlock"] > div:nth-child(4) div.stButton > button {
        border-color: rgba(255, 90, 50, 0.6) !important;
        box-shadow: 
            0 10px 30px rgba(0, 0, 0, 0.5),
            0 0 40px rgba(255, 90, 50, 0.3),
            0 0 80px rgba(255, 90, 50, 0.15),
            inset 0 1px 0 rgba(255, 255, 255, 0.1) !important;
        text-shadow: 0 0 10px rgba(255, 90, 50, 0.5);
    }
    div[data-testid="stHorizontalBlock"] > div:nth-child(4) div.stButton > button:hover {
        border-color: rgba(255, 90, 50, 1) !important;
        box-shadow: 
            0 15px 40px rgba(0, 0, 0, 0.6),
            0 0 60px rgba(255, 90, 50, 0.5),
            0 0 100px rgba(255, 90, 50, 0.3),
            0 0 140px rgba(255, 90, 50, 0.15),
            inset 0 1px 0 rgba(255, 255, 255, 0.2) !important;
        transform: translateY(-5px) scale(1.02) !important;
        text-shadow: 0 0 20px rgba(255, 90, 50, 0.8);
    }
    
    /* Link Button (Planilla MEC) - Violeta Neon */
    .stLinkButton > a {
        background: linear-gradient(145deg, rgba(20, 20, 40, 0.95), rgba(10, 10, 25, 0.95)) !important;
        border-radius: 18px !important;
        height: 5.5em !important;
        font-weight: 800 !important;
        font-size: 1em !important;
        text-transform: uppercase !important;
        letter-spacing: 2px !important;
        color: white !important;
        border: 2px solid rgba(180, 100, 255, 0.6) !important;
        box-shadow: 
            0 10px 30px rgba(0, 0, 0, 0.5),
            0 0 40px rgba(180, 100, 255, 0.3),
            0 0 80px rgba(180, 100, 255, 0.15),
            inset 0 1px 0 rgba(255, 255, 255, 0.1) !important;
        transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1) !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        text-shadow: 0 0 10px rgba(180, 100, 255, 0.5);
    }
    
    .stLinkButton > a:hover {
        border-color: rgba(180, 100, 255, 1) !important;
        box-shadow: 
            0 15px 40px rgba(0, 0, 0, 0.6),
            0 0 60px rgba(180, 100, 255, 0.5),
            0 0 100px rgba(180, 100, 255, 0.3),
            0 0 140px rgba(180, 100, 255, 0.15),
            inset 0 1px 0 rgba(255, 255, 255, 0.2) !important;
        transform: translateY(-5px) scale(1.02) !important;
        text-decoration: none !important;
        text-shadow: 0 0 20px rgba(180, 100, 255, 0.8);
    }
    
    /* ===== TARJETAS FLOTANTES GLASSMORPHISM ===== */
    .glass-card {
        background: linear-gradient(145deg, rgba(15, 15, 30, 0.85), rgba(10, 15, 35, 0.75));
        border-radius: 24px;
        padding: 30px;
        border: 1px solid rgba(255, 255, 255, 0.1);
        box-shadow: 
            0 20px 50px rgba(0, 0, 0, 0.5),
            0 0 0 1px rgba(255, 255, 255, 0.05),
            inset 0 1px 0 rgba(255, 255, 255, 0.1);
        backdrop-filter: blur(20px);
        position: relative;
        overflow: hidden;
        margin-bottom: 25px;
    }
    
    .glass-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 3px;
        background: linear-gradient(90deg, transparent, rgba(0, 200, 255, 0.6), transparent);
    }
    
    .glass-card-green::before {
        background: linear-gradient(90deg, transparent, rgba(0, 255, 136, 0.7), transparent);
    }
    
    .glass-card-green {
        border-color: rgba(0, 255, 136, 0.2);
        box-shadow: 
            0 20px 50px rgba(0, 0, 0, 0.5),
            0 0 60px rgba(0, 255, 136, 0.1),
            inset 0 1px 0 rgba(255, 255, 255, 0.1);
    }
    
    .glass-card-orange::before {
        background: linear-gradient(90deg, transparent, rgba(255, 150, 50, 0.7), transparent);
    }
    
    .glass-card-orange {
        border-color: rgba(255, 150, 50, 0.2);
        box-shadow: 
            0 20px 50px rgba(0, 0, 0, 0.5),
            0 0 60px rgba(255, 150, 50, 0.1),
            inset 0 1px 0 rgba(255, 255, 255, 0.1);
    }
    
    .glass-card-blue::before {
        background: linear-gradient(90deg, transparent, rgba(0, 180, 255, 0.7), transparent);
    }
    
    .glass-card-blue {
        border-color: rgba(0, 180, 255, 0.2);
        box-shadow: 
            0 20px 50px rgba(0, 0, 0, 0.5),
            0 0 60px rgba(0, 180, 255, 0.1),
            inset 0 1px 0 rgba(255, 255, 255, 0.1);
    }
    
    .card-icon {
        font-size: 1.6em;
        margin-right: 12px;
    }
    
    .card-title {
        color: #ffffff;
        font-weight: 700;
        font-size: 1.05em;
        text-transform: uppercase;
        letter-spacing: 2px;
        display: flex;
        align-items: center;
        margin-bottom: 25px;
        text-shadow: 0 0 15px rgba(255, 255, 255, 0.3);
    }
    
    /* ===== FILE UPLOADER MODERNO ===== */
    [data-testid="stFileUploader"] {
        background: rgba(255, 255, 255, 0.03);
        border-radius: 16px;
        padding: 20px;
        border: 2px dashed rgba(255, 255, 255, 0.2);
        transition: all 0.3s ease;
    }
    
    [data-testid="stFileUploader"]:hover {
        border-color: rgba(0, 200, 255, 0.5);
        background: rgba(0, 200, 255, 0.05);
        box-shadow: 0 0 30px rgba(0, 200, 255, 0.1);
    }
    
    [data-testid="stFileUploader"] label {
        color: rgba(255, 255, 255, 0.7) !important;
    }
    
    /* ===== TEXT AREA MODERNO ===== */
    .stTextArea textarea {
        background: rgba(255, 255, 255, 0.03) !important;
        border: 2px solid rgba(255, 255, 255, 0.15) !important;
        border-radius: 16px !important;
        color: white !important;
        font-family: 'Inter', sans-serif !important;
        font-size: 1em !important;
        padding: 15px !important;
    }
    
    .stTextArea textarea:focus {
        border-color: rgba(0, 200, 255, 0.6) !important;
        box-shadow: 
            0 0 30px rgba(0, 200, 255, 0.2),
            0 0 60px rgba(0, 200, 255, 0.1) !important;
    }
    
    .stTextArea textarea::placeholder {
        color: rgba(255, 255, 255, 0.4) !important;
    }
    
    /* ===== METRICAS NEON - NUMEROS BRILLANTES ===== */
    [data-testid="stMetric"] {
        background: linear-gradient(145deg, rgba(0, 150, 255, 0.15), rgba(0, 80, 180, 0.1));
        border-radius: 20px;
        padding: 25px;
        border: 2px solid rgba(0, 200, 255, 0.4);
        box-shadow: 
            0 10px 40px rgba(0, 0, 0, 0.4),
            0 0 50px rgba(0, 200, 255, 0.15),
            0 0 100px rgba(0, 200, 255, 0.05);
        position: relative;
        overflow: hidden;
    }
    
    [data-testid="stMetric"]::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 2px;
        background: linear-gradient(90deg, transparent, rgba(0, 255, 200, 0.8), transparent);
    }
    
    [data-testid="stMetricLabel"] {
        color: rgba(255, 255, 255, 0.8) !important;
        font-weight: 700 !important;
        text-transform: uppercase !important;
        letter-spacing: 2px !important;
        font-size: 0.85em !important;
    }
    
    [data-testid="stMetricValue"] {
        color: #00ffcc !important;
        font-family: 'Orbitron', sans-serif !important;
        font-weight: 900 !important;
        font-size: 3em !important;
        text-shadow: 
            0 0 10px rgba(0, 255, 200, 1),
            0 0 20px rgba(0, 255, 200, 0.8),
            0 0 40px rgba(0, 255, 200, 0.6),
            0 0 80px rgba(0, 255, 200, 0.4),
            0 0 120px rgba(0, 255, 200, 0.2) !important;
        animation: neon-pulse 2s ease-in-out infinite;
    }
    
    [data-testid="stMetricDelta"] {
        color: #00ff88 !important;
        font-weight: 600 !important;
        text-shadow: 0 0 10px rgba(0, 255, 136, 0.5);
    }
    
    /* ===== CONTADOR NEON PERSONALIZADO ===== */
    .neon-counter {
        font-family: 'Orbitron', sans-serif;
        font-weight: 900;
        font-size: 4em;
        color: #00ffcc;
        text-align: center;
        padding: 30px;
        text-shadow: 
            0 0 10px rgba(0, 255, 200, 1),
            0 0 20px rgba(0, 255, 200, 0.9),
            0 0 40px rgba(0, 255, 200, 0.7),
            0 0 80px rgba(0, 255, 200, 0.5),
            0 0 120px rgba(0, 255, 200, 0.3);
        animation: neon-pulse 2s ease-in-out infinite;
    }
    
    .neon-counter-label {
        font-family: 'Inter', sans-serif;
        font-weight: 600;
        font-size: 0.9em;
        color: rgba(255, 255, 255, 0.7);
        text-transform: uppercase;
        letter-spacing: 3px;
        text-align: center;
        margin-top: 10px;
    }
    
    .neon-counter-orange {
        color: #ffaa00;
        text-shadow: 
            0 0 10px rgba(255, 170, 0, 1),
            0 0 20px rgba(255, 170, 0, 0.9),
            0 0 40px rgba(255, 170, 0, 0.7),
            0 0 80px rgba(255, 170, 0, 0.5),
            0 0 120px rgba(255, 170, 0, 0.3);
    }
    
    .neon-counter-blue {
        color: #00d4ff;
        text-shadow: 
            0 0 10px rgba(0, 212, 255, 1),
            0 0 20px rgba(0, 212, 255, 0.9),
            0 0 40px rgba(0, 212, 255, 0.7),
            0 0 80px rgba(0, 212, 255, 0.5),
            0 0 120px rgba(0, 212, 255, 0.3);
    }
    
    .neon-counter-green {
        color: #00ff88;
        text-shadow: 
            0 0 10px rgba(0, 255, 136, 1),
            0 0 20px rgba(0, 255, 136, 0.9),
            0 0 40px rgba(0, 255, 136, 0.7),
            0 0 80px rgba(0, 255, 136, 0.5),
            0 0 120px rgba(0, 255, 136, 0.3);
    }
    
    /* ===== GRAFICOS ===== */
    [data-testid="stVegaLiteChart"] {
        background: rgba(255, 255, 255, 0.02);
        border-radius: 16px;
        padding: 20px;
        border: 1px solid rgba(255, 255, 255, 0.05);
    }
    
    /* ===== MENSAJES DE ESTADO ===== */
    .stSuccess {
        background: linear-gradient(145deg, rgba(0, 255, 136, 0.15), rgba(0, 200, 100, 0.1)) !important;
        border: 2px solid rgba(0, 255, 136, 0.5) !important;
        border-radius: 16px !important;
        color: #00ff88 !important;
        box-shadow: 0 0 30px rgba(0, 255, 136, 0.1);
    }
    
    .stInfo {
        background: linear-gradient(145deg, rgba(0, 180, 255, 0.15), rgba(0, 120, 200, 0.1)) !important;
        border: 2px solid rgba(0, 180, 255, 0.5) !important;
        border-radius: 16px !important;
        color: #00d4ff !important;
        box-shadow: 0 0 30px rgba(0, 180, 255, 0.1);
    }
    
    .stWarning {
        background: linear-gradient(145deg, rgba(255, 170, 0, 0.15), rgba(200, 130, 0, 0.1)) !important;
        border: 2px solid rgba(255, 170, 0, 0.5) !important;
        border-radius: 16px !important;
        color: #ffcc00 !important;
        box-shadow: 0 0 30px rgba(255, 170, 0, 0.1);
    }
    
    /* ===== DOWNLOAD BUTTON NEON ===== */
    .stDownloadButton > button {
        background: linear-gradient(135deg, #0066ff, #00d4ff) !important;
        border: none !important;
        border-radius: 14px !important;
        color: white !important;
        font-weight: 700 !important;
        text-transform: uppercase !important;
        letter-spacing: 1.5px !important;
        box-shadow: 
            0 8px 30px rgba(0, 150, 255, 0.4),
            0 0 40px rgba(0, 150, 255, 0.2) !important;
        transition: all 0.3s ease !important;
    }
    
    .stDownloadButton > button:hover {
        transform: translateY(-3px) scale(1.02) !important;
        box-shadow: 
            0 12px 40px rgba(0, 150, 255, 0.5),
            0 0 60px rgba(0, 150, 255, 0.3) !important;
    }
    
    /* ===== ESPACIADO ===== */
    .block-container {
        padding-top: 2.5rem !important;
        padding-bottom: 2.5rem !important;
        max-width: 1500px !important;
    }
    
    /* ===== SCROLLBAR NEON ===== */
    ::-webkit-scrollbar {
        width: 10px;
        height: 10px;
    }
    
    ::-webkit-scrollbar-track {
        background: rgba(255, 255, 255, 0.03);
        border-radius: 5px;
    }
    
    ::-webkit-scrollbar-thumb {
        background: linear-gradient(180deg, #0066ff, #00d4ff);
        border-radius: 5px;
        box-shadow: 0 0 10px rgba(0, 150, 255, 0.5);
    }
    
    ::-webkit-scrollbar-thumb:hover {
        background: linear-gradient(180deg, #0088ff, #00e5ff);
        box-shadow: 0 0 15px rgba(0, 150, 255, 0.7);
    }
    
    /* Hide default Streamlit elements */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    </style>
""", unsafe_allow_html=True)

# --- HEADER MODERNO ---
# Cargar logo como base64 para incluirlo en HTML
import base64

def get_image_base64(image_path):
    try:
        with open(image_path, "rb") as img_file:
            return base64.b64encode(img_file.read()).decode()
    except:
        return None

logo_base64 = get_image_base64("carrefour+logo.png")
logo_html = ""
if logo_base64:
    logo_html = f'<img src="data:image/png;base64,{logo_base64}" style="height: 80px; width: auto;" alt="Carrefour">'
else:
    logo_html = '<span style="color: rgba(255,255,255,0.5);">Logo</span>'

st.markdown("""
    <div class="header-container">
        <div style="display: flex; align-items: center; justify-content: space-between; flex-wrap: wrap;">
            <div>
                <h1 class="title-main">Central Online T-268</h1>
                <p class="subtitle-main">Rosario - Gestion de Ventas Online 
                    <span class="date-badge">""" + hoy_ar.strftime("%d/%m/%Y") + """</span>
                </p>
            </div>
            <div style="padding-right: 20px;">
                """ + logo_html + """
            </div>
        </div>
    </div>
""", unsafe_allow_html=True)

# --- FILA DE BOTONES NEON ---
st.write("")
b1, b2, b3, b4, b5 = st.columns(5)
with b1: 
    btn_1 = st.button("CLIENTES", key="top_1", use_container_width=True)
with b2: 
    btn_2 = st.button("FALTANTES", key="top_2", use_container_width=True)
with b3: 
    btn_3 = st.button("DOMICILIOS", key="top_3", use_container_width=True)
with b4: 
    btn_4 = st.button("INFORME", key="top_4", use_container_width=True)
with b5: 
    st.link_button("PLANILLA MEC", "https://docs.google.com/spreadsheets/d/1v0Rls8fg_uIGfhA1t3CzINq3VfAUvPY3DY8_m_ZSmM8/edit#gid=0", use_container_width=True)

# --- CUERPO PRINCIPAL ---
st.write("")
st.write("")
col_izq, col_der = st.columns([1, 1], gap="large")

with col_izq:
    # --- TARJETA 1: CARGA CDP ---
    st.markdown('<div class="card-title" style="margin-bottom: 15px;"><span class="card-icon">📂</span> CARGAR EXCEL DE CDP (OPERACIONES CARREFOUR ONLINE)</div>', unsafe_allow_html=True)
    archivo_cdp = st.file_uploader("Subir CDP", type=["xlsx"], label_visibility="collapsed", key="cdp_upload")
    
    # Variables para almacenar datos del CDP
    df_clean = None
    fecha_tit = None
    archivo_cdp_bytes = None
    
    if archivo_cdp:
        # Leer el archivo como bytes para hashear
        archivo_cdp_bytes = archivo_cdp.read()
        archivo_cdp.seek(0)  # Resetear el puntero para pd.read_excel
        
        df_raw = pd.read_excel(archivo_cdp)
        df_clean, fecha_tit = logic_clientes.motor_limpieza(df_raw)
        
        # Registrar pedidos para el grafico (evita duplicados)
        datos_actualizados, fue_registrado = registrar_pedidos_cdp(archivo_cdp_bytes, df_raw)
        
        st.success(f"CDP CARGADO: {fecha_tit}")
        
        # PROCESAMIENTO DE BOTONES
        if btn_1:
            pdf = logic_clientes.generar_pdf_clientes(df_clean, fecha_tit)
            st.download_button("DESCARGAR PDF CLIENTES", bytes(pdf), f"Clientes_{fecha_tit}.pdf", use_container_width=True)
        if btn_2:
            pdf = logic_faltantes.generar_pdf_faltantes(df_clean, fecha_tit)
            st.download_button("DESCARGAR PDF FALTANTES", bytes(pdf), f"Faltantes_{fecha_tit}.pdf", use_container_width=True)
        if btn_3:
            pdf = logic_domicilios.generar_pdf_domicilios(df_clean, fecha_tit)
            st.download_button("DESCARGAR PDF RUTAS", bytes(pdf), f"Rutas_{fecha_tit}.pdf", use_container_width=True)

    st.write("")
    st.write("")

    # --- TARJETA 2: INFORME ---
    st.markdown(f'<div class="card-title" style="margin-bottom: 15px;"><span class="card-icon">📝</span> PROCESADOR DE INFORME (MAÑANA {manana_txt})</div>', unsafe_allow_html=True)
    archivo_inf = st.file_uploader("Subir CDP Manana", type=["xlsx"], key="inf_upload", label_visibility="collapsed")
    obs = st.text_area("Observaciones:", height=100, placeholder="Ingresa las novedades del turno aqui...", key="obs_area")
    
    if btn_4:
        if archivo_inf:
            df_inf_raw = pd.read_excel(archivo_inf)
            df_inf_clean, fecha_inf_tit = logic_clientes.motor_limpieza(df_inf_raw)
            pdf_bytes = logic_informe.generar_pdf_informe(df_inf_clean, obs)
            st.download_button("DESCARGAR REPORTE FINAL", pdf_bytes, f"Informe_{fecha_inf_tit}.pdf", use_container_width=True)
        else:
            st.warning("Cargue el CDP de manana primero.")

with col_der:
    # --- PANEL DE VISUALIZACION ---
    st.markdown('<div class="card-title" style="margin-bottom: 20px;"><span class="card-icon">📈</span> PANEL DE VISUALIZACION DE VENTAS ONLINE</div>', unsafe_allow_html=True)
    
    # Calcular fechas de la semana actual
    inicio_semana = hoy_ar - timedelta(days=hoy_ar.weekday())
    fin_semana = inicio_semana + timedelta(days=6)
    
    # Meses en español para el rango
    MESES_ES = {1: "Ene", 2: "Feb", 3: "Mar", 4: "Abr", 5: "May", 6: "Jun",
                7: "Jul", 8: "Ago", 9: "Sep", 10: "Oct", 11: "Nov", 12: "Dic"}
    rango_semana = f"Semana {inicio_semana.day}-{MESES_ES[inicio_semana.month]} al {fin_semana.day}-{MESES_ES[fin_semana.month]}"
    
    # Cargar datos mensuales guardados
    datos_mensuales = cargar_datos_mensuales()
    
    # Obtener datos de la semana actual
    dias_labels, pedidos_semana = obtener_datos_semana(datos_mensuales, inicio_semana)
    
    # Calcular total del mes (solo dias con datos reales)
    total_pedidos_mes = calcular_total_mes(datos_mensuales)
    
    # Obtener pedidos del dia actual desde los datos guardados
    fecha_hoy_str = hoy_ar.strftime("%Y-%m-%d")
    pedidos_dia_actual = datos_mensuales.get("pedidos_por_dia", {}).get(fecha_hoy_str, 0)
    
    # Si se acaba de cargar un archivo CDP, usar esos datos
    if archivo_cdp and df_clean is not None:
        # Extraer fecha del archivo para mostrar
        fecha_archivo = extraer_fecha_entrega(df_raw)
        if fecha_archivo:
            fecha_archivo_str = fecha_archivo.strftime("%Y-%m-%d")
            pedidos_dia_actual = datos_mensuales.get("pedidos_por_dia", {}).get(fecha_archivo_str, len(df_clean))
    
    # Contadores Neon compactos
    col_n1, col_n2 = st.columns(2)
    with col_n1:
        if pedidos_dia_actual > 0:
            st.markdown(f'''
                <div style="text-align: center; padding: 8px 0;">
                    <div class="neon-counter neon-counter-green" style="font-size: 2.2em;">{pedidos_dia_actual}</div>
                    <div class="neon-counter-label" style="font-size: 0.7em;">Pedidos del Dia</div>
                </div>
            ''', unsafe_allow_html=True)
        else:
            st.markdown('''
                <div style="text-align: center; padding: 8px 0;">
                    <div class="neon-counter neon-counter-green" style="opacity: 0.4; font-size: 2.2em;">--</div>
                    <div class="neon-counter-label" style="font-size: 0.7em;">Pedidos del Dia</div>
                </div>
            ''', unsafe_allow_html=True)
    
    with col_n2:
        if total_pedidos_mes > 0:
            st.markdown(f'''
                <div style="text-align: center; padding: 8px 0;">
                    <div class="neon-counter neon-counter-blue" style="font-size: 2.2em;">{total_pedidos_mes}</div>
                    <div class="neon-counter-label" style="font-size: 0.7em;">Total Pedidos del Mes</div>
                </div>
            ''', unsafe_allow_html=True)
        else:
            st.markdown('''
                <div style="text-align: center; padding: 8px 0;">
                    <div class="neon-counter neon-counter-blue" style="opacity: 0.4; font-size: 2.2em;">--</div>
                    <div class="neon-counter-label" style="font-size: 0.7em;">Total Pedidos del Mes</div>
                </div>
            ''', unsafe_allow_html=True)
    
    # Rango de semana compacto
    st.markdown(f'''
        <div style="text-align: center; margin: 5px 0;">
            <span style="color: rgba(255,255,255,0.5); font-size: 0.75em; letter-spacing: 1px;">
                {rango_semana}
            </span>
        </div>
    ''', unsafe_allow_html=True)
    
    # Crear DataFrame para el grafico con datos reales
    chart_data = pd.DataFrame({
        'Dia': dias_labels,
        'Pedidos': pedidos_semana
    })
    
    # Grafico compacto con Altair
    import altair as alt
    
    # Determinar opacidad basada en si hay datos
    tiene_datos = any(p > 0 for p in pedidos_semana)
    opacidad_barras = 1.0 if tiene_datos else 0.5
    color_labels = 'rgba(255,255,255,0.6)' if tiene_datos else 'rgba(255,255,255,0.3)'
    
    chart = alt.Chart(chart_data).mark_bar(
        cornerRadiusTopLeft=4,
        cornerRadiusTopRight=4,
        color='#00ffcc',
        opacity=opacidad_barras
    ).encode(
        x=alt.X('Dia:N', sort=None, axis=alt.Axis(
            labelColor=color_labels,
            labelAngle=0,  # Horizontal
            labelFontSize=10,
            title=None
        )),
        y=alt.Y('Pedidos:Q', axis=alt.Axis(
            labelColor=color_labels,
            gridColor='rgba(255,255,255,0.08)',
            title=None
        )),
        tooltip=['Dia', 'Pedidos']
    ).properties(
        height=160
    ).configure(
        background='transparent'
    ).configure_view(
        strokeWidth=0
    )
    
    st.altair_chart(chart, use_container_width=True)
    
    # Mensaje informativo si no hay archivo cargado
    if not archivo_cdp:
        st.info("Suba un archivo de CDP para visualizar las metricas del dia")

# --- FOOTER ---
st.markdown('''
    <div style="text-align: center; padding: 20px;">
        <p style="color: rgba(255, 255, 255, 0.4); font-size: 0.85em; letter-spacing: 2px;">
            CENTRAL DE ARMADO T268 | CARREFOUR ONLINE | ROSARIO
        </p>
    </div>
''', unsafe_allow_html=True)



