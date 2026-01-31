"""
SaaS Financial Intelligence Dashboard
Dashboard interactivo para análisis de transacciones financieras.

Author: Senior BI Developer
Date: 2026-01-31
"""

import os
from datetime import datetime, timedelta

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from dotenv import load_dotenv
from sqlalchemy import create_engine

# Configuración de la página
st.set_page_config(
    page_title="Financial Intelligence Dashboard",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Cargar variables de entorno
load_dotenv()

# CSS personalizado para mejorar la estética
st.markdown("""
    <style>
    .main {
        padding: 0rem 1rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 20px;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    h1 {
        color: #1f77b4;
        font-weight: 700;
    }
    .stMetric {
        background-color: #ffffff;
        padding: 15px;
        border-radius: 8px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
    }
    </style>
    """, unsafe_allow_html=True)


@st.cache_resource
def init_connection():
    """
    Inicializa la conexión a PostgreSQL.
    Usa st.cache_resource para mantener la conexión activa.
    """
    database_url = os.getenv('DATABASE_URL')
    
    if not database_url:
        st.error("❌ DATABASE_URL no configurado en el archivo .env")
        st.stop()
    
    try:
        engine = create_engine(database_url, pool_pre_ping=True)
        return engine
    except Exception as e:
        st.error(f"❌ Error al conectar a la base de datos: {e}")
        st.stop()


@st.cache_data(ttl=300)  # Cache por 5 minutos
def load_data():
    """
    Carga los datos de la tabla transactions desde PostgreSQL.
    Usa st.cache_data para evitar consultas repetidas.
    """
    engine = init_connection()
    
    query = """
    SELECT 
        id,
        timestamp,
        amount,
        currency,
        status,
        client_email,
        client_ip,
        client_device,
        metadata
    FROM transactions
    ORDER BY timestamp DESC
    """
    
    try:
        df = pd.read_sql(query, engine)
        
        # Convertir timestamp a datetime si no lo es
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        
        # Agregar columnas derivadas útiles para análisis
        df['date'] = df['timestamp'].dt.date
        df['year_month'] = df['timestamp'].dt.to_period('M').astype(str)
        df['day_of_week'] = df['timestamp'].dt.day_name()
        df['hour'] = df['timestamp'].dt.hour
        
        return df
    
    except Exception as e:
        st.error(f"❌ Error al cargar datos: {e}")
        st.stop()


def format_currency(value, currency='USD'):
    """Formatea un valor como moneda."""
    if currency == 'COP':
        return f"${value:,.0f} COP"
    elif currency == 'EUR':
        return f"€{value:,.2f}"
    elif currency == 'GBP':
        return f"£{value:,.2f}"
    else:  # USD por defecto
        return f"${value:,.2f}"


def format_large_number(value):
    """Formatea números grandes con sufijos (K, M, B)."""
    if value >= 1_000_000_000:
        return f"${value/1_000_000_000:.2f}B"
    elif value >= 1_000_000:
        return f"${value/1_000_000:.2f}M"
    elif value >= 1_000:
        return f"${value/1_000:.2f}K"
    else:
        return f"${value:.2f}"


def create_kpi_cards(df):
    """Crea las tarjetas de KPIs principales."""
    col1, col2, col3 = st.columns(3)
    
    total_transactions = len(df)
    total_volume = df['amount'].sum()
    avg_ticket = df['amount'].mean()
    
    with col1:
        st.metric(
            label="📊 Total Transacciones",
            value=f"{total_transactions:,}",
            help="Número total de transacciones en el período seleccionado"
        )
    
    with col2:
        st.metric(
            label="💰 Volumen Total",
            value=format_large_number(total_volume),
            help="Suma total de todas las transacciones"
        )
    
    with col3:
        st.metric(
            label="🎯 Ticket Promedio",
            value=format_large_number(avg_ticket),
            help="Valor promedio por transacción"
        )


def create_volume_by_currency_chart(df):
    """Crea gráfico de barras: Volumen por moneda."""
    # Agrupar por moneda
    currency_volume = df.groupby('currency').agg({
        'amount': 'sum',
        'id': 'count'
    }).reset_index()
    currency_volume.columns = ['currency', 'volume', 'count']
    currency_volume = currency_volume.sort_values('volume', ascending=False)
    
    # Crear gráfico
    fig = px.bar(
        currency_volume,
        x='currency',
        y='volume',
        title='💵 Volumen de Ventas por Moneda',
        labels={'currency': 'Moneda', 'volume': 'Volumen Total'},
        color='currency',
        color_discrete_map={
            'USD': '#1f77b4',
            'EUR': '#ff7f0e',
            'GBP': '#2ca02c',
            'COP': '#d62728'
        },
        text='volume'
    )
    
    fig.update_traces(
        texttemplate='$%{text:,.0f}',
        textposition='outside'
    )
    
    fig.update_layout(
        showlegend=False,
        height=400,
        hovermode='x unified',
        xaxis_title="Moneda",
        yaxis_title="Volumen Total ($)"
    )
    
    return fig


def create_trend_chart(df):
    """Crea gráfico de línea: Tendencia de transacciones en el tiempo."""
    # Agrupar por fecha
    daily_trend = df.groupby('date').agg({
        'amount': 'sum',
        'id': 'count'
    }).reset_index()
    daily_trend.columns = ['date', 'volume', 'count']
    
    # Crear gráfico con dos ejes Y
    fig = go.Figure()
    
    # Línea de volumen
    fig.add_trace(go.Scatter(
        x=daily_trend['date'],
        y=daily_trend['volume'],
        name='Volumen ($)',
        mode='lines+markers',
        line=dict(color='#1f77b4', width=3),
        marker=dict(size=6),
        yaxis='y'
    ))
    
    # Línea de conteo de transacciones
    fig.add_trace(go.Scatter(
        x=daily_trend['date'],
        y=daily_trend['count'],
        name='# Transacciones',
        mode='lines+markers',
        line=dict(color='#ff7f0e', width=2, dash='dash'),
        marker=dict(size=4),
        yaxis='y2'
    ))
    
    fig.update_layout(
        title='📈 Tendencia de Transacciones en el Tiempo',
        xaxis_title='Fecha',
        yaxis=dict(
            title='Volumen ($)',
            titlefont=dict(color='#1f77b4'),
            tickfont=dict(color='#1f77b4')
        ),
        yaxis2=dict(
            title='Número de Transacciones',
            titlefont=dict(color='#ff7f0e'),
            tickfont=dict(color='#ff7f0e'),
            overlaying='y',
            side='right'
        ),
        height=400,
        hovermode='x unified',
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        )
    )
    
    return fig


