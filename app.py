"""
SaaS Financial Intelligence Dashboard v3.0 - Gold Master
Dashboard profesional con optimizaciones avanzadas y UX mejorada.

Mejoras v3.0:
- Vectorización con .map() para alto rendimiento
- Localización completa en español
- Corrección de bugs en Plotly con custom_data
- Status con emojis integrados
- Insights automáticos inteligentes
- Robustez total en cálculos de deltas
- Badge de versión demo
- Código production-ready

Author: Lead Python BI Developer
Date: 2026-01-31
"""

import os
from datetime import datetime

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from dotenv import load_dotenv
from sqlalchemy import create_engine, text

# ==================== CONFIGURACIÓN ====================

st.set_page_config(
    page_title="Dashboard Financial Intelligence",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="expanded"
)

load_dotenv()

# ==================== CONSTANTES ====================

# Tasas de cambio fijas (USD como base)
EXCHANGE_RATES = {
    'USD': 1.0,
    'EUR': 1.08,
    'GBP': 1.27,
    'COP': 0.00025
}

# Colores consistentes
STATUS_COLORS = {
    'COMPLETED': '#2ecc71',
    'FAILED': '#e74c3c',
    'PENDING': '#f39c12',
    'REFUNDED': '#9b59b6'
}

CURRENCY_COLORS = {
    'USD': '#1f77b4',
    'EUR': '#ff7f0e',
    'GBP': '#2ca02c',
    'COP': '#d62728'
}

# Emojis para Status
STATUS_EMOJIS = {
    'COMPLETED': '✅',
    'FAILED': '❌',
    'PENDING': '⏳',
    'REFUNDED': '💰'
}

# Localización: Días de la semana en español
DAYS_ES = {
    'Monday': 'Lunes',
    'Tuesday': 'Martes',
    'Wednesday': 'Miércoles',
    'Thursday': 'Jueves',
    'Friday': 'Viernes',
    'Saturday': 'Sábado',
    'Sunday': 'Domingo'
}

# ==================== CSS PERSONALIZADO ====================

st.markdown("""
    <style>
    /* General */
    .main {
        padding: 0rem 1rem;
    }
    
    /* Badge Demo */
    .demo-badge {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 8px 16px;
        border-radius: 20px;
        font-weight: 600;
        display: inline-block;
        margin-bottom: 1rem;
        font-size: 0.9rem;
        box-shadow: 0 2px 8px rgba(102, 126, 234, 0.3);
    }
    
    /* Insights Box */
    .insights-box {
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        padding: 20px;
        border-radius: 12px;
        color: white;
        margin: 1rem 0;
        box-shadow: 0 4px 12px rgba(245, 87, 108, 0.3);
    }
    
    .insights-box h3 {
        color: white !important;
        margin-top: 0;
        font-size: 1.2rem;
    }
    
    .insights-box p {
        margin: 0.5rem 0;
        font-size: 1rem;
        line-height: 1.6;
    }
    
    /* Headers */
    h1 {
        color: #1e3a8a;
        font-weight: 700;
    }
    
    h2 {
        color: #334155;
        font-weight: 600;
    }
    
    /* Metrics */
    [data-testid="stMetricValue"] {
        font-size: 2rem;
        font-weight: 700;
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
    </style>
    """, unsafe_allow_html=True)

# ==================== FUNCIONES DE CONEXIÓN ====================

@st.cache_resource
def init_connection():
    """Inicializa conexión a PostgreSQL con cache persistente."""
    database_url = os.getenv('DATABASE_URL')
    
    if not database_url:
        st.error("❌ DATABASE_URL no configurado en .env")
        st.stop()
    
    try:
        engine = create_engine(
            database_url,
            pool_pre_ping=True,
            pool_size=10,
            max_overflow=20
        )
        # Test de conexión
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        return engine
    except Exception as e:
        st.error(f"❌ Error al conectar a PostgreSQL: {e}")
        st.stop()


