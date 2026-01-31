"""
SaaS Financial Intelligence Dashboard v2.0
Dashboard profesional con normalización de monedas y UI/UX mejorada.

Features:
- Normalización de monedas a USD para comparaciones justas
- KPIs con deltas temporales
- Estructura con tabs para mejor navegación
- Tabla avanzada con column_config
- Colores consistentes en todas las visualizaciones

Author: Lead BI Developer
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

# ==================== CONFIGURACIÓN ====================

# Configuración de la página
st.set_page_config(
    page_title="Financial Intelligence Dashboard",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Cargar variables de entorno
load_dotenv()

# ==================== CONSTANTES ====================

# Tasas de cambio fijas (base: USD = 1.0)
EXCHANGE_RATES = {
    'USD': 1.0,
    'EUR': 1.08,      # 1 EUR = 1.08 USD
    'GBP': 1.27,      # 1 GBP = 1.27 USD
    'COP': 0.00025    # 1 COP = 0.00025 USD
}

# Mapa de colores consistente para Status
STATUS_COLORS = {
    'COMPLETED': '#2ecc71',  # Verde
    'FAILED': '#e74c3c',     # Rojo
    'PENDING': '#f39c12',    # Naranja
    'REFUNDED': '#9b59b6'    # Morado
}

# Mapa de colores para Monedas
CURRENCY_COLORS = {
    'USD': '#1f77b4',  # Azul
    'EUR': '#ff7f0e',  # Naranja
    'GBP': '#2ca02c',  # Verde
    'COP': '#d62728'   # Rojo
}

# ==================== CSS PERSONALIZADO ====================

st.markdown("""
    <style>
    /* General */
    .main {
        padding: 0rem 1rem;
    }
    
    /* Headers */
    h1 {
        color: #1e3a8a;
        font-weight: 700;
        margin-bottom: 0.5rem;
    }
    
    h2 {
        color: #334155;
        font-weight: 600;
        font-size: 1.5rem;
    }
    
    h3 {
        color: #475569;
        font-weight: 600;
    }
    
    /* Metrics */
    [data-testid="stMetricValue"] {
        font-size: 2rem;
        font-weight: 700;
    }
    
    [data-testid="stMetricDelta"] {
        font-size: 1rem;
    }
    
    /* Cards */
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 20px;
        border-radius: 12px;
        color: white;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    
    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }
    
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        padding: 0px 24px;
        border-radius: 8px 8px 0px 0px;
        font-weight: 600;
    }
    
    /* Sidebar */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #f8fafc 0%, #e2e8f0 100%);
    }
    
    /* Dataframe */
    .dataframe {
        font-size: 0.9rem;
    }
    </style>
    """, unsafe_allow_html=True)

# ==================== FUNCIONES DE CONEXIÓN ====================

@st.cache_resource
def init_connection():
    """
    Inicializa la conexión a PostgreSQL.
    Cache persistente durante toda la sesión.
    """
    database_url = os.getenv('DATABASE_URL')
    
    if not database_url:
        st.error("❌ DATABASE_URL no configurado en el archivo .env")
        st.stop()
    
    try:
        engine = create_engine(
            database_url,
            pool_pre_ping=True,
            pool_size=10,
            max_overflow=20
        )
        return engine
    except Exception as e:
        st.error(f"❌ Error al conectar a la base de datos: {e}")
        st.stop()


@st.cache_data(ttl=300)
def load_data():
    """
    Carga datos desde PostgreSQL con transformaciones.
    Cache de 5 minutos para mejor rendimiento.
    
    Returns:
        DataFrame con columnas adicionales:
        - amount_usd: Monto normalizado a USD
        - date: Fecha sin hora
        - year_month: Año-mes para agrupaciones
        - week: Año-semana
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
        
        # Convertir timestamp
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        
        # Normalizar montos a USD (CRÍTICO para KPIs globales)
        df['amount_usd'] = df.apply(
            lambda row: row['amount'] * EXCHANGE_RATES.get(row['currency'], 1.0),
            axis=1
        )
        
        # Columnas derivadas para análisis temporal
        df['date'] = df['timestamp'].dt.date
        df['year_month'] = df['timestamp'].dt.to_period('M').astype(str)
        df['week'] = df['timestamp'].dt.to_period('W').astype(str)
        df['day_of_week'] = df['timestamp'].dt.day_name()
        df['hour'] = df['timestamp'].dt.hour
        
        return df
    
    except Exception as e:
        st.error(f"❌ Error al cargar datos: {e}")
        st.stop()

