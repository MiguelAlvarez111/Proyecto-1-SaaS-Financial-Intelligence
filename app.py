"""
Financial Intelligence Dashboard v5.0 - Modern SaaS Card UI
Professional card-based layout with gradient charts and polished design.

Design Features:
- Card-based architecture (all components in white cards)
- Modern area charts with gradients
- Donut charts for distributions
- Fixed visual bugs (alignment, labels, data filtering)
- Light gray background with white cards
- Soft shadows and rounded corners

Author: Product Designer (Streamlit + CSS Specialist)
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

EXCHANGE_RATES = {
    'USD': 1.0,
    'EUR': 1.08,
    'GBP': 1.27,
    'COP': 0.00025
}

# Modern color palette
COLOR_PRIMARY = '#6366f1'      # Indigo 500
COLOR_SUCCESS = '#10b981'      # Green 500
COLOR_WARNING = '#f59e0b'      # Amber 500
COLOR_DANGER = '#ef4444'       # Red 500
COLOR_INFO = '#3b82f6'         # Blue 500
COLOR_GRAY = '#6b7280'         # Gray 500

STATUS_COLORS = {
    'COMPLETED': COLOR_SUCCESS,
    'FAILED': COLOR_DANGER,
    'PENDING': COLOR_WARNING,
    'REFUNDED': COLOR_INFO
}

# ==================== CSS MODERN CARD UI ====================

st.markdown("""
    <style>
    /* Import Google Fonts */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
    
    /* Global Styles */
    html, body, [class*="css"] {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
        font-size: 14px;
        color: #1f2937;
    }
    
    /* Background color suave */
    .main {
        background-color: #f8fafc;
    }
    
    .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
        padding-left: 3rem;
        padding-right: 3rem;
    }
    
    /* Card Component - CRÍTICO */
    .card {
        background-color: #ffffff;
        border: 1px solid #e2e8f0;
        border-radius: 12px;
        padding: 24px;
        box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.1), 0 1px 2px 0 rgba(0, 0, 0, 0.06);
        margin-bottom: 20px;
        transition: box-shadow 0.3s ease;
    }
    
    .card:hover {
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
    }
    
    /* Card para KPIs más compacta */
    .card-kpi {
        background-color: #ffffff;
        border: 1px solid #e2e8f0;
        border-radius: 12px;
        padding: 20px;
        box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.1);
        margin-bottom: 16px;
        min-height: 120px;
        display: flex;
        flex-direction: column;
        justify-content: space-between;
    }
    
    /* Typography */
    h1 {
        font-size: 32px;
        font-weight: 700;
        color: #111827;
        letter-spacing: -0.5px;
        margin-bottom: 8px;
    }
    
    h2 {
        font-size: 20px;
        font-weight: 600;
        color: #374151;
        margin-bottom: 16px;
    }
    
    h3 {
        font-size: 14px;
        font-weight: 600;
        color: #6b7280;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        margin-bottom: 12px;
    }
    
    /* Metrics - Diseño Card */
    [data-testid="stMetricValue"] {
        font-size: 32px !important;
        font-weight: 700 !important;
        color: #111827 !important;
        font-variant-numeric: tabular-nums !important;
    }
    
    [data-testid="stMetricLabel"] {
        font-size: 12px !important;
        font-weight: 600 !important;
        color: #6b7280 !important;
        text-transform: uppercase !important;
        letter-spacing: 0.5px !important;
        margin-bottom: 8px !important;
    }
    
    [data-testid="stMetricDelta"] {
        font-size: 13px !important;
        font-weight: 500 !important;
    }
    
    /* Sidebar moderna */
    [data-testid="stSidebar"] {
        background-color: #ffffff;
        border-right: 1px solid #e5e7eb;
    }
    
    [data-testid="stSidebar"] h3 {
        color: #111827;
        font-size: 16px;
        font-weight: 600;
        margin-bottom: 16px;
    }
    
    /* Tabs modernas */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background-color: transparent;
        border-bottom: 2px solid #e5e7eb;
    }
    
    .stTabs [data-baseweb="tab"] {
        height: 48px;
        padding: 0px 24px;
        background-color: transparent;
        border: none;
        color: #6b7280;
        font-weight: 500;
        font-size: 14px;
        border-radius: 8px 8px 0 0;
    }
    
    .stTabs [aria-selected="true"] {
        background-color: transparent;
        color: #6366f1;
        border-bottom: 2px solid #6366f1;
        margin-bottom: -2px;
    }
    
    /* Dataframe styling */
    .stDataFrame {
        border-radius: 8px;
        border: 1px solid #e5e7eb;
        font-size: 13px;
    }
    
    /* Buttons */
    .stButton>button {
        border-radius: 8px;
        font-weight: 500;
        font-size: 14px;
        padding: 0.5rem 1.5rem;
        transition: all 0.2s ease;
    }
    
    .stDownloadButton>button {
        background-color: #6366f1;
        color: white;
        border: none;
        border-radius: 8px;
        font-weight: 500;
        padding: 0.5rem 1.5rem;
    }
    
    .stDownloadButton>button:hover {
        background-color: #4f46e5;
    }
    
    /* MultiSelect */
    .stMultiSelect [data-baseweb="select"] {
        border-radius: 8px;
        border-color: #e5e7eb;
    }
    
    /* Caption styling */
    .caption-text {
        font-size: 13px;
        color: #6b7280;
        margin-top: 8px;
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
    """Carga y transforma datos."""
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
        
        # Vectorización
        df['amount_usd'] = df['amount'] * df['currency'].map(EXCHANGE_RATES).fillna(1.0)
        
        # Temporal
        df['date'] = df['timestamp'].dt.date
        df['year_month'] = df['timestamp'].dt.to_period('M').astype(str)
        df['week'] = df['timestamp'].dt.to_period('W').astype(str)
        df['day_of_week'] = df['timestamp'].dt.day_name()
        df['hour'] = df['timestamp'].dt.hour
        
        return df
    except Exception as e:
        st.error(f"Data loading failed: {e}")
        st.stop()

# ==================== UTILIDADES ====================

def format_currency(value):
    """Formatea moneda."""
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
    """Formatea números."""
    return f"{value:,}" if not pd.isna(value) else "0"


def calculate_delta(df, metric_col='amount_usd', period_col='year_month'):
    """Calcula delta robusto."""
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

# ==================== COMPONENTES UI ====================

def render_kpis_cards(df):
    """Renderiza KPIs en tarjetas."""
    if len(df) == 0:
        st.warning("No data available")
        return
    
    col1, col2, col3, col4 = st.columns(4)
    
    # KPI 1: Total Transactions
    total = len(df)
    delta_txn = calculate_delta(
        df.groupby('year_month').size().reset_index(name='count').assign(amount_usd=lambda x: x['count'])
    )
    
    with col1:
        st.markdown('<div class="card-kpi">', unsafe_allow_html=True)
        st.metric(
            label="Total Transactions",
            value=format_number(total),
            delta=f"{delta_txn:+.1f}% MoM" if delta_txn != 0 else None
        )
        st.markdown('</div>', unsafe_allow_html=True)
    
    # KPI 2: Total Volume
    volume = df['amount_usd'].sum()
    delta_vol = calculate_delta(df)
    
    with col2:
        st.markdown('<div class="card-kpi">', unsafe_allow_html=True)
        st.metric(
            label="Total Volume",
            value=format_currency(volume),
            delta=f"{delta_vol:+.1f}% MoM" if delta_vol != 0 else None
        )
        st.markdown('</div>', unsafe_allow_html=True)
    
    # KPI 3: Average Ticket
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
        st.markdown('<div class="card-kpi">', unsafe_allow_html=True)
        st.metric(
            label="Average Ticket",
            value=format_currency(avg),
            delta=f"{delta_avg:+.1f}% MoM" if delta_avg != 0 else None
        )
        st.markdown('</div>', unsafe_allow_html=True)
    
    # KPI 4: Success Rate
    completed = len(df[df['status'] == 'COMPLETED'])
    success_rate = (completed / len(df) * 100) if len(df) > 0 else 0
    
    with col4:
        st.markdown('<div class="card-kpi">', unsafe_allow_html=True)
        st.metric(
            label="Success Rate",
            value=f"{success_rate:.1f}%",
            delta=f"{completed:,} completed"
        )
        st.markdown('</div>', unsafe_allow_html=True)


def create_trend_area_chart(df):
    """Gráfico de área con gradiente moderno."""
    daily = df.groupby('date').agg({
        'amount_usd': 'sum',
        'id': 'count'
    }).reset_index()
    
    fig = go.Figure()
    
    # Area chart con gradiente
    fig.add_trace(go.Scatter(
        x=daily['date'],
        y=daily['amount_usd'],
        name='Volume',
        mode='lines',
        line=dict(color='#6366f1', width=3),
        fill='tozeroy',
        fillcolor='rgba(99, 102, 241, 0.2)',
        hovertemplate='<b>%{x}</b><br>Volume: $%{y:,.0f}<extra></extra>'
    ))
    
    fig.update_layout(
        title=dict(
            text='Daily Transaction Volume',
            font=dict(size=16, weight=600, color='#374151')
        ),
        xaxis_title='',
        yaxis_title='Volume (USD)',
        height=350,  # Altura fija para alineación
        margin=dict(l=60, r=40, t=60, b=40),
        hovermode='x unified',
        template='plotly_white',
        font=dict(family='Inter, sans-serif', size=12),
        showlegend=False,
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)'
    )
    
    fig.update_xaxes(showgrid=False, zeroline=False)
    fig.update_yaxes(
        showgrid=True, 
        gridcolor='#f3f4f6', 
        zeroline=False, 
        tickformat='$,.0f'
    )
    
    return fig