@st.cache_data(ttl=300)
def load_data():
    """
    Carga datos desde PostgreSQL con transformaciones optimizadas.
    
    OPTIMIZACIÓN v3.0: Usa vectorización con .map() en lugar de .apply()
    """
    engine = init_connection()
    
    query = """
    SELECT 
        id, timestamp, amount, currency, status,
        client_email, client_ip, client_device, metadata
    FROM transactions
    ORDER BY timestamp DESC
    """
    
    try:
        df = pd.read_sql(query, engine)
        
        # Convertir timestamp
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        
        # OPTIMIZACIÓN: Normalización vectorizada (mucho más rápido que .apply())
        df['amount_usd'] = df['amount'] * df['currency'].map(EXCHANGE_RATES).fillna(1.0)
        
        # Columnas temporales
        df['date'] = df['timestamp'].dt.date
        df['year_month'] = df['timestamp'].dt.to_period('M').astype(str)
        df['week'] = df['timestamp'].dt.to_period('W').astype(str)
        
        # LOCALIZACIÓN: Días en español con .map()
        df['day_of_week'] = df['timestamp'].dt.day_name().map(DAYS_ES)
        df['hour'] = df['timestamp'].dt.hour
        
        # UX: Status con emojis integrados
        df['status_icon'] = df['status'].map(lambda x: f"{STATUS_EMOJIS.get(x, '📊')} {x}")
        
        return df
    
    except Exception as e:
        st.error(f"❌ Error al cargar datos: {e}")
        st.stop()

# ==================== FUNCIONES DE ANÁLISIS ====================

def calculate_insights(df):
    """
    Genera insights automáticos del dataset.
    
    Returns:
        dict con insights clave
    """
    insights = {}
    
    try:
        # Moneda con mayor volumen (USD normalizado)
        currency_volume = df.groupby('currency')['amount_usd'].sum()
        top_currency = currency_volume.idxmax()
        top_currency_volume = currency_volume.max()
        top_currency_pct = (top_currency_volume / df['amount_usd'].sum() * 100)
        
        insights['top_currency'] = top_currency
        insights['top_currency_volume'] = top_currency_volume
        insights['top_currency_pct'] = top_currency_pct
        
        # Día más activo
        day_activity = df.groupby('day_of_week').size()
        busiest_day = day_activity.idxmax()
        busiest_day_count = day_activity.max()
        
        insights['busiest_day'] = busiest_day
        insights['busiest_day_count'] = busiest_day_count
        
        # Tasa de éxito
        success_rate = (len(df[df['status'] == 'COMPLETED']) / len(df) * 100)
        insights['success_rate'] = success_rate
        
    except Exception as e:
        st.warning(f"No se pudieron generar algunos insights: {e}")
        insights = {
            'top_currency': 'N/A',
            'top_currency_volume': 0,
            'top_currency_pct': 0,
            'busiest_day': 'N/A',
            'busiest_day_count': 0,
            'success_rate': 0
        }
    
    return insights


def calculate_delta_robust(df, metric_col='amount_usd', period_col='year_month'):
    """
    Calcula delta % de forma robusta con manejo completo de errores.
    
    ROBUSTEZ v3.0: No falla con rangos de fecha cortos.
    """
    try:
        if len(df) == 0 or period_col not in df.columns:
            return 0
        
        periods = sorted(df[period_col].unique())
        
        if len(periods) < 2:
            return 0
        
        current_period = periods[-1]
        previous_period = periods[-2]
        
        current_value = df[df[period_col] == current_period][metric_col].sum()
        previous_value = df[df[period_col] == previous_period][metric_col].sum()
        
        if previous_value == 0:
            return 0
        
        delta = ((current_value - previous_value) / previous_value * 100)
        return delta
    
    except Exception:
        return 0


