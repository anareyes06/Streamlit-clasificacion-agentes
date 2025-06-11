# utils.py
import pandas as pd
import json
import matplotlib.pyplot as plt
import seaborn as sns
import altair as alt

def cargar_datos(lista_archivos):
    tickets = []
    for archivo in lista_archivos:
        data = json.load(archivo)
        for item in data:
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
    return pd.DataFrame(tickets)

def procesar_datos(df):
    df = df.copy()
    df['created_at'] = pd.to_datetime(df['created_at'])
    df['first_response_time'] = pd.to_datetime(df['first_response_time'])
    df['response_time_difference'] = df['first_response_time'] - df['created_at']
    return df

def calcular_tiempos(df):
    prom = df.groupby('responder_name')['response_time_difference'].mean().dropna()
    prom_min = prom.dt.total_seconds() / 60
    return prom_min.reset_index(name='Promedio (min)')

def resumen_por_estado(df):
    df_summary = df.groupby(['responder_name', 'status']).size().unstack(fill_value=0)
    df_summary = df_summary.rename(columns={
        'Open': 'Abiertos',
        'Closed': 'Cerrados',
        'Pending': 'Pendientes',
        'Resolved': 'Resueltos',
        'Escalado': 'Escalado'
    })
    columnas = [c for c in ['Abiertos', 'Cerrados', 'Pendientes', 'Resueltos', 'Escalado'] if c in df_summary.columns]
    return df_summary[columnas].reset_index()

def graficar_tiempos(promedios):
    fig, ax = plt.subplots(figsize=(10, 5))
    sns.barplot(data=promedios, x='responder_name', y='Promedio (min)', palette='viridis', ax=ax)
    ax.set_title('Tiempo de Respuesta Promedio por Agente')
    ax.set_xlabel('Agente')
    ax.set_ylabel('Minutos')
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
    return fig

def graficar_estado_altair(df_summary):
    df_melted = df_summary.melt(id_vars=['responder_name'], var_name='Estado', value_name='Cantidad')
    chart = alt.Chart(df_melted).mark_bar().encode(
        x='Estado:N',
        y='Cantidad:Q',
        color='responder_name:N',
        column='responder_name:N'
    ).properties(title='Cantidad de Tickets por Estado y por Agente')
    return chart