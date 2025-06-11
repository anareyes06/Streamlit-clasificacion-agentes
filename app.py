# app.py
import streamlit as st
from utils import cargar_datos, procesar_datos, calcular_tiempos, resumen_por_estado, graficar_tiempos, graficar_estado_altair
import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt
import json
import numpy as np
from matplotlib.colors import LinearSegmentedColormap
from matplotlib.patches import Wedge

# Configuración de página DEBE SER LA PRIMERA LÍNEA DE STREAMLIT
st.set_page_config(page_title="Dashboard de Agentes", layout="wide", page_icon="🍽️")
st.image("https://static.wixstatic.com/media/201dfc_540830a0d22940dcb57449162d3a6362~mv2.png/v1/fill/w_233,h_69,al_c,q_85,usm_0.66_1.00_0.01,enc_avif,quality_auto/201dfc_540830a0d22940dcb57449162d3a6362~mv2.png",  use_container_width=False, width=200) # Adjust width as needed
# Configuración de tema personalizado con paleta rosa (#EC008B)
def set_custom_theme():
    st.markdown("""
        <style>
        .main {
            background-color: #FFF0F5;
        }
        .stButton>button {
            background-color: #EC008B;
            color: white;
            border-radius: 8px;
            border: none;
            font-weight: bold;
        }
        .stButton>button:hover {
            background-color: #C60074;
            color: white;
        }
        .stSelectbox div[data-baseweb="select"] {
            background-color: #FFFFFF;
            border-radius: 8px;
        }
        .metric {
            background-color: #FFFFFF;
            padding: 15px;
            border-radius: 10px;
            box-shadow: 0 4px 6px rgba(236, 0, 139, 0.1);
            margin-bottom: 10px;
            color: #EC008B;
            text-align: center;
            border-left: 4px solid #EC008B;
        }
        .header {
            color: #EC008B;
            font-family: 'Arial', sans-serif;
            border-bottom: 2px solid #EC008B;
            padding-bottom: 5px;
        }
        .stDataFrame {
            border-radius: 10px;
            box-shadow: 0 4px 6px rgba(236, 0, 139, 0.1);
        }
        .half-moon-container {
            background-color: #FFFFFF;
            border-radius: 10px;
            padding: 15px;
            margin-bottom: 15px;
            display: flex;
            flex-direction: column;
            align-items: center;
            height: 100%;
            color: #EC008B;
            box-shadow: 0 4px 6px rgba(236, 0, 139, 0.1);
            border-top: 3px solid #EC008B;
        }
        .half-moon-title {
            text-align: center;
            margin-bottom: 10px;
            font-weight: light;
            color: #000000;
        }
        .vision-general-del-equipo {
            text-align: center;
            margin-bottom: 10px;
            font-weight: bold;
            color: #000000;
        }
        .performance-text {
            text-align: center;
            margin-top: 10px;
            font-size: 14px;
            color: #000000;
            font-weight: light;
        }
        .progress-container {
            width: 100%;
            margin-top: 15px;
        }
        .progress-label {
            display: flex;
            justify-content: space-between;
            margin-top: 5px;
            font-size: 12px;
            color: #000000;
        }
        .half-moon-chart {
            height: 300px !important;
            margin-bottom: 20px;
        }
        .bar-chart-container {
            background-color: #FFFFFF;
            border-radius: 10px;
            padding: 15px;
            margin-bottom: 15px;
            box-shadow: 0 4px 6px rgba(236, 0, 139, 0.1);
            border-top: 3px solid #EC008B;
        }
        h1 {
            color: #EC008B !important;
            text-align: center;
            background: linear-gradient(to right, #FFB6C1, #EC008B);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            padding: 10px;
        }
        h2 {
            color: #EC008B !important;
        }
        h3 {
            color: #1E0805;
        }
        .css-1aumxhk {
            background-color: #FFF0F5;
        }
        </style>
        """, unsafe_allow_html=True)