def format_currency_usd(value):
    """Formatea valores en USD con sufijos."""
    if pd.isna(value) or value == 0:
        return "$0"
    
    if abs(value) >= 1_000_000_000:
        return f"${value/1_000_000_000:.2f}B"
    elif abs(value) >= 1_000_000:
        return f"${value/1_000_000:.2f}M"
    elif abs(value) >= 1_000:
        return f"${value/1_000:.1f}K"
    else:
        return f"${value:.2f}"

# ==================== COMPONENTES DE VISUALIZACIÓN ====================

def render_insights_banner(insights):
    """Renderiza banner de insights automáticos."""
    st.markdown(f"""
    <div class="insights-box">
        <h3>🎯 Insights Automáticos</h3>
        <p><strong>💰 Moneda Dominante:</strong> {insights['top_currency']} con {format_currency_usd(insights['top_currency_volume'])} USD 
        ({insights['top_currency_pct']:.1f}% del volumen total)</p>
        <p><strong>📅 Día Más Activo:</strong> {insights['busiest_day']} con {insights['busiest_day_count']:,} transacciones</p>
        <p><strong>✅ Tasa de Éxito Global:</strong> {insights['success_rate']:.1f}% de transacciones completadas</p>
    </div>
    """, unsafe_allow_html=True)


def render_kpis(df):
    """Renderiza KPIs principales con deltas robustos."""
    st.subheader("📊 Métricas Principales (USD Normalizado)")
    
    if len(df) == 0:
        st.warning("⚠️ No hay datos para mostrar")
        return
    
    col1, col2, col3, col4 = st.columns(4)
    
    # KPI 1: Total Transacciones
    total_txns = len(df)
    txn_delta = calculate_delta_robust(
        df.groupby('year_month').size().reset_index(name='count').assign(amount_usd=lambda x: x['count']),
        metric_col='amount_usd',
        period_col='year_month'
    )
    
    with col1:
        st.metric(
            label="📊 Total Transacciones",
            value=f"{total_txns:,}",
            delta=f"{txn_delta:+.1f}% vs mes anterior" if txn_delta != 0 else None,
            help="Cantidad total de transacciones"
        )
    
    # KPI 2: Volumen Total USD
    total_volume = df['amount_usd'].sum()
    volume_delta = calculate_delta_robust(df, 'amount_usd', 'year_month')
    
    with col2:
        st.metric(
            label="💰 Volumen Total",
            value=format_currency_usd(total_volume),
            delta=f"{volume_delta:+.1f}% vs mes anterior" if volume_delta != 0 else None,
            help="Suma total normalizada a USD"
        )
    
    # KPI 3: Ticket Promedio
    avg_ticket = df['amount_usd'].mean()
    
    # Calcular delta de promedio de forma robusta
    try:
        periods = sorted(df['year_month'].unique())
        if len(periods) >= 2:
            current_avg = df[df['year_month'] == periods[-1]]['amount_usd'].mean()
            prev_avg = df[df['year_month'] == periods[-2]]['amount_usd'].mean()
            avg_delta = ((current_avg - prev_avg) / prev_avg * 100) if prev_avg > 0 else 0
        else:
            avg_delta = 0
    except:
        avg_delta = 0
    
    with col3:
        st.metric(
            label="🎯 Ticket Promedio",
            value=format_currency_usd(avg_ticket),
            delta=f"{avg_delta:+.1f}% vs mes anterior" if avg_delta != 0 else None,
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
    """Gráfico de tendencia temporal."""
    daily = df.groupby('date').agg({
        'amount_usd': 'sum',
        'id': 'count'
    }).reset_index()
    daily.columns = ['Fecha', 'Volumen USD', 'Cantidad']
    
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        x=daily['Fecha'],
        y=daily['Volumen USD'],
        name='Volumen (USD)',
        mode='lines+markers',
        line=dict(color='#3b82f6', width=3),
        marker=dict(size=6),
        fill='tozeroy',
        fillcolor='rgba(59, 130, 246, 0.1)',
        yaxis='y',
        hovertemplate='<b>%{x}</b><br>Volumen: $%{y:,.2f}<extra></extra>'
    ))
    
    fig.add_trace(go.Scatter(
        x=daily['Fecha'],
        y=daily['Cantidad'],
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
            tickformat='$,.0f'
        ),
        yaxis2=dict(
            title='Número de Transacciones',
            titlefont=dict(color='#f59e0b'),
            overlaying='y',
            side='right'
        ),
        height=400,
        hovermode='x unified',
        template='plotly_white',
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )
    
    return fig


