"""
Financial Intelligence Dashboard v4.0 - Enterprise Edition
Professional minimalist design for financial analytics.

Design Principles:
- Zero emojis, pure data focus
- Monochromatic palette with single accent color
- High data density, minimal spacing
- System fonts, tabular numerals
- Excel/Stripe-inspired table layouts

Author: Senior Frontend Engineer (Fintech Specialist)
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
    page_title="Financial Intelligence",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

load_dotenv()

# ==================== CONSTANTES ====================

# Tasas de cambio (base USD)
EXCHANGE_RATES = {
    'USD': 1.0,
    'EUR': 1.08,
    'GBP': 1.27,
    'COP': 0.00025
}

# Colores enterprise (minimalista)
COLOR_PRIMARY = '#0f172a'      # Slate 900
COLOR_ACCENT = '#3b82f6'       # Blue 500
COLOR_SUCCESS = '#10b981'      # Green 500
COLOR_WARNING = '#f59e0b'      # Amber 500
COLOR_DANGER = '#ef4444'       # Red 500
COLOR_GRAY = '#6b7280'         # Gray 500
COLOR_LIGHT_GRAY = '#e5e7eb'   # Gray 200

# Status colors (minimalista)
STATUS_COLORS = {
    'COMPLETED': COLOR_SUCCESS,
    'FAILED': COLOR_DANGER,
    'PENDING': COLOR_WARNING,
    'REFUNDED': COLOR_GRAY
}

# ==================== CSS ENTERPRISE ====================

st.markdown("""
    <style>
    /* Reset y Fuentes */
    html, body, [class*="css"] {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
        font-size: 13px;
        color: #1a1a1a;
    }
    
    /* Títulos Sobrios */
    h1 { 
        font-size: 24px; 
        font-weight: 600; 
        color: #111; 
        letter-spacing: -0.5px; 
        margin-bottom: 8px;
        margin-top: 0;
    }
    
    h2 {
        font-size: 18px;
        font-weight: 600;
        color: #111;
        letter-spacing: -0.3px;
        margin-top: 16px;
        margin-bottom: 8px;
    }
    
    h3 { 
        font-size: 14px; 
        font-weight: 600; 
        color: #444; 
        margin-top: 12px;
        margin-bottom: 8px;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    
    /* Métricas Compactas con Números Monoespaciados */
    [data-testid="stMetricValue"] {
        font-size: 28px !important;
        font-weight: 500 !important;
        font-family: 'SF Mono', 'Consolas', 'Courier New', monospace !important;
        font-variant-numeric: tabular-nums !important;
        color: #0f172a !important;
    }
    
    [data-testid="stMetricLabel"] { 
        font-size: 11px !important; 
        color: #666 !important; 
        font-weight: 600 !important;
        text-transform: uppercase !important;
        letter-spacing: 0.5px !important;
    }
    
    [data-testid="stMetricDelta"] { 
        font-size: 11px !important;
        font-family: 'SF Mono', 'Consolas', monospace !important;
    }

    /* Sidebar Minimalista */
    [data-testid="stSidebar"] { 
        background-color: #fafafa; 
        border-right: 1px solid #e5e7eb;
    }
    
    /* Tablas estilo Excel/Stripe */
    .stDataFrame { 
        border: 1px solid #e5e7eb; 
        border-radius: 4px;
        font-size: 12px;
    }
    
    /* Tabs minimalistas */
    .stTabs [data-baseweb="tab-list"] {
        gap: 0;
        border-bottom: 1px solid #e5e7eb;
    }
    
    .stTabs [data-baseweb="tab"] {
        height: 40px;
        padding: 0px 20px;
        background-color: transparent;
        border: none;
        color: #6b7280;
        font-weight: 500;
        font-size: 13px;
    }
    
    .stTabs [aria-selected="true"] {
        background-color: transparent;
        color: #0f172a;
        border-bottom: 2px solid #0f172a;
    }
    
    /* Reducir espaciados globales */
    .main .block-container {
        padding-top: 1rem;
        padding-bottom: 1rem;
        padding-left: 2rem;
        padding-right: 2rem;
    }
    
    /* Botones minimalistas */
    .stButton>button {
        border: 1px solid #e5e7eb;
        background-color: white;
        color: #374151;
        font-size: 12px;
        font-weight: 500;
        padding: 0.5rem 1rem;
        border-radius: 4px;
    }
    
    .stButton>button:hover {
        border-color: #9ca3af;
        background-color: #f9fafb;
    }
    
    /* Download button específico */
    .stDownloadButton>button {
        border: 1px solid #e5e7eb;
        background-color: white;
        color: #374151;
        font-size: 11px;
        font-weight: 500;
        padding: 0.4rem 0.8rem;
    }
    
    /* Inputs y selectores minimalistas */
    .stMultiSelect [data-baseweb="select"] {
        border: 1px solid #e5e7eb;
        font-size: 12px;
    }
    
    /* Info boxes discretos */
    .stAlert {
        background-color: #f9fafb;
        border: 1px solid #e5e7eb;
        border-radius: 4px;
        padding: 0.75rem;
        font-size: 12px;
    }
    </style>
    """, unsafe_allow_html=True)

# ==================== CONEXIÓN ====================

@st.cache_resource
def init_connection():
    """Inicializa conexión a PostgreSQL."""
    database_url = os.getenv('DATABASE_URL')
    
    if not database_url:
        st.error("DATABASE_URL not configured")
        st.stop()
    
    try:
        engine = create_engine(database_url, pool_pre_ping=True, pool_size=10, max_overflow=20)
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        return engine
    except Exception as e:
        st.error(f"Database connection failed: {e}")
        st.stop()


@st.cache_data(ttl=300)
def load_data():
    """Carga y transforma datos con optimización vectorizada."""
    engine = init_connection()
    
    query = """
    SELECT id, timestamp, amount, currency, status,
           client_email, client_ip, client_device, metadata
    FROM transactions
    ORDER BY timestamp DESC
    """
    
    try:
        df = pd.read_sql(query, engine)
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        
        # Vectorización pura
        df['amount_usd'] = df['amount'] * df['currency'].map(EXCHANGE_RATES).fillna(1.0)
        
        # Temporal data
        df['date'] = df['timestamp'].dt.date
        df['year_month'] = df['timestamp'].dt.to_period('M').astype(str)
        df['week'] = df['timestamp'].dt.to_period('W').astype(str)
        df['day_of_week'] = df['timestamp'].dt.day_name()
        df['hour'] = df['timestamp'].dt.hour
        
        # Formato fecha ISO corto
        df['date_display'] = df['timestamp'].dt.strftime('%a, %b %d')
        
        return df
    
    except Exception as e:
        st.error(f"Data loading failed: {e}")
        st.stop()

# ==================== UTILIDADES ====================

def format_currency(value):
    """Formatea moneda con estilo financiero."""
    if pd.isna(value) or value == 0:
        return "$0"
    
    if abs(value) >= 1_000_000_000:
        return f"${value/1_000_000_000:.2f}B"
    elif abs(value) >= 1_000_000:
        return f"${value/1_000_000:.2f}M"
    elif abs(value) >= 1_000:
        return f"${value/1_000:.1f}K"
    else:
        return f"${value:,.2f}"


def format_number(value):
    """Formatea números con separadores."""
    return f"{value:,}" if not pd.isna(value) else "0"


def calculate_delta(df, metric_col='amount_usd', period_col='year_month'):
    """Calcula delta % robusto."""
    try:
        if len(df) == 0 or period_col not in df.columns:
            return 0
        
        periods = sorted(df[period_col].unique())
        if len(periods) < 2:
            return 0
        
        current = df[df[period_col] == periods[-1]][metric_col].sum()
        previous = df[df[period_col] == periods[-2]][metric_col].sum()
        
        if previous == 0:
            return 0
        
        return ((current - previous) / previous * 100)
    except:
        return 0

# ==================== COMPONENTES ====================

def render_ledger_table(df):
    """Tabla resumen estilo libro mayor (The Ledger)."""
    st.markdown("### Currency Ledger")
    
    ledger = df.groupby('currency').agg({
        'amount_usd': 'sum',
        'id': 'count'
    }).reset_index()
    
    total_volume = ledger['amount_usd'].sum()
    ledger['percentage'] = (ledger['amount_usd'] / total_volume * 100).round(2)
    
    ledger.columns = ['Currency', 'Volume (USD)', 'Transactions', '% of Total']
    ledger = ledger.sort_values('Volume (USD)', ascending=False)
    
    # Formatear
    ledger['Volume (USD)'] = ledger['Volume (USD)'].apply(format_currency)
    ledger['Transactions'] = ledger['Transactions'].apply(format_number)
    ledger['% of Total'] = ledger['% of Total'].apply(lambda x: f"{x}%")
    
    st.dataframe(
        ledger,
        use_container_width=True,
        hide_index=True,
        height=180
    )


def render_kpis(df):
    """KPIs minimalistas con números monoespaciados."""
    if len(df) == 0:
        st.warning("No data available")
        return
    
    col1, col2, col3, col4 = st.columns(4)
    
    # Total Transactions
    total = len(df)
    delta_txn = calculate_delta(
        df.groupby('year_month').size().reset_index(name='count').assign(amount_usd=lambda x: x['count'])
    )
    
    with col1:
        st.metric(
            label="Total Transactions",
            value=format_number(total),
            delta=f"{delta_txn:+.1f}% MoM" if delta_txn != 0 else None
        )
    
    # Total Volume
    volume = df['amount_usd'].sum()
    delta_vol = calculate_delta(df)
    
    with col2:
        st.metric(
            label="Total Volume",
            value=format_currency(volume),
            delta=f"{delta_vol:+.1f}% MoM" if delta_vol != 0 else None
        )
    
    # Average Ticket
    avg = df['amount_usd'].mean()
    try:
        periods = sorted(df['year_month'].unique())
        if len(periods) >= 2:
            curr_avg = df[df['year_month'] == periods[-1]]['amount_usd'].mean()
            prev_avg = df[df['year_month'] == periods[-2]]['amount_usd'].mean()
            delta_avg = ((curr_avg - prev_avg) / prev_avg * 100) if prev_avg > 0 else 0
        else:
            delta_avg = 0
    except:
        delta_avg = 0
    
    with col3:
        st.metric(
            label="Average Ticket",
            value=format_currency(avg),
            delta=f"{delta_avg:+.1f}% MoM" if delta_avg != 0 else None
        )
    
    # Success Rate
    completed = len(df[df['status'] == 'COMPLETED'])
    success_rate = (completed / len(df) * 100) if len(df) > 0 else 0
    
    with col4:
        st.metric(
            label="Success Rate",
            value=f"{success_rate:.1f}%",
            delta=f"{completed:,} completed"
        )


def create_trend_chart(df):
    """Gráfico minimalista de tendencia."""
    daily = df.groupby('date').agg({
        'amount_usd': 'sum',
        'id': 'count'
    }).reset_index()
    
    fig = go.Figure()
    
    # Área principal
    fig.add_trace(go.Scatter(
        x=daily['date'],
        y=daily['amount_usd'],
        name='Volume',
        mode='lines',
        line=dict(color=COLOR_ACCENT, width=2),
        fill='tozeroy',
        fillcolor=f'rgba(59, 130, 246, 0.1)',
        hovertemplate='<b>%{x}</b><br>Volume: $%{y:,.0f}<extra></extra>'
    ))
    
    fig.update_layout(
        title='Daily Volume Trend',
        xaxis_title='',
        yaxis_title='Volume (USD)',
        height=300,
        margin=dict(l=40, r=20, t=40, b=30),
        hovermode='x unified',
        template='plotly_white',
        font=dict(family='Inter, sans-serif', size=11),
        showlegend=False,
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)'
    )
    
    fig.update_xaxes(showgrid=False, zeroline=False)
    fig.update_yaxes(showgrid=True, gridcolor='#f3f4f6', zeroline=False, tickformat='$,.0f')
    
    return fig


def create_status_chart(df):
    """Gráfico de barras horizontal minimalista."""
    status_data = df.groupby('status').size().reset_index(name='count')
    status_data = status_data.sort_values('count', ascending=True)
    
    colors = [STATUS_COLORS.get(s, COLOR_GRAY) for s in status_data['status']]
    
    fig = go.Figure(go.Bar(
        x=status_data['count'],
        y=status_data['status'],
        orientation='h',
        marker=dict(color=colors),
        text=status_data['count'],
        textposition='outside',
        texttemplate='%{text:,}',
        hovertemplate='<b>%{y}</b><br>Count: %{x:,}<extra></extra>'
    ))
    
    fig.update_layout(
        title='Status Distribution',
        xaxis_title='',
        yaxis_title='',
        height=250,
        margin=dict(l=80, r=40, t=40, b=30),
        template='plotly_white',
        font=dict(family='Inter, sans-serif', size=11),
        showlegend=False,
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)'
    )
    
    fig.update_xaxes(showgrid=True, gridcolor='#f3f4f6', zeroline=False)
    fig.update_yaxes(showgrid=False)
    
    return fig


def create_currency_chart(df):
    """Gráfico de barras por moneda (escala de grises)."""
    currency_data = df.groupby('currency').agg({
        'amount': 'sum',
        'id': 'count'
    }).reset_index()
    currency_data = currency_data.sort_values('amount', ascending=False)
    
    # Colores en escala de grises
    gray_scale = ['#374151', '#6b7280', '#9ca3af', '#d1d5db']
    colors = [gray_scale[i % len(gray_scale)] for i in range(len(currency_data))]
    
    fig = go.Figure(go.Bar(
        x=currency_data['currency'],
        y=currency_data['amount'],
        marker=dict(color=colors),
        text=currency_data['amount'],
        textposition='outside',
        texttemplate='%{text:,.0f}',
        customdata=currency_data['id'],
        hovertemplate='<b>%{x}</b><br>Volume: %{y:,.0f}<br>Transactions: %{customdata:,}<extra></extra>'
    ))
    
    fig.update_layout(
        title='Volume by Currency (Original)',
        xaxis_title='',
        yaxis_title='',
        height=300,
        margin=dict(l=40, r=20, t=40, b=30),
        template='plotly_white',
        font=dict(family='Inter, sans-serif', size=11),
        showlegend=False,
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)'
    )
    
    fig.update_xaxes(showgrid=False)
    fig.update_yaxes(showgrid=True, gridcolor='#f3f4f6', zeroline=False, tickformat=',')
    
    return fig


def create_device_chart(df):
    """Gráfico simple de dispositivos."""
    device_data = df.groupby('client_device').agg({
        'amount_usd': 'sum'
    }).reset_index()
    
    fig = go.Figure(go.Bar(
        x=device_data['client_device'],
        y=device_data['amount_usd'],
        marker=dict(color=[COLOR_ACCENT, COLOR_GRAY]),
        text=device_data['amount_usd'],
        textposition='outside',
        texttemplate='$%{text:,.0f}',
        hovertemplate='<b>%{x}</b><br>Volume: $%{y:,.0f}<extra></extra>'
    ))
    
    fig.update_layout(
        title='Volume by Device (USD)',
        xaxis_title='',
        yaxis_title='',
        height=280,
        margin=dict(l=40, r=20, t=40, b=30),
        template='plotly_white',
        font=dict(family='Inter, sans-serif', size=11),
        showlegend=False,
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)'
    )
    
    fig.update_xaxes(showgrid=False)
    fig.update_yaxes(showgrid=True, gridcolor='#f3f4f6', zeroline=False, tickformat='$,.0f')
    
    return fig


def render_data_table(df):
    """Tabla de datos estilo Excel."""
    display_df = df.head(100).copy()
    
    column_config = {
        "timestamp": st.column_config.DatetimeColumn(
            "Date/Time",
            format="MMM DD, YYYY HH:mm",
            width="medium"
        ),
        "amount": st.column_config.NumberColumn(
            "Amount",
            format="%.2f",
            width="small"
        ),
        "amount_usd": st.column_config.NumberColumn(
            "Amount USD",
            format="$%.2f",
            width="medium"
        ),
        "currency": st.column_config.TextColumn(
            "Currency",
            width="small"
        ),
        "status": st.column_config.TextColumn(
            "Status",
            width="small"
        ),
        "client_email": st.column_config.TextColumn(
            "Client",
            width="large"
        ),
        "client_device": st.column_config.TextColumn(
            "Device",
            width="small"
        )
    }
    
    columns = ['timestamp', 'amount', 'currency', 'amount_usd', 'status', 'client_email', 'client_device']
    
    st.dataframe(
        display_df[columns],
        column_config=column_config,
        use_container_width=True,
        height=500,
        hide_index=True
    )

# ==================== MAIN ====================

def main():
    """Aplicación principal."""
    
    # Header minimalista
    col1, col2 = st.columns([3, 1])
    
    with col1:
        st.title("Financial Intelligence")
        st.caption("Real-time transaction analytics | USD normalized")
    
    with col2:
        # Export button discreto
        if st.button("Export Data", type="secondary", use_container_width=False):
            st.session_state.show_export = True
    
    st.markdown("---")
    
    # Cargar datos
    with st.spinner("Loading data..."):
        df = load_data()
    
    # ==================== SIDEBAR ====================
    
    st.sidebar.markdown("### Filters")
    
    # Filtros
    all_currencies = sorted(df['currency'].unique())
    selected_currencies = st.sidebar.multiselect(
        "Currency",
        options=all_currencies,
        default=all_currencies
    )
    
    all_statuses = sorted(df['status'].unique())
    selected_statuses = st.sidebar.multiselect(
        "Status",
        options=all_statuses,
        default=all_statuses
    )
    
    st.sidebar.markdown("---")
    
    date_range = st.sidebar.date_input(
        "Date Range",
        value=(df['timestamp'].min().date(), df['timestamp'].max().date()),
        min_value=df['timestamp'].min().date(),
        max_value=df['timestamp'].max().date()
    )
    
    st.sidebar.markdown("---")
    
    # Export en sidebar si activado
    if st.session_state.get('show_export', False):
        csv = df.to_csv(index=False)
        st.sidebar.download_button(
            label="Download CSV",
            data=csv,
            file_name=f"transactions_{datetime.now().strftime('%Y%m%d')}.csv",
            mime="text/csv"
        )
    
    st.sidebar.markdown("---")
    st.sidebar.caption("Exchange Rates (Fixed)")
    st.sidebar.caption("USD: 1.00 | EUR: 1.08")
    st.sidebar.caption("GBP: 1.27 | COP: 0.00025")
    
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
    st.sidebar.metric("Filtered Records", format_number(len(df_filtered)))
    st.sidebar.caption(f"Total: {format_number(len(df))}")
    
    if len(df_filtered) == 0:
        st.warning("No data matches the selected filters")
        return
    
    # ==================== TABS ====================
    
    tab1, tab2, tab3 = st.tabs(["Overview", "Analysis", "Data"])
    
    # TAB 1: OVERVIEW
    with tab1:
        # Ledger table primero
        render_ledger_table(df_filtered)
        
        st.markdown("---")
        
        # KPIs
        render_kpis(df_filtered)
        
        st.markdown("---")
        
        # Gráficos principales
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.plotly_chart(create_trend_chart(df_filtered), use_container_width=True)
        
        with col2:
            st.plotly_chart(create_status_chart(df_filtered), use_container_width=True)
        
        # Stats adicionales
        st.markdown("---")
        st.markdown("### Key Statistics")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Max Transaction", format_currency(df_filtered['amount_usd'].max()))
        
        with col2:
            st.metric("Min Transaction", format_currency(df_filtered['amount_usd'].min()))
        
        with col3:
            unique = df_filtered['client_email'].nunique()
            st.metric("Unique Clients", format_number(unique))
        
        with col4:
            mobile_pct = len(df_filtered[df_filtered['client_device'] == 'mobile']) / len(df_filtered) * 100
            st.metric("Mobile Share", f"{mobile_pct:.1f}%")
    
    # TAB 2: ANALYSIS
    with tab2:
        st.markdown("### Segment Analysis")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.plotly_chart(create_currency_chart(df_filtered), use_container_width=True)
        
        with col2:
            st.plotly_chart(create_device_chart(df_filtered), use_container_width=True)
        
        st.markdown("---")
        st.markdown("### Status Breakdown")
        
        status_summary = df_filtered.groupby('status').agg({
            'amount_usd': ['sum', 'mean', 'count']
        }).round(2)
        status_summary.columns = ['Total Volume', 'Average', 'Count']
        status_summary['Total Volume'] = status_summary['Total Volume'].apply(format_currency)
        status_summary['Average'] = status_summary['Average'].apply(format_currency)
        status_summary['Count'] = status_summary['Count'].apply(format_number)
        
        st.dataframe(status_summary, use_container_width=True)
    
    # TAB 3: DATA
    with tab3:
        st.markdown("### Transaction Data (Last 100)")
        st.caption("All amounts normalized to USD using fixed exchange rates")
        
        render_data_table(df_filtered)
    
    # Footer minimalista
    st.markdown("---")
    st.caption(f"Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | PostgreSQL on Railway | v4.0 Enterprise")


if __name__ == "__main__":
    main()