def cargar_datos():
    # Cargar archivos JSON
    with open("Tickets de atencion a socios (1).json", encoding="utf-8") as f1:
        data1 = json.load(f1)
    with open("Tickets de atencion a socios (2).json", encoding="utf-8") as f2:
        data2 = json.load(f2)

    # Unificar datos
    tickets = []
    for item in data1 + data2:
        ticket = item.get("helpdesk_ticket", {})
        tickets.append({
            "id": ticket.get("id"),
            "created_at": ticket.get("created_at"),
            "updated_at": ticket.get("updated_at"),
            "status": ticket.get("status_name"),
            "priority": ticket.get("priority_name"),
            "responder_name": ticket.get("responder_name"),
            "requester_name": ticket.get("requester_name"),
            "subject": ticket.get("subject"),
            "description": ticket.get("description"),
            "agent_reply_count": ticket.get("reports_data", {}).get("agent_reply_count"),
            "customer_reply_count": ticket.get("reports_data", {}).get("customer_reply_count"),
            "first_response_time": ticket.get("ticket_states", {}).get("first_response_time"),
            "resolved_at": ticket.get("ticket_states", {}).get("resolved_at"),
            "first_assigned_at": ticket.get("ticket_states", {}).get("first_assigned_at"),
            "agent_responded_at": ticket.get("ticket_states", {}).get("agent_responded_at"),
            "requester_responded_at": ticket.get("ticket_states", {}).get("requester_responded_at")
        })

    df = pd.DataFrame(tickets)
    # Convertir a datetime
    df['created_at'] = pd.to_datetime(df['created_at'])
    df['first_response_time'] = pd.to_datetime(df['first_response_time'])

    return df

def asignar_color(valor, umbrales):
    if valor <= umbrales[0]:
        return '🟢'
    elif valor <= umbrales[1]:
        return '🟡'
    else:
        return '🔴'

def crear_grafico_barras_top_agentes(df, columna, titulo, color):
    # Ordenar y tomar los top 5 agentes
    top_agentes = df.sort_values(columna, ascending=False).head(5)

    fig, ax = plt.subplots(figsize=(8, 4))
    bars = ax.barh(top_agentes.index, top_agentes[columna], color=color)

    # Añadir etiquetas con los valores
    for bar in bars:
        width = bar.get_width()
        ax.text(width + 0.1, bar.get_y() + bar.get_height()/2,
                f'{width:.1f}',
                ha='left', va='center', color='#EC008B')

    ax.set_title(titulo, color='#EC008B', pad=20)
    ax.set_xlabel('')
    ax.set_ylabel('')
    ax.tick_params(colors='#EC008B')
    ax.grid(axis='x', linestyle='--', alpha=0.3, color='#EC008B')
    plt.tight_layout()

    return fig

def calcular_metricas_agentes(df):
    # Normalización de datos
    df['status'] = df['status'].str.strip().str.lower()
    df['priority'] = df['priority'].str.strip().str.lower()

    # Conversión de fechas robusta
    df['created_at'] = pd.to_datetime(df['created_at'], errors='coerce')
    df['first_response_time'] = pd.to_datetime(df['first_response_time'], errors='coerce')

    # Filtrado y copia para evitar SettingWithCopyWarning
    df = df[df['responder_name'].notna()].copy()

    # Cálculo de tiempo de respuesta
    df['tiempo_respuesta'] = (df['first_response_time'] - df['created_at']).dt.total_seconds() / 60

    # Métrica 1: Tiempo promedio
    tiempo_promedio = df.groupby('responder_name')['tiempo_respuesta'].mean()

    # Métrica 2: Porcentaje de tickets abiertos/pendientes (con normalización)
    total_tickets = df.groupby('responder_name').size()
    abiertos_y_pendientes = df[df['status'].isin(['open', 'pending'])].groupby('responder_name').size()
    porcentaje_abiertos = (abiertos_y_pendientes / total_tickets * 100).fillna(0)

    # Métrica 3: Casos críticos (urgentes + abiertos)
    criticos = df[(df['status'] == 'open') & ((df['priority'] == 'urgent') | (df['priority'] == 'high'))].groupby('responder_name').size()

    # Unificación de métricas
    metricas = pd.concat([
        tiempo_promedio.rename('Tiempo promedio (min)'),
        porcentaje_abiertos.rename('Tickets abiertos y pendientes (%)'),
        criticos.rename('Casos críticos')
    ], axis=1).fillna(0)

    return metricas