# ==================== FUNCIONES DE CÁLCULO ====================

def calculate_period_comparison(df, period='month'):
    """
    Calcula métricas comparativas entre períodos.
    
    Args:
        df: DataFrame con datos
        period: 'month' o 'week'
    
    Returns:
        dict con current_value, previous_value, delta_pct
    """
    if len(df) == 0:
        return {'current': 0, 'previous': 0, 'delta': 0}
    
    # Determinar columna de agrupación
    period_col = 'year_month' if period == 'month' else 'week'
    
    # Agrupar por período
    period_data = df.groupby(period_col)['amount_usd'].sum().sort_index()
    
    if len(period_data) < 2:
        return {'current': period_data.iloc[-1] if len(period_data) > 0 else 0, 
                'previous': 0, 
                'delta': 0}
    
    current = period_data.iloc[-1]
    previous = period_data.iloc[-2]
    delta = ((current - previous) / previous * 100) if previous != 0 else 0
    
    return {
        'current': current,
        'previous': previous,
        'delta': delta
    }


def format_currency_usd(value):
    """Formatea valores en USD con sufijos K/M/B."""
    if value >= 1_000_000_000:
        return f"${value/1_000_000_000:.2f}B"
    elif value >= 1_000_000:
        return f"${value/1_000_000:.2f}M"
    elif value >= 1_000:
        return f"${value/1_000:.1f}K"
    else:
        return f"${value:.2f}"

# ==================== COMPONENTES DE VISUALIZACIÓN ====================

def render_kpis_with_deltas(df):
    """
    Renderiza KPIs principales con deltas comparativos.
    Todos los montos usan amount_usd (normalizado).
    """
    st.subheader("📊 Métricas Principales (Todas en USD)")
    
    # Validar que hay datos
    if len(df) == 0:
        st.warning("⚠️ No hay datos para mostrar métricas")
        return
    
    col1, col2, col3, col4 = st.columns(4)
    
    # KPI 1: Total Transacciones
    total_transactions = len(df)
    # Calcular delta de transacciones
    try:
        current_month_txns = len(df[df['year_month'] == df['year_month'].max()])
        months = df['year_month'].unique()
        if len(months) > 1:
            prev_month = sorted(months)[-2]
            prev_month_txns = len(df[df['year_month'] == prev_month])
            txn_delta = ((current_month_txns - prev_month_txns) / prev_month_txns * 100) if prev_month_txns > 0 else 0
        else:
            txn_delta = 0
    except:
        txn_delta = 0
    
    with col1:
        st.metric(
            label="📊 Total Transacciones",
            value=f"{total_transactions:,}",
            delta=f"{txn_delta:+.1f}% vs mes anterior",
            help="Total de transacciones en el período seleccionado"
        )
    
    # KPI 2: Volumen Total (USD normalizado)
    total_volume_usd = df['amount_usd'].sum()
    try:
        volume_comparison = calculate_period_comparison(df, 'month')
    except:
        volume_comparison = {'current': total_volume_usd, 'previous': 0, 'delta': 0}
    
    with col2:
        st.metric(
            label="💰 Volumen Total (USD)",
            value=format_currency_usd(total_volume_usd),
            delta=f"{volume_comparison['delta']:+.1f}% vs mes anterior",
            help="Suma de todas las transacciones normalizadas a USD"
        )
    
    # KPI 3: Ticket Promedio (USD)
    avg_ticket_usd = df['amount_usd'].mean()
    
    # Calcular delta de ticket promedio comparando meses
    try:
        current_month = df['year_month'].max()
        current_month_avg = df[df['year_month'] == current_month]['amount_usd'].mean()
        months = sorted(df['year_month'].unique())
        if len(months) > 1:
            prev_month = months[-2]
            prev_month_avg = df[df['year_month'] == prev_month]['amount_usd'].mean()
            avg_delta = ((current_month_avg - prev_month_avg) / prev_month_avg * 100) if prev_month_avg > 0 else 0
        else:
            avg_delta = 0
    except:
        avg_delta = 0
    
    with col3:
        st.metric(
            label="🎯 Ticket Promedio (USD)",
            value=format_currency_usd(avg_ticket_usd),
            delta=f"{avg_delta:+.1f}% vs mes anterior",
            help="Promedio por transacción en USD"
        )
    
    # KPI 4: Tasa de Éxito
    completed = len(df[df['status'] == 'COMPLETED'])
    success_rate = (completed / len(df) * 100) if len(df) > 0 else 0
    
    with col4:
        st.metric(
            label="✅ Tasa de Éxito",
            value=f"{success_rate:.1f}%",
            delta=f"{completed:,} completadas",
            help="Porcentaje de transacciones exitosas"
        )