def create_status_distribution_chart(df):
    """Crea gráfico donut: Distribución de Status."""
    # Agrupar por status
    status_dist = df.groupby('status').size().reset_index(name='count')
    
    # Colores personalizados por status
    color_map = {
        'COMPLETED': '#2ca02c',
        'FAILED': '#d62728',
        'PENDING': '#ff7f0e',
        'REFUNDED': '#9467bd'
    }
    
    colors = [color_map.get(status, '#7f7f7f') for status in status_dist['status']]
    
    # Crear gráfico donut
    fig = go.Figure(data=[go.Pie(
        labels=status_dist['status'],
        values=status_dist['count'],
        hole=0.4,
        marker=dict(colors=colors),
        textinfo='label+percent',
        textposition='outside',
        hovertemplate='<b>%{label}</b><br>Transacciones: %{value:,}<br>Porcentaje: %{percent}<extra></extra>'
    )])
    
    fig.update_layout(
        title='📊 Distribución de Status de Transacciones',
        height=400,
        showlegend=True,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=-0.15,
            xanchor="center",
            x=0.5
        )
    )
    
    return fig


def create_device_distribution_chart(df):
    """Crea gráfico de barras horizontales: Distribución por dispositivo."""
    device_dist = df.groupby('client_device').agg({
        'amount': 'sum',
        'id': 'count'
    }).reset_index()
    device_dist.columns = ['device', 'volume', 'count']
    
    fig = px.bar(
        device_dist,
        x='count',
        y='device',
        title='📱 Transacciones por Dispositivo',
        labels={'count': 'Número de Transacciones', 'device': 'Dispositivo'},
        orientation='h',
        color='device',
        color_discrete_map={'mobile': '#ff7f0e', 'desktop': '#1f77b4'},
        text='count'
    )
    
    fig.update_traces(texttemplate='%{text:,}', textposition='outside')
    fig.update_layout(showlegend=False, height=300)
    
    return fig