def generar_semaforo(metricas):
    # Asignación de colores con umbrales actualizados
    metricas['color_tiempo'] = metricas['Tiempo promedio (min)'].apply(
        lambda x: '🔴' if x > 5 else ('🟡' if x > 3 else '🟢'))

    metricas['color_abiertos'] = metricas['Tickets abiertos y pendientes (%)'].apply(
        asignar_color, umbrales=(10, 20))

    metricas['color_criticos'] = metricas['Casos críticos'].apply(
        lambda x: '🔴' if x >= 3 else ('🟡' if x >= 1 else '🟢'))

    # Determinación del semáforo final
    color_map = {'🟢': 0, '🟡': 1, '🔴': 2}
    semaforo_final = metricas[['color_tiempo', 'color_abiertos', 'color_criticos']]\
        .replace(color_map).max(axis=1).replace({0: '🟢', 1: '🟡', 2: '🔴'})

    metricas['Semáforo'] = semaforo_final
    return metricas

def analisis_agentes(df):
    metricas = calcular_metricas_agentes(df)
    metricas = generar_semaforo(metricas)
    return metricas

def crear_grafico_media_luna(porcentaje, titulo, tipo_metrica):
    fig, ax = plt.subplots(figsize=(8, 6))  # Más alto

    # Lógica de colores basada en el tipo de métrica
    if tipo_metrica == 'tiempo':
        # Para tiempo, menos es mejor (invertimos la lógica)
        if porcentaje >= 80:  # Menos de 1 minuto (100 - (1/5*100) = 80)
            color = '#4CAF50'  # Verde
            performance = "Excelente"
        elif porcentaje >= 60:  # Menos de 2 minutos (100 - (2/5*100) = 60)
            color = '#FFC107'  # Amarillo
            performance = "Bueno"
        else:
            color = '#F44336'  # Rojo
            performance = "Necesita mejorar"
    else:
        # Para otros casos (tickets y críticos), más es mejor
        if porcentaje >= 80:
            color = '#4CAF50'  # Verde
            performance = "Excelente"
        elif porcentaje >= 60:
            color = '#FFC107'  # Amarillo
            performance = "Bueno"
        else:
            color = '#F44336'  # Rojo
            performance = "Necesita mejorar"

    # Fondo (gris claro)
    wedge_bg = Wedge((0.5, 0.5), 0.45, 0, 180, width=0.25, color='#FFF0F5')
    ax.add_patch(wedge_bg)

    # Porcentaje (color)
    wedge_fill = Wedge((0.5, 0.5), 0.45, 0, porcentaje / 100 * 180, width=0.25, color=color)
    ax.add_patch(wedge_fill)

    # Texto central
    ax.text(0.5, 0.6, f"{porcentaje:.1f}%", ha='center', va='center', fontsize=24, fontweight='bold', color=color)
    ax.text(0.5, 0.35, titulo, ha='center', va='center', fontsize=16, color='#EC008B')

    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis('off')
    plt.tight_layout()

    return fig, performance