def create_trend_chart(df):
    """
    Gráfico de tendencia temporal (Volumen en USD).
    """
    # Agrupar por fecha
    daily_trend = df.groupby('date').agg({
        'amount_usd': 'sum',
        'id': 'count'
    }).reset_index()
    daily_trend.columns = ['date', 'volume_usd', 'count']
    
    # Crear gráfico con dos ejes
    fig = go.Figure()
    
    # Volumen en USD
    fig.add_trace(go.Scatter(
        x=daily_trend['date'],
        y=daily_trend['volume_usd'],
        name='Volumen (USD)',
        mode='lines+markers',
        line=dict(color='#3b82f6', width=3),
        marker=dict(size=6),
        fill='tozeroy',
        fillcolor='rgba(59, 130, 246, 0.1)',
        yaxis='y',
        hovertemplate='<b>%{x}</b><br>Volumen: $%{y:,.2f}<extra></extra>'
    ))
    
    # Número de transacciones
    fig.add_trace(go.Scatter(
        x=daily_trend['date'],
        y=daily_trend['count'],
        name='# Transacciones',
        mode='lines+markers',
        line=dict(color='#f59e0b', width=2, dash='dash'),
        marker=dict(size=4),
        yaxis='y2',
        hovertemplate='<b>%{x}</b><br>Transacciones: %{y:,}<extra></extra>'
    ))
    
    fig.update_layout(
        title='📈 Tendencia Temporal de Transacciones',
        xaxis_title='Fecha',
        yaxis=dict(
            title='Volumen (USD)',
            titlefont=dict(color='#3b82f6'),
            tickfont=dict(color='#3b82f6'),
            tickformat='$,.0f'
        ),
        yaxis2=dict(
            title='Número de Transacciones',
            titlefont=dict(color='#f59e0b'),
            tickfont=dict(color='#f59e0b'),
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
        ),
        template='plotly_white'
    )
    
    return fig


def create_status_donut_chart(df):
    """
    Gráfico donut de distribución de Status con colores consistentes.
    """
    status_dist = df.groupby('status').size().reset_index(name='count')
    
    colors = [STATUS_COLORS.get(status, '#94a3b8') for status in status_dist['status']]
    
    fig = go.Figure(data=[go.Pie(
        labels=status_dist['status'],
        values=status_dist['count'],
        hole=0.5,
        marker=dict(colors=colors, line=dict(color='#ffffff', width=2)),
        textinfo='label+percent',
        textposition='outside',
        textfont=dict(size=12, color='#1e293b'),
        hovertemplate='<b>%{label}</b><br>Transacciones: %{value:,}<br>Porcentaje: %{percent}<extra></extra>'
    )])
    
    fig.update_layout(
        title='📊 Distribución de Status de Transacciones',
        height=400,
        showlegend=True,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=-0.2,
            xanchor="center",
            x=0.5
        ),
        template='plotly_white'
    )
    
    return fig