def create_status_donut(df):
    """Gráfico donut de distribución de status."""
    status_dist = df.groupby('status').size().reset_index(name='Cantidad')
    
    colors = [STATUS_COLORS.get(s, '#94a3b8') for s in status_dist['status']]
    
    fig = go.Figure(data=[go.Pie(
        labels=status_dist['status'],
        values=status_dist['Cantidad'],
        hole=0.5,
        marker=dict(colors=colors, line=dict(color='#ffffff', width=2)),
        textinfo='label+percent',
        textfont=dict(size=12),
        hovertemplate='<b>%{label}</b><br>Transacciones: %{value:,}<br>%{percent}<extra></extra>'
    )])
    
    fig.update_layout(
        title='📊 Distribución por Estado',
        height=400,
        template='plotly_white',
        legend=dict(orientation="h", yanchor="bottom", y=-0.2, xanchor="center", x=0.5)
    )
    
    return fig


def create_currency_chart(df):
    """
    Gráfico de barras por moneda.
    
    CORRECCIÓN v3.0: Usa custom_data para evitar bug de hover.
    """
    currency_data = df.groupby('currency').agg({
        'amount': 'sum',
        'id': 'count'
    }).reset_index()
    currency_data.columns = ['Moneda', 'Volumen', 'Cantidad']
    currency_data = currency_data.sort_values('Cantidad', ascending=False)
    
    fig = px.bar(
        currency_data,
        x='Moneda',
        y='Volumen',
        title='💵 Volumen por Moneda (Moneda Original)',
        labels={'Volumen': 'Volumen Total'},
        color='Moneda',
        color_discrete_map=CURRENCY_COLORS,
        text='Volumen',
        custom_data=['Cantidad']  # CORRECCIÓN: Pasar cantidad como custom_data
    )
    
    fig.update_traces(
        texttemplate='%{text:,.0f}',
        textposition='outside',
        hovertemplate='<b>%{x}</b><br>Volumen: %{y:,.2f}<br>Transacciones: %{customdata[0]:,}<extra></extra>'
    )
    
    fig.update_layout(
        showlegend=False,
        height=400,
        template='plotly_white'
    )
    
    return fig


def create_device_chart(df):
    """Gráfico de barras por dispositivo."""
    device_data = df.groupby('client_device').agg({
        'amount_usd': 'sum',
        'id': 'count'
    }).reset_index()
    device_data.columns = ['Dispositivo', 'Volumen USD', 'Cantidad']
    
    fig = px.bar(
        device_data,
        x='Dispositivo',
        y='Volumen USD',
        title='📱 Volumen por Dispositivo (USD)',
        color='Dispositivo',
        color_discrete_map={'mobile': '#f59e0b', 'desktop': '#3b82f6'},
        text='Volumen USD',
        custom_data=['Cantidad']
    )
    
    fig.update_traces(
        texttemplate='$%{text:,.0f}',
        textposition='outside',
        hovertemplate='<b>%{x}</b><br>Volumen: $%{y:,.0f}<br>Transacciones: %{customdata[0]:,}<extra></extra>'
    )
    
    fig.update_layout(
        showlegend=False,
        height=350,
        template='plotly_white'
    )
    
    return fig