def crear_barra_progreso(porcentaje, tipo_metrica):
    # Lógica de colores basada en el tipo de métrica
    if tipo_metrica == 'tiempo':
        # Para tiempo, menos es mejor (invertimos la lógica)
        if porcentaje >= 80:
            color = '#4CAF50'
        elif porcentaje >= 60:
            color = '#FFC107'
        else:
            color = '#F44336'
    else:
        # Para otros casos (tickets y críticos), más es mejor
        if porcentaje >= 80:
            color = '#4CAF50'
        elif porcentaje >= 60:
            color = '#FFC107'
        else:
            color = '#F44336'

    st.markdown(f"""
    <div class="progress-container">
        <div style="width: 100%; height: 10px; background-color: #FFF0F5; border-radius: 5px;">
            <div style="width: {porcentaje}%; height: 10px; background-color: {color}; border-radius: 5px;"></div>
        </div>
        <div class="progress-label">
            <span>0%</span>
            <span>100%</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

# ============ INTERFAZ STREAMLIT MEJORADA ============
set_custom_theme()


# Título con estilo
st.markdown("<h1 style='text-align: center;'>Dashboard de Desempeño de Agentes</h1>", unsafe_allow_html=True)

# Cargar datos
df = cargar_datos()
metricas = analisis_agentes(df)
agentes = metricas.index.tolist()

# ===== NUEVOS GRÁFICOS DE BARRAS =====
st.markdown("---")
col1, col2 = st.columns(2)

with col1:
    st.markdown("<div class='bar-chart-container'>", unsafe_allow_html=True)
    st.markdown("<h3 style='text-align: center;'>Top 5 Agentes - Mejor Tiempo Respuesta</h3>", unsafe_allow_html=True)
    # Para tiempo de respuesta, menor es mejor (ordenamos ascendente)
    fig = crear_grafico_barras_top_agentes(
        metricas.sort_values('Tiempo promedio (min)').head(5),
        'Tiempo promedio (min)',
        '',
        '#EC008B'
    )
    st.pyplot(fig)
    st.markdown("</div>", unsafe_allow_html=True)

with col2:
    st.markdown("<div class='bar-chart-container'>", unsafe_allow_html=True)
    st.markdown("<h3 style='text-align: center;'>Top 5 Agentes - Menos Tickets Pendientes</h3>", unsafe_allow_html=True)
    # Para tickets pendientes, menor es mejor (ordenamos ascendente)
    fig = crear_grafico_barras_top_agentes(
        metricas.sort_values('Tickets abiertos y pendientes (%)').head(5),
        'Tickets abiertos y pendientes (%)',
        '',
        '#FF69B4'
    )
    st.pyplot(fig)
    st.markdown("</div>", unsafe_allow_html=True)

# ===== FIN NUEVOS GRÁFICOS =====

st.subheader("Visión general del equipo")

col1, col2, col3 = st.columns(3)

with col1:
    st.metric("Tiempo promedio general (min)", f"{metricas['Tiempo promedio (min)'].mean():.2f}")
with col2:
    st.metric("% de tickets abiertos o pendientes", f"{metricas['Tickets abiertos y pendientes (%)'].mean():.1f}%")
with col3:
    st.metric("Casos críticos totales", int(metricas['Casos críticos'].sum()))


# Sección de selección de agente
st.markdown("---")
st.markdown("<h1 class='header'> Visualización por Agente</h1>", unsafe_allow_html=True)
agente_seleccionado = st.selectbox("Selecciona un agente para ver sus métricas detalladas:", agentes)

if agente_seleccionado:
    datos = metricas.loc[agente_seleccionado]

    # Tarjetas de métricas mejoradas
    st.markdown("---")
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.markdown(f"""
        <div class='metric'>
            <h3>Tiempo Respuesta</h3>
            <h2>{round(datos['Tiempo promedio (min)'],1)} min</h2>
            <h2>{datos['color_tiempo']}</h2>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown(f"""
        <div class='metric'>
            <h3>Tickets Abiertos</h3>
            <h2>{round(datos['Tickets abiertos y pendientes (%)'],1)}%</h2>
            <h2>{datos['color_abiertos']}</h2>
        </div>
        """, unsafe_allow_html=True)

    with col3:
        st.markdown(f"""
        <div class='metric'>
            <h3>Casos Críticos</h3>
            <h2>{int(datos['Casos críticos'])}</h2>
            <h2>{datos['color_criticos']}</h2>
        </div>
        """, unsafe_allow_html=True)

    with col4:
        st.markdown(f"""
        <div class='metric'>
            <h3>Estado General</h3>
            <h3>{datos['Semáforo']}</h3>
        </div>
        """, unsafe_allow_html=True)

    # Nueva sección de gráficos de media luna
    st.markdown("---")
    st.markdown("<h2 class='header'> Cumplimiento de Objetivos</h2>", unsafe_allow_html=True)

    # Calcular porcentajes para las medias lunas
    # Para tiempo: menos tiempo es mejor (invertimos la lógica)
    cumplimiento_tiempo = max(0, min(100, (1.5 / max(0.1, datos['Tiempo promedio (min)'])) * 100 * 0.8))

    # Para tickets abiertos: menos es mejor (invertimos la lógica)
    cumplimiento_abiertos = max(0, min(100, 100 - datos['Tickets abiertos y pendientes (%)']))

    # Para casos críticos: menos es mejor (invertimos la lógica)
    cumplimiento_criticos = max(0, min(100, 100 - (datos['Casos críticos'] / 3 * 100)))

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown("<div class='half-moon-container'>", unsafe_allow_html=True)
        st.markdown("<div class='half-moon-title'>Eficiencia en Tiempo</div>", unsafe_allow_html=True)
        fig, performance = crear_grafico_media_luna(round(cumplimiento_tiempo, 1), "Tiempo Respuesta", 'tiempo')
        st.pyplot(fig, use_container_width=True)
        st.markdown(f"<div class='performance-text'>{performance}</div>", unsafe_allow_html=True)
        crear_barra_progreso(cumplimiento_tiempo, 'tiempo')
        st.markdown("</div>", unsafe_allow_html=True)

    with col2:
        st.markdown("<div class='half-moon-container'>", unsafe_allow_html=True)
        st.markdown("<div class='half-moon-title'>Resolución de Tickets</div>", unsafe_allow_html=True)
        fig, performance = crear_grafico_media_luna(round(cumplimiento_abiertos, 1), "Tickets Resueltos", 'tickets')
        st.pyplot(fig, use_container_width=True)
        st.markdown(f"<div class='performance-text'>{performance}</div>", unsafe_allow_html=True)
        crear_barra_progreso(cumplimiento_abiertos, 'tickets')
        st.markdown("</div>", unsafe_allow_html=True)

    with col3:
        st.markdown("<div class='half-moon-container'>", unsafe_allow_html=True)
        st.markdown("<div class='half-moon-title'>Manejo de Casos Críticos</div>", unsafe_allow_html=True)
        fig, performance = crear_grafico_media_luna(round(cumplimiento_criticos, 1), "Casos Críticos", 'criticos')
        st.pyplot(fig, use_container_width=True)
        st.markdown(f"<div class='performance-text'>{performance}</div>", unsafe_allow_html=True)
        crear_barra_progreso(cumplimiento_criticos, 'criticos')
        st.markdown("</div>", unsafe_allow_html=True)

# Tabla de todos los agentes
st.markdown("---")
st.markdown("<h2 class='header'> Resumen de Todos los Agentes</h2>", unsafe_allow_html=True)

# Función para aplicar estilo a la tabla
def color_semaforo(val):
    color = '#4CAF50' if val == '🟢' else '#FFC107' if val == '🟡' else '#F44336'
    return f'background-color: {color}; color: white; text-align: center;'

# Función para poner en negrita la primera columna
def highlight_index(s):
    return ['font-weight: bold; color: #000000' if s.name == 'Agente' else '' for _ in s]

# Preparamos los datos
styled_metricas = metricas[['Tiempo promedio (min)', 'Tickets abiertos y pendientes (%)', 'Casos críticos', 'Semáforo']].copy()
styled_metricas.index.name = 'Agente'  # Cambiar nombre del índice
styled_metricas = styled_metricas.rename(columns={
    'Tiempo promedio (min)': 'Tiempo promedio de respuesta (min)',
    'Tickets abiertos y pendientes (%)': 'Tickets pendientes (%)',
    'Semáforo': 'Estado'
})

# Formatear valores
styled_metricas['Tiempo promedio de respuesta (min)'] = styled_metricas['Tiempo promedio de respuesta (min)'].apply(lambda x: f"{x:.1f}")
styled_metricas['Tickets pendientes (%)'] = styled_metricas['Tickets pendientes (%)'].apply(lambda x: f"{x:.1f}%")
styled_metricas['Casos críticos'] = styled_metricas['Casos críticos'].astype(int)

# Resetear el índice para que 'Agente' sea una columna regular
styled_metricas = styled_metricas.reset_index()

# Mostrar la tabla con estilos
st.dataframe(
    styled_metricas.style
        .applymap(color_semaforo, subset=['Estado'])
        .apply(highlight_index, subset=['Agente']),
    height=(len(metricas) + 1) * 35 + 3,
    width=1000
)