def create_currency_volume_chart(df):
    """
    Gráfico de barras: Volumen POR MONEDA (en moneda original).
    Especifica claramente que NO está normalizado.
    """
    currency_volume = df.groupby('currency').agg({
        'amount': 'sum',  # Monto en moneda original
        'id': 'count'
    }).reset_index()
    currency_volume.columns = ['currency', 'volume', 'count']
    currency_volume = currency_volume.sort_values('count', ascending=False)
    
    colors = [CURRENCY_COLORS.get(curr, '#94a3b8') for curr in currency_volume['currency']]
    
    fig = px.bar(
        currency_volume,
        x='currency',
        y='volume',
        title='💵 Volumen por Moneda (En moneda original)',
        labels={'currency': 'Moneda', 'volume': 'Volumen Total'},
        color='currency',
        color_discrete_map=CURRENCY_COLORS,
        text='volume'
    )
    
    fig.update_traces(
        texttemplate='%{text:,.0f}',
        textposition='outside',
        hovertemplate='<b>%{x}</b><br>Volumen: %{y:,.2f}<br>Transacciones: ' + 
                      currency_volume['count'].astype(str) + '<extra></extra>'
    )
    
    fig.update_layout(
        showlegend=False,
        height=400,
        template='plotly_white',
        yaxis_title="Volumen (Moneda Original)"
    )
    
    return fig


def create_device_chart(df):
    """
    Gráfico de barras: Volumen por dispositivo (normalizado a USD).
    """
    device_data = df.groupby('client_device').agg({
        'amount_usd': 'sum',
        'id': 'count'
    }).reset_index()
    device_data.columns = ['device', 'volume_usd', 'count']
    
    fig = px.bar(
        device_data,
        x='device',
        y='volume_usd',
        title='📱 Volumen por Dispositivo (USD)',
        labels={'device': 'Dispositivo', 'volume_usd': 'Volumen (USD)'},
        color='device',
        color_discrete_map={'mobile': '#f59e0b', 'desktop': '#3b82f6'},
        text='volume_usd'
    )
    
    fig.update_traces(
        texttemplate='$%{text:,.0f}',
        textposition='outside'
    )
    
    fig.update_layout(
        showlegend=False,
        height=350,
        template='plotly_white'
    )
    
    return fig


def create_heatmap_by_day_hour(df):
    """
    Heatmap de transacciones por día de semana y hora.
    """
    # Crear pivot table
    heatmap_data = df.groupby(['day_of_week', 'hour']).size().reset_index(name='count')
    heatmap_pivot = heatmap_data.pivot(index='day_of_week', columns='hour', values='count').fillna(0)
    
    # Ordenar días de la semana
    days_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    heatmap_pivot = heatmap_pivot.reindex([day for day in days_order if day in heatmap_pivot.index])
    
    fig = go.Figure(data=go.Heatmap(
        z=heatmap_pivot.values,
        x=heatmap_pivot.columns,
        y=heatmap_pivot.index,
        colorscale='Blues',
        text=heatmap_pivot.values,
        texttemplate='%{text:.0f}',
        textfont={"size": 10},
        hovertemplate='<b>%{y}</b><br>Hora: %{x}:00<br>Transacciones: %{z:.0f}<extra></extra>'
    ))
    
    fig.update_layout(
        title='🔥 Heatmap: Transacciones por Día y Hora',
        xaxis_title='Hora del Día',
        yaxis_title='Día de la Semana',
        height=350,
        template='plotly_white'
    )
    
    return fig