def create_status_donut_chart(df):
    """Donut chart moderno para distribución de status."""
    status_data = df.groupby('status').size().reset_index(name='count')
    
    colors = [STATUS_COLORS.get(s, COLOR_GRAY) for s in status_data['status']]
    
    fig = go.Figure(go.Pie(
        labels=status_data['status'],
        values=status_data['count'],
        hole=0.6,  # Donut hole
        marker=dict(
            colors=colors,
            line=dict(color='#ffffff', width=3)
        ),
        textinfo='label+percent',
        textposition='outside',
        textfont=dict(size=12, family='Inter'),
        hovertemplate='<b>%{label}</b><br>Transactions: %{value:,}<br>%{percent}<extra></extra>'
    ))
    
    fig.update_layout(
        title=dict(
            text='Status Distribution',
            font=dict(size=16, weight=600, color='#374151')
        ),
        height=350,  # Altura fija para alineación
        margin=dict(l=20, r=20, t=60, b=20),
        template='plotly_white',
        font=dict(family='Inter, sans-serif', size=12),
        showlegend=True,
        legend=dict(
            orientation="v",
            yanchor="middle",
            y=0.5,
            xanchor="left",
            x=1.1
        ),
        paper_bgcolor='rgba(0,0,0,0)'
    )
    
    return fig