def create_heatmap(df):
    """Heatmap de actividad por día y hora."""
    heatmap_data = df.groupby(['day_of_week', 'hour']).size().reset_index(name='Cantidad')
    heatmap_pivot = heatmap_data.pivot(index='day_of_week', columns='hour', values='Cantidad').fillna(0)
    
    # Ordenar días
    days_order = ['Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes', 'Sábado', 'Domingo']
    heatmap_pivot = heatmap_pivot.reindex([d for d in days_order if d in heatmap_pivot.index])
    
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
        title='🔥 Mapa de Calor: Actividad por Día y Hora',
        xaxis_title='Hora del Día',
        yaxis_title='Día de la Semana',
        height=350,
        template='plotly_white'
    )
    
    return fig


def render_advanced_table(df):
    """Tabla avanzada con configuración profesional."""
    display_df = df.head(100).copy()
    
    column_config = {
        "timestamp": st.column_config.DatetimeColumn(
            "Fecha/Hora",
            format="DD/MM/YYYY HH:mm",
            width="medium"
        ),
        "amount": st.column_config.NumberColumn(
            "Monto",
            format="%.2f",
            width="small"
        ),
        "amount_usd": st.column_config.NumberColumn(
            "Monto USD",
            format="$%.2f",
            width="medium"
        ),
        "currency": st.column_config.TextColumn(
            "💱 Moneda",
            width="small"
        ),
        "status_icon": st.column_config.TextColumn(
            "📊 Estado",
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
    
    columns_show = [
        'timestamp', 'amount', 'currency', 'amount_usd',
        'status_icon', 'client_email', 'client_device'
    ]
    
    st.dataframe(
        display_df[columns_show],
        column_config=column_config,
        width=None,  # Actualizado de use_container_width
        height=500,
        hide_index=True
    )

# ==================== APLICACIÓN PRINCIPAL ====================

def main():
    """Función principal del dashboard."""
    
    # Badge de versión demo
    st.markdown("""
    <div class="demo-badge">
        ⚡ DEMO VERSION v3.0: Métricas normalizadas a USD con tasas fijas
    </div>
    """, unsafe_allow_html=True)
    
    # Header
    st.title("💰 Dashboard de Inteligencia Financiera SaaS")
    st.markdown("**Análisis profesional con normalización de monedas y insights automáticos**")
    st.markdown("---")
    
    # Cargar datos
    with st.spinner("📊 Cargando datos desde PostgreSQL..."):
        df = load_data()
    
    # ==================== SIDEBAR ====================
    
    st.sidebar.title("🔍 Filtros")
    st.sidebar.markdown("---")
    
    # Filtros
    all_currencies = sorted(df['currency'].unique())
    selected_currencies = st.sidebar.multiselect(
        "💵 Monedas",
        options=all_currencies,
        default=all_currencies
    )
    
    all_statuses = sorted(df['status'].unique())
    selected_statuses = st.sidebar.multiselect(
        "📊 Estados",
        options=all_statuses,
        default=all_statuses
    )
    
    st.sidebar.markdown("---")
    date_range = st.sidebar.date_input(
        "📅 Rango de Fechas",
        value=(df['timestamp'].min().date(), df['timestamp'].max().date()),
        min_value=df['timestamp'].min().date(),
        max_value=df['timestamp'].max().date()
    )
    
    # Info de tasas
    st.sidebar.markdown("---")
    st.sidebar.info(
        "**💱 Tasas de Cambio a USD**\n\n" +
        "• USD: 1.00\n" +
        "• EUR: 1.08\n" +
        "• GBP: 1.27\n" +
        "• COP: 0.00025"
    )
    
    # ==================== APLICAR FILTROS ====================
    
    df_filtered = df.copy()
    
    if selected_currencies:
        df_filtered = df_filtered[df_filtered['currency'].isin(selected_currencies)]
    
    if selected_statuses:
        df_filtered = df_filtered[df_filtered['status'].isin(selected_statuses)]
    
    if len(date_range) == 2:
        start, end = date_range
        df_filtered = df_filtered[
            (df_filtered['timestamp'].dt.date >= start) &
            (df_filtered['timestamp'].dt.date <= end)
        ]
    
    st.sidebar.markdown("---")
    st.sidebar.success(f"✅ {len(df_filtered):,} transacciones")
    st.sidebar.caption(f"Total: {len(df):,}")
    
    if len(df_filtered) == 0:
        st.warning("⚠️ No hay datos con estos filtros")
        return
    
    # ==================== TABS ====================
    
    tab1, tab2, tab3 = st.tabs([
        "📈 Resumen",
        "🌍 Detalle",
        "📋 Datos"
    ])
    
    # TAB 1: RESUMEN
    with tab1:
        # Insights automáticos
        insights = calculate_insights(df_filtered)
        render_insights_banner(insights)
        
        st.markdown("---")
        
        # KPIs
        render_kpis(df_filtered)
        
        st.markdown("---")
        
        # Gráficos principales
        col1, col2 = st.columns(2)
        
        with col1:
            st.plotly_chart(create_trend_chart(df_filtered), width='stretch')
        
        with col2:
            st.plotly_chart(create_status_donut(df_filtered), width='stretch')
        
        # Stats adicionales
        st.markdown("---")
        st.subheader("📊 Estadísticas Adicionales")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("💎 Máxima", format_currency_usd(df_filtered['amount_usd'].max()))
        
        with col2:
            st.metric("💵 Mínima", format_currency_usd(df_filtered['amount_usd'].min()))
        
        with col3:
            unique = df_filtered['client_email'].nunique()
            st.metric("👥 Clientes", f"{unique:,}")
        
        with col4:
            mobile_pct = len(df_filtered[df_filtered['client_device'] == 'mobile']) / len(df_filtered) * 100
            st.metric("📱 Mobile", f"{mobile_pct:.1f}%")
    
    # TAB 2: DETALLE
    with tab2:
        st.subheader("🌍 Análisis Detallado por Segmentos")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.plotly_chart(create_currency_chart(df_filtered), width='stretch')
        
        with col2:
            st.plotly_chart(create_device_chart(df_filtered), width='stretch')
        
        st.markdown("---")
        st.plotly_chart(create_heatmap(df_filtered), width='stretch')
        
        st.markdown("---")
        st.subheader("📊 Resumen por Estado")
        
        status_summary = df_filtered.groupby('status').agg({
            'amount_usd': ['sum', 'mean', 'count']
        }).round(2)
        status_summary.columns = ['Volumen Total USD', 'Promedio USD', 'Cantidad']
        status_summary['Volumen Total USD'] = status_summary['Volumen Total USD'].apply(format_currency_usd)
        status_summary['Promedio USD'] = status_summary['Promedio USD'].apply(format_currency_usd)
        
        st.dataframe(status_summary, width=None)
    
    # TAB 3: DATOS
    with tab3:
        st.subheader("📋 Últimas 100 Transacciones")
        st.caption("Nota: Montos normalizados a USD con tasas fijas")
        
        render_advanced_table(df_filtered)
        
        st.markdown("---")
        
        col1, col2 = st.columns([3, 1])
        
        with col2:
            csv = df_filtered.to_csv(index=False)
            st.download_button(
                label="📥 Descargar CSV",
                data=csv,
                file_name=f"transacciones_{datetime.now().strftime('%Y%m%d')}.csv",
                mime="text/csv"
            )
    
    # Footer
    st.markdown("---")
    st.markdown(f"""
    <div style='text-align: center; color: #64748b; padding: 20px;'>
        <p><b>Actualizado:</b> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
        <p>Dashboard v3.0 Gold Master | PostgreSQL en Railway</p>
        <p><small>Lead Python BI Developer</small></p>
    </div>
    """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()