def render_advanced_table(df):
    """
    Tabla avanzada con column_config para mejor UX.
    """
    # Preparar datos para mostrar
    display_df = df.head(100).copy()
    
    # Configuración de columnas
    column_config = {
        "timestamp": st.column_config.DatetimeColumn(
            "Fecha/Hora",
            format="DD/MM/YYYY HH:mm",
            width="medium"
        ),
        "amount": st.column_config.NumberColumn(
            "Monto Original",
            format="%.2f",
            width="small"
        ),
        "amount_usd": st.column_config.NumberColumn(
            "Monto (USD)",
            format="$%.2f",
            width="medium",
            help="Monto normalizado a USD usando tasas fijas"
        ),
        "currency": st.column_config.TextColumn(
            "💱 Moneda",
            width="small"
        ),
        "status": st.column_config.TextColumn(
            "📊 Status",
            width="medium"
        ),
        "client_email": st.column_config.TextColumn(
            "📧 Cliente",
            width="large"
        ),
        "client_device": st.column_config.TextColumn(
            "📱 Dispositivo",
            width="small"
        )
    }
    
    # Seleccionar columnas a mostrar
    columns_to_show = [
        'timestamp', 'amount', 'currency', 'amount_usd', 
        'status', 'client_email', 'client_device'
    ]
    
    # Aplicar estilo condicional a Status
    def highlight_status(row):
        color = STATUS_COLORS.get(row['status'], '#94a3b8')
        return [f'background-color: {color}20' if col == 'status' else '' for col in row.index]
    
    st.dataframe(
        display_df[columns_to_show],
        column_config=column_config,
        use_container_width=True,
        height=500,
        hide_index=True
    )

# ==================== APLICACIÓN PRINCIPAL ====================