def create_currency_bar_chart(df):
    """Gráfico de barras con márgenes corregidos."""
    currency_data = df.groupby('currency').agg({
        'amount': 'sum',
        'id': 'count'
    }).reset_index()
    currency_data = currency_data.sort_values('amount', ascending=True)
    
    fig = go.Figure(go.Bar(
        x=currency_data['amount'],
        y=currency_data['currency'],
        orientation='h',
        marker=dict(
            color='#6366f1',
            line=dict(color='#4f46e5', width=1)
        ),
        text=currency_data['amount'],
        textposition='outside',
        texttemplate='%{text:,.0f}',
        customdata=currency_data['id'],
        hovertemplate='<b>%{y}</b><br>Volume: %{x:,.0f}<br>Transactions: %{customdata:,}<extra></extra>'
    ))
    
    fig.update_layout(
        title=dict(
            text='Volume by Currency (Original)',
            font=dict(size=16, weight=600, color='#374151')
        ),
        xaxis_title='',
        yaxis_title='',
        height=350,
        margin=dict(l=60, r=100, t=60, b=40),  # Margen derecho aumentado
        template='plotly_white',
        font=dict(family='Inter, sans-serif', size=12),
        showlegend=False,
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)'
    )
    
    fig.update_xaxes(showgrid=True, gridcolor='#f3f4f6', zeroline=False)
    fig.update_yaxes(showgrid=False)
    
    return fig


def render_transaction_table_card(df):
    """Tabla de transacciones en tarjeta."""
    st.markdown('<div class="card">', unsafe_allow_html=True)
    
    st.markdown("### Recent Transactions")
    st.markdown('<p class="caption-text">Last 50 transactions with amounts normalized to USD</p>', unsafe_allow_html=True)
    
    display_df = df.head(50).copy()
    
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
        "client_device": st.column_config.TextColumn(
            "Device",
            width="small"
        )
    }
    
    columns = ['timestamp', 'amount', 'currency', 'amount_usd', 'status', 'client_device']
    
    st.dataframe(
        display_df[columns],
        column_config=column_config,
        use_container_width=True,
        height=400,
        hide_index=True
    )
    
    st.markdown('</div>', unsafe_allow_html=True)

# ==================== MAIN ====================