def main():
    """Función principal del dashboard."""
    
    # Header
    st.title("💰 SaaS Financial Intelligence Dashboard")
    st.markdown("---")
    
    # Cargar datos
    with st.spinner("Cargando datos desde PostgreSQL..."):
        df = load_data()
    
    # Sidebar - Filtros
    st.sidebar.title("🔍 Filtros")
    st.sidebar.markdown("Personaliza tu vista seleccionando filtros:")
    
    # Filtro de Moneda
    all_currencies = sorted(df['currency'].unique().tolist())
    selected_currencies = st.sidebar.multiselect(
        "💵 Selecciona Monedas",
        options=all_currencies,
        default=all_currencies,
        help="Filtra transacciones por tipo de moneda"
    )
    
    # Filtro de Status
    all_statuses = sorted(df['status'].unique().tolist())
    selected_statuses = st.sidebar.multiselect(
        "📊 Selecciona Status",
        options=all_statuses,
        default=all_statuses,
        help="Filtra transacciones por estado"
    )
    
    # Filtro de Rango de Fechas
    st.sidebar.markdown("---")
    date_range = st.sidebar.date_input(
        "📅 Rango de Fechas",
        value=(df['timestamp'].min().date(), df['timestamp'].max().date()),
        min_value=df['timestamp'].min().date(),
        max_value=df['timestamp'].max().date(),
        help="Selecciona el rango de fechas para análisis"
    )
    
    # Aplicar filtros
    df_filtered = df.copy()
    
    if selected_currencies:
        df_filtered = df_filtered[df_filtered['currency'].isin(selected_currencies)]
    
    if selected_statuses:
        df_filtered = df_filtered[df_filtered['status'].isin(selected_statuses)]
    
    if len(date_range) == 2:
        start_date, end_date = date_range
        df_filtered = df_filtered[
            (df_filtered['timestamp'].dt.date >= start_date) &
            (df_filtered['timestamp'].dt.date <= end_date)
        ]
    
    # Mostrar información de filtros aplicados
    st.sidebar.markdown("---")
    st.sidebar.success(f"✅ {len(df_filtered):,} transacciones seleccionadas")
    st.sidebar.info(f"📊 De un total de {len(df):,} transacciones")
    
    # Verificar si hay datos después de filtrar
    if len(df_filtered) == 0:
        st.warning("⚠️ No hay datos que cumplan con los filtros seleccionados. Por favor, ajusta los filtros.")
        return
    
    # KPIs principales
    st.subheader("📊 Métricas Principales")
    create_kpi_cards(df_filtered)
    
    st.markdown("---")
    
    # Gráficos - Primera fila
    st.subheader("📈 Análisis Visual")
    col1, col2 = st.columns(2)
    
    with col1:
        st.plotly_chart(
            create_volume_by_currency_chart(df_filtered),
            use_container_width=True
        )
    
    with col2:
        st.plotly_chart(
            create_status_distribution_chart(df_filtered),
            use_container_width=True
        )
    
    # Gráficos - Segunda fila
    st.plotly_chart(
        create_trend_chart(df_filtered),
        use_container_width=True
    )
    
    # Gráfico adicional - Dispositivos
    st.plotly_chart(
        create_device_distribution_chart(df_filtered),
        use_container_width=True
    )
    
    st.markdown("---")
    
    # Estadísticas adicionales
    st.subheader("📊 Estadísticas Detalladas")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            "💵 Transacción Máxima",
            format_large_number(df_filtered['amount'].max())
        )
    
    with col2:
        st.metric(
            "💵 Transacción Mínima",
            format_large_number(df_filtered['amount'].min())
        )
    
    with col3:
        completed = len(df_filtered[df_filtered['status'] == 'COMPLETED'])
        success_rate = (completed / len(df_filtered) * 100) if len(df_filtered) > 0 else 0
        st.metric(
            "✅ Tasa de Éxito",
            f"{success_rate:.1f}%"
        )
    
    with col4:
        unique_clients = df_filtered['client_email'].nunique()
        st.metric(
            "👥 Clientes Únicos",
            f"{unique_clients:,}"
        )
    
    st.markdown("---")
    
    # Tabla de datos
    st.subheader("📋 Últimas 100 Transacciones")
    
    # Preparar datos para mostrar
    display_df = df_filtered.head(100).copy()
    display_df['timestamp'] = display_df['timestamp'].dt.strftime('%Y-%m-%d %H:%M:%S')
    display_df['amount'] = display_df['amount'].apply(lambda x: f"${x:,.2f}")
    
    # Seleccionar columnas relevantes
    columns_to_display = ['timestamp', 'amount', 'currency', 'status', 'client_email', 'client_device']
    display_df = display_df[columns_to_display]
    
    # Renombrar columnas para mejor presentación
    display_df.columns = ['Fecha/Hora', 'Monto', 'Moneda', 'Status', 'Cliente', 'Dispositivo']
    
    # Mostrar tabla
    st.dataframe(
        display_df,
        use_container_width=True,
        height=400
    )
    
    # Footer con estadísticas
    st.markdown("---")
    st.markdown(f"""
    <div style='text-align: center; color: #666; padding: 20px;'>
        <p><b>Dashboard actualizado:</b> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
        <p>Datos cargados desde PostgreSQL en Railway | Total de registros en BD: {len(df):,}</p>
    </div>
    """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()