def main():
    """Función principal del dashboard."""
    
    # Header
    st.title("💰 SaaS Financial Intelligence Dashboard")
    st.markdown("**Dashboard profesional con normalización de monedas a USD**")
    st.markdown("---")
    
    # Cargar datos
    with st.spinner("📊 Cargando datos desde PostgreSQL..."):
        df = load_data()
    
    # ==================== SIDEBAR - FILTROS ====================
    
    st.sidebar.title("🔍 Filtros y Configuración")
    st.sidebar.markdown("---")
    
    # Filtro de Moneda
    all_currencies = sorted(df['currency'].unique().tolist())
    selected_currencies = st.sidebar.multiselect(
        "💵 Monedas",
        options=all_currencies,
        default=all_currencies,
        help="Filtra transacciones por tipo de moneda"
    )
    
    # Filtro de Status
    all_statuses = sorted(df['status'].unique().tolist())
    selected_statuses = st.sidebar.multiselect(
        "📊 Status",
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
        max_value=df['timestamp'].max().date()
    )
    
    # Información de tasas de cambio
    st.sidebar.markdown("---")
    st.sidebar.info("**💱 Tasas de Cambio Fijas**\n\n" + 
                   "\n".join([f"• {curr}: {rate}" for curr, rate in EXCHANGE_RATES.items()]))
    
    # ==================== APLICAR FILTROS ====================
    
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
    
    # Mostrar información de filtros
    st.sidebar.markdown("---")
    st.sidebar.success(f"✅ {len(df_filtered):,} transacciones")
    st.sidebar.caption(f"Total en base: {len(df):,}")
    
    # Verificar datos
    if len(df_filtered) == 0:
        st.warning("⚠️ No hay datos que cumplan con los filtros seleccionados.")
        return
    
    # ==================== TABS DE NAVEGACIÓN ====================
    
    tab1, tab2, tab3 = st.tabs([
        "📈 Resumen Ejecutivo",
        "🌍 Análisis Detallado",
        "📋 Datos Crudos"
    ])
    
    # ==================== TAB 1: RESUMEN EJECUTIVO ====================
    
    with tab1:
        # KPIs con deltas
        render_kpis_with_deltas(df_filtered)
        
        st.markdown("---")
        
        # Gráficos principales en 2 columnas
        col1, col2 = st.columns(2)
        
        with col1:
            st.plotly_chart(
                create_trend_chart(df_filtered),
                use_container_width=True,
                key="trend_executive"
            )
        
        with col2:
            st.plotly_chart(
                create_status_donut_chart(df_filtered),
                use_container_width=True,
                key="donut_executive"
            )
        
        # Estadísticas adicionales
        st.markdown("---")
        st.subheader("📊 Estadísticas Adicionales")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(
                "💎 Transacción Máxima (USD)",
                format_currency_usd(df_filtered['amount_usd'].max())
            )
        
        with col2:
            st.metric(
                "💵 Transacción Mínima (USD)",
                format_currency_usd(df_filtered['amount_usd'].min())
            )
        
        with col3:
            unique_clients = df_filtered['client_email'].nunique()
            st.metric(
                "👥 Clientes Únicos",
                f"{unique_clients:,}"
            )
        
        with col4:
            mobile_pct = (len(df_filtered[df_filtered['client_device'] == 'mobile']) / len(df_filtered) * 100)
            st.metric(
                "📱 % Mobile",
                f"{mobile_pct:.1f}%"
            )
    
    # ==================== TAB 2: ANÁLISIS DETALLADO ====================
    
    with tab2:
        st.subheader("🌍 Análisis por Segmentos")
        
        # Fila 1: Monedas y Dispositivos
        col1, col2 = st.columns(2)
        
        with col1:
            st.plotly_chart(
                create_currency_volume_chart(df_filtered),
                use_container_width=True,
                key="currency_detailed"
            )
        
        with col2:
            st.plotly_chart(
                create_device_chart(df_filtered),
                use_container_width=True,
                key="device_detailed"
            )
        
        st.markdown("---")
        
        # Fila 2: Heatmap
        st.plotly_chart(
            create_heatmap_by_day_hour(df_filtered),
            use_container_width=True,
            key="heatmap_detailed"
        )
        
        st.markdown("---")
        
        # Análisis por Status con métricas
        st.subheader("📊 Análisis por Status")
        
        status_analysis = df_filtered.groupby('status').agg({
            'amount_usd': ['sum', 'mean', 'count']
        }).round(2)
        status_analysis.columns = ['Volumen Total (USD)', 'Promedio (USD)', 'Cantidad']
        
        # Formatear como moneda
        status_analysis['Volumen Total (USD)'] = status_analysis['Volumen Total (USD)'].apply(format_currency_usd)
        status_analysis['Promedio (USD)'] = status_analysis['Promedio (USD)'].apply(format_currency_usd)
        
        st.dataframe(
            status_analysis,
            use_container_width=True
        )
    
    # ==================== TAB 3: DATOS CRUDOS ====================
    
    with tab3:
        st.subheader("📋 Últimas 100 Transacciones")
        st.markdown("**Nota**: Los montos están normalizados a USD usando tasas de cambio fijas.")
        
        # Tabla avanzada
        render_advanced_table(df_filtered)
        
        # Opción de descarga
        st.markdown("---")
        
        col1, col2 = st.columns([3, 1])
        
        with col2:
            csv = df_filtered.to_csv(index=False)
            st.download_button(
                label="📥 Descargar CSV",
                data=csv,
                file_name=f"transactions_{datetime.now().strftime('%Y%m%d')}.csv",
                mime="text/csv",
                use_container_width=True
            )
    
    # ==================== FOOTER ====================
    
    st.markdown("---")
    st.markdown(f"""
    <div style='text-align: center; color: #64748b; padding: 20px;'>
        <p><b>Dashboard actualizado:</b> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
        <p>Todas las métricas globales están normalizadas a USD | Datos: PostgreSQL en Railway</p>
        <p><small>v2.0 - Lead BI Developer</small></p>
    </div>
    """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()