def main():
    """Aplicación principal."""
    
    # Header
    col1, col2 = st.columns([3, 1])
    
    with col1:
        st.title("Financial Intelligence")
        st.markdown('<p class="caption-text">Real-time transaction analytics with USD normalization</p>', unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Cargar datos
    with st.spinner("Loading data..."):
        df = load_data()
    
    # ==================== SIDEBAR ====================
    
    st.sidebar.markdown("### Filters")
    st.sidebar.markdown("---")
    
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
    
    # Export
    csv = df.to_csv(index=False)
    st.sidebar.download_button(
        label="Export to CSV",
        data=csv,
        file_name=f"transactions_{datetime.now().strftime('%Y%m%d')}.csv",
        mime="text/csv"
    )
    
    st.sidebar.markdown("---")
    st.sidebar.markdown("**Exchange Rates**")
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
    
    tab1, tab2, tab3 = st.tabs(["Overview", "Analysis", "Transactions"])
    
    # TAB 1: OVERVIEW
    with tab1:
        # Fila 1: KPIs en Cards
        render_kpis_cards(df_filtered)
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        # Fila 2: Gráficos principales en Cards (2/3 y 1/3)
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.markdown('<div class="card">', unsafe_allow_html=True)
            st.plotly_chart(create_trend_area_chart(df_filtered), use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)
        
        with col2:
            st.markdown('<div class="card">', unsafe_allow_html=True)
            st.plotly_chart(create_status_donut_chart(df_filtered), use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        # Fila 3: Stats adicionales en Cards
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown("### Key Statistics")
        
        col1, col2, col3, col4 = st.columns(4)
        
        # Filtrar valores > 0 para max/min
        valid_amounts = df_filtered[df_filtered['amount_usd'] > 0]['amount_usd']
        
        with col1:
            max_val = valid_amounts.max() if len(valid_amounts) > 0 else 0
            st.metric("Max Transaction", format_currency(max_val))
        
        with col2:
            min_val = valid_amounts.min() if len(valid_amounts) > 0 else 0
            st.metric("Min Transaction", format_currency(min_val))
        
        with col3:
            unique = df_filtered['client_email'].nunique()
            st.metric("Unique Clients", format_number(unique))
        
        with col4:
            mobile_pct = len(df_filtered[df_filtered['client_device'] == 'mobile']) / len(df_filtered) * 100
            st.metric("Mobile Share", f"{mobile_pct:.1f}%")
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    # TAB 2: ANALYSIS
    with tab2:
        # Gráficos de análisis en Cards
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown('<div class="card">', unsafe_allow_html=True)
            st.plotly_chart(create_currency_bar_chart(df_filtered), use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)
        
        with col2:
            st.markdown('<div class="card">', unsafe_allow_html=True)
            
            # Device analysis
            device_data = df_filtered.groupby('client_device').agg({
                'amount_usd': 'sum'
            }).reset_index()
            
            fig = go.Figure(go.Bar(
                x=device_data['client_device'],
                y=device_data['amount_usd'],
                marker=dict(color=['#6366f1', '#10b981']),
                text=device_data['amount_usd'],
                textposition='outside',
                texttemplate='$%{text:,.0f}',
                hovertemplate='<b>%{x}</b><br>Volume: $%{y:,.0f}<extra></extra>'
            ))
            
            fig.update_layout(
                title=dict(
                    text='Volume by Device (USD)',
                    font=dict(size=16, weight=600, color='#374151')
                ),
                xaxis_title='',
                yaxis_title='',
                height=350,
                margin=dict(l=60, r=40, t=60, b=40),
                template='plotly_white',
                font=dict(family='Inter, sans-serif', size=12),
                showlegend=False,
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)'
            )
            
            fig.update_xaxes(showgrid=False)
            fig.update_yaxes(showgrid=True, gridcolor='#f3f4f6', zeroline=False, tickformat='$,.0f')
            
            st.plotly_chart(fig, use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        # Status breakdown table en Card
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown("### Status Breakdown")
        
        status_summary = df_filtered.groupby('status').agg({
            'amount_usd': ['sum', 'mean', 'count']
        }).round(2)
        status_summary.columns = ['Total Volume', 'Average', 'Count']
        status_summary['Total Volume'] = status_summary['Total Volume'].apply(format_currency)
        status_summary['Average'] = status_summary['Average'].apply(format_currency)
        status_summary['Count'] = status_summary['Count'].apply(format_number)
        
        st.dataframe(status_summary, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
    
    # TAB 3: TRANSACTIONS
    with tab3:
        render_transaction_table_card(df_filtered)
    
    # Footer
    st.markdown("---")
    st.markdown(
        f'<p class="caption-text" style="text-align: center;">Last updated: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")} | '
        f'v5.0 Modern SaaS Card UI | PostgreSQL on Railway</p>',
        unsafe_allow_html=True
    )


if __name__ == "__main__":
    main()
