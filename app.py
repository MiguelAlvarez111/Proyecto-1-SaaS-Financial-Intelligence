"""
Financial Intelligence Dashboard v6.0 - UX Enhanced Edition
Professional card-based dashboard with Nielsen Heuristics implementation.

UX Improvements:
- Heuristic 1: Live status indicator, visible timestamps
- Heuristic 3: Reset filters button, quick date filters
- Heuristic 5: Defensive validation, empty state handling
- Heuristic 6: Currency labels with flags
- Heuristic 7: Quick filters, session state persistence
- Heuristic 9: Improved error messages and recovery
- Heuristic 10: Tooltips, help button, contextual guidance
- Accessibility: WCAG 2.1 compliant contrast, ARIA labels, focus states

Author: Senior UI/UX Designer
Date: 2026-01-31
"""

import os
from datetime import datetime, timedelta

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

# Currency display with flags
CURRENCY_DISPLAY = {
    'USD': '🇺🇸 USD - US Dollar',
    'EUR': '🇪🇺 EUR - Euro',
    'GBP': '🇬🇧 GBP - British Pound',
    'COP': '🇨🇴 COP - Colombian Peso'
}

# WCAG 2.1 compliant colors (4.5:1 contrast minimum)
COLOR_PRIMARY = '#6366f1'      # Indigo 500
COLOR_SUCCESS = '#059669'      # Green 600 (darker for contrast)
COLOR_WARNING = '#d97706'      # Amber 600
COLOR_DANGER = '#dc2626'       # Red 600 (darker for contrast)
COLOR_INFO = '#2563eb'         # Blue 600
COLOR_GRAY = '#6b7280'         # Gray 500

STATUS_COLORS = {
    'COMPLETED': COLOR_SUCCESS,
    'FAILED': COLOR_DANGER,
    'PENDING': COLOR_WARNING,
    'REFUNDED': COLOR_INFO
}

# ==================== CSS MODERN CARD UI + ACCESSIBILITY ====================

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
        padding-top: 1.5rem;
        padding-bottom: 2rem;
        padding-left: 3rem;
        padding-right: 3rem;
    }
    
    /* Card Component */
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
    
    /* Card para KPIs */
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
    
    /* Hero KPI (primer KPI más grande) */
    .card-kpi-hero {
        background: linear-gradient(135deg, #6366f1 0%, #4f46e5 100%);
        border: none;
        color: white;
        min-height: 140px;
    }
    
    .card-kpi-hero [data-testid="stMetricValue"] {
        color: white !important;
        font-size: 40px !important;
    }
    
    .card-kpi-hero [data-testid="stMetricLabel"] {
        color: rgba(255, 255, 255, 0.9) !important;
    }
    
    .card-kpi-hero [data-testid="stMetricDelta"] {
        color: rgba(255, 255, 255, 0.8) !important;
    }
    
    /* Live Status Indicator */
    .live-indicator {
        display: flex;
        align-items: center;
        gap: 8px;
        padding: 8px 16px;
        background: #f0fdf4;
        border: 1px solid #86efac;
        border-radius: 20px;
        font-size: 12px;
        color: #166534;
        font-weight: 500;
    }
    
    .live-dot {
        width: 8px;
        height: 8px;
        background: #22c55e;
        border-radius: 50%;
        animation: pulse 2s infinite;
    }
    
    @keyframes pulse {
        0%, 100% { opacity: 1; }
        50% { opacity: 0.5; }
    }
    
    /* Help Button */
    .help-button {
        position: fixed;
        bottom: 24px;
        right: 24px;
        width: 56px;
        height: 56px;
        background: #6366f1;
        color: white;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
        cursor: pointer;
        font-size: 24px;
        z-index: 1000;
        transition: transform 0.2s;
    }
    
    .help-button:hover {
        transform: scale(1.1);
        box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05);
    }
    
    /* Typography */
    h1 {
        font-size: 32px;
        font-weight: 700;
        color: #111827;
        letter-spacing: -0.5px;
        margin-bottom: 4px;
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
    
    /* Focus States - WCAG 2.1 Accessibility */
    button:focus,
    .stMultiSelect:focus-within,
    .stDateInput:focus-within,
    .stSelectbox:focus-within {
        outline: 2px solid #3b82f6 !important;
        outline-offset: 2px !important;
        box-shadow: 0 0 0 4px rgba(59, 130, 246, 0.1) !important;
    }
    
    /* MultiSelect */
    .stMultiSelect [data-baseweb="select"] {
        border-radius: 8px;
        border-color: #e5e7eb;
    }
    
    /* Warning/Error boxes */
    .stAlert {
        border-radius: 8px;
        border-left: 4px solid;
    }
    
    /* Caption styling */
    .caption-text {
        font-size: 13px;
        color: #6b7280;
        margin-top: 8px;
    }
    
    /* Empty State */
    .empty-state {
        text-align: center;
        padding: 48px 24px;
        background: #f9fafb;
        border: 2px dashed #e5e7eb;
        border-radius: 12px;
        margin: 24px 0;
    }
    
    .empty-state-icon {
        font-size: 64px;
        margin-bottom: 16px;
        opacity: 0.5;
    }
    
    .empty-state-title {
        font-size: 18px;
        font-weight: 600;
        color: #111827;
        margin-bottom: 8px;
    }
    
    .empty-state-text {
        font-size: 14px;
        color: #6b7280;
        margin-bottom: 24px;
    }
    </style>
    """, unsafe_allow_html=True)

# ==================== SESSION STATE INITIALIZATION ====================

if 'filters' not in st.session_state:
    st.session_state.filters = {
        'currencies': None,  # Will be set to all on first load
        'statuses': None,
        'date_range': None,
        'quick_filter': 'All Time'
    }

if 'show_help' not in st.session_state:
    st.session_state.show_help = False

if 'last_refresh' not in st.session_state:
    st.session_state.last_refresh = datetime.now()

# ==================== CONEXIÓN ====================

@st.cache_resource
def init_connection():
    """Inicializa conexión a PostgreSQL con error handling mejorado."""
    database_url = os.getenv('DATABASE_URL')
    if not database_url:
        st.error("""
        ### ⚠️ Configuration Error
        
        **DATABASE_URL** not found in environment variables.
        
        **To fix this:**
        1. Create a `.env` file in the project root
        2. Add your PostgreSQL connection string:
           ```
           DATABASE_URL=postgresql://user:password@host:port/database
           ```
        3. Restart the dashboard
        
        **Need help?** [View Documentation](https://github.com/...)
        """)
        st.stop()
    
    try:
        engine = create_engine(database_url, pool_pre_ping=True, pool_size=10, max_overflow=20)
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        return engine
    except Exception as e:
        st.error(f"""
        ### ⚠️ Database Connection Failed
        
        We couldn't connect to PostgreSQL. Please verify:
        
        1. **Database is running**: Check your Railway/PostgreSQL service
        2. **Credentials are correct**: Verify DATABASE_URL in `.env`
        3. **Network access**: Ensure firewall allows connections
        
        **Error details:**
        ```
        {str(e)}
        ```
        
        **Need help?** Contact support or check the logs.
        """)
        st.stop()


@st.cache_data(ttl=300)
def load_data():
    """Carga y transforma datos con validación mejorada."""
    engine = init_connection()
    
    query = """
    SELECT id, timestamp, amount, currency, status,
           client_email, client_ip, client_device, metadata
    FROM transactions
    ORDER BY timestamp DESC
    """
    
    try:
        df = pd.read_sql(query, engine)
        
        # Validación de datos vacíos
        if len(df) == 0:
            return pd.DataFrame()  # Return empty DataFrame
        
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        
        # Vectorización
        df['amount_usd'] = df['amount'] * df['currency'].map(EXCHANGE_RATES).fillna(1.0)
        
        # Temporal
        df['date'] = df['timestamp'].dt.date
        df['year_month'] = df['timestamp'].dt.to_period('M').astype(str)
        df['week'] = df['timestamp'].dt.to_period('W').astype(str)
        df['day_of_week'] = df['timestamp'].dt.day_name()
        df['hour'] = df['timestamp'].dt.hour
        
        # Update last refresh
        st.session_state.last_refresh = datetime.now()
        
        return df
    except Exception as e:
        st.error(f"""
        ### ⚠️ Data Loading Failed
        
        We couldn't load data from the database.
        
        **Error details:**
        ```
        {str(e)}
        ```
        
        **Possible solutions:**
        - Check if the `transactions` table exists
        - Verify data types are correct
        - Try running the ETL pipeline again: `python3 etl_pipeline.py`
        """)
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
    """Calcula delta robusto con manejo de errores."""
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


def get_time_ago(dt):
    """Convierte datetime a formato 'time ago'."""
    now = datetime.now()
    diff = now - dt
    
    if diff.seconds < 60:
        return f"{diff.seconds}s ago"
    elif diff.seconds < 3600:
        return f"{diff.seconds // 60}m ago"
    elif diff.seconds < 86400:
        return f"{diff.seconds // 3600}h ago"
    else:
        return f"{diff.days}d ago"


def apply_quick_filter(df, filter_type):
    """Aplica filtros rápidos de fecha."""
    now = pd.Timestamp.now()
    
    if filter_type == "Last 7 Days":
        start_date = (now - pd.Timedelta(days=7)).date()
        return df[df['date'] >= start_date]
    elif filter_type == "Last 30 Days":
        start_date = (now - pd.Timedelta(days=30)).date()
        return df[df['date'] >= start_date]
    elif filter_type == "This Month":
        start_date = now.replace(day=1).date()
        return df[df['date'] >= start_date]
    elif filter_type == "Last Month":
        last_month = now.replace(day=1) - pd.Timedelta(days=1)
        start_date = last_month.replace(day=1).date()
        end_date = last_month.date()
        return df[(df['date'] >= start_date) & (df['date'] <= end_date)]
    else:  # "All Time"
        return df

# ==================== COMPONENTES UI ====================

def render_empty_state():
    """Renderiza estado vacío cuando no hay datos."""
    st.markdown("""
    <div class="empty-state">
        <div class="empty-state-icon">📊</div>
        <div class="empty-state-title">No Transactions Found</div>
        <div class="empty-state-text">
            The transactions table is empty or no data matches your filters.
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    with st.expander("🚀 Get Started"):
        st.markdown("""
        **To populate the dashboard with data:**
        
        1. **Generate sample data:**
           ```bash
           python3 generate_data.py
           ```
        
        2. **Run the ETL pipeline:**
           ```bash
           python3 etl_pipeline.py
           ```
        
        3. **Refresh this page**
        
        **Need help?** Check the [Documentation](https://github.com/...)
        """)


def render_header(df):
    """Renderiza header con live status."""
    col1, col2, col3 = st.columns([3, 2, 1])
    
    with col1:
        st.title("Financial Intelligence")
        st.markdown('<p class="caption-text">Real-time transaction analytics with USD normalization</p>', unsafe_allow_html=True)
    
    with col2:
        # Live status indicator
        time_ago = get_time_ago(st.session_state.last_refresh)
        st.markdown(f"""
        <div class="live-indicator">
            <div class="live-dot"></div>
            <span>Live • Updated {time_ago}</span>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        # Help button
        if st.button("❓ Help", use_container_width=True):
            st.session_state.show_help = not st.session_state.show_help
    
    # Help modal
    if st.session_state.show_help:
        st.info("""
        ### 📖 Quick Guide
        
        **Filters:**
        - Use the sidebar to filter by currency, status, and date
        - Try Quick Filters for common date ranges
        - Click "Reset Filters" to start over
        
        **Metrics:**
        - All volumes are normalized to USD using fixed exchange rates
        - Deltas show month-over-month comparison
        - Hover over metrics for detailed explanations
        
        **Export:**
        - Download filtered data as CSV from the sidebar
        
        **Need more help?** [View Full Documentation](https://github.com/...)
        """)


def render_kpis_hero(df):
    """Renderiza KPIs con hero metric."""
    if len(df) == 0:
        return
    
    col1, col2, col3, col4 = st.columns([2, 1, 1, 1])
    
    # HERO KPI: Total Volume (más grande y destacado)
    volume = df['amount_usd'].sum()
    delta_vol = calculate_delta(df)
    
    with col1:
        st.markdown('<div class="card-kpi-hero">', unsafe_allow_html=True)
        st.metric(
            label="Total Volume",
            value=format_currency(volume),
            delta=f"{delta_vol:+.1f}% MoM" if delta_vol != 0 else None,
            help="💡 Total transaction volume in USD. Uses fixed exchange rates: EUR=1.08, GBP=1.27, COP=0.00025"
        )
        st.markdown('</div>', unsafe_allow_html=True)
    
    # KPI 2: Total Transactions
    total = len(df)
    delta_txn = calculate_delta(
        df.groupby('year_month').size().reset_index(name='count').assign(amount_usd=lambda x: x['count'])
    )
    
    with col2:
        st.markdown('<div class="card-kpi">', unsafe_allow_html=True)
        st.metric(
            label="Transactions",
            value=format_number(total),
            delta=f"{delta_txn:+.1f}% MoM" if delta_txn != 0 else None,
            help="Total number of transactions in the selected period"
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
            label="Avg Ticket",
            value=format_currency(avg),
            delta=f"{delta_avg:+.1f}% MoM" if delta_avg != 0 else None,
            help="Average transaction amount (mean) in USD"
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
            delta=f"{completed:,} successful",
            help="Percentage of completed transactions vs total"
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
        height=350,
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
    status_data = status_data.sort_values('count', ascending=False)
    
    colors = [STATUS_COLORS.get(s, COLOR_GRAY) for s in status_data['status']]
    
    fig = go.Figure(go.Pie(
        labels=status_data['status'],
        values=status_data['count'],
        hole=0.6,
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
        height=350,
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
        margin=dict(l=60, r=100, t=60, b=40),
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
    """Aplicación principal con UX mejorado."""
    
    # Cargar datos
    with st.spinner("Loading data..."):
        df = load_data()
    
    # Empty state
    if len(df) == 0:
        render_empty_state()
        return
    
    # ==================== SIDEBAR CON MEJORAS UX ====================
    
    st.sidebar.markdown("### Filters")
    
    # Quick Filters y Reset en fila
    col1, col2 = st.sidebar.columns(2)
    
    with col1:
        if st.button("🔄 Reset", use_container_width=True, help="Clear all filters"):
            st.session_state.filters = {
                'currencies': None,
                'statuses': None,
                'date_range': None,
                'quick_filter': 'All Time'
            }
            st.rerun()
    
    with col2:
        quick_filter = st.selectbox(
            "Quick",
            ["All Time", "Last 7 Days", "Last 30 Days", "This Month", "Last Month"],
            index=["All Time", "Last 7 Days", "Last 30 Days", "This Month", "Last Month"].index(
                st.session_state.filters.get('quick_filter', 'All Time')
            ),
            help="Quick date range filters"
        )
        st.session_state.filters['quick_filter'] = quick_filter
    
    st.sidebar.markdown("---")
    
    # Currency filter con flags
    all_currencies = sorted(df['currency'].unique())
    
    # Initialize default if not set
    if st.session_state.filters['currencies'] is None:
        st.session_state.filters['currencies'] = all_currencies
    
    selected_currencies = st.sidebar.multiselect(
        "Currency",
        options=all_currencies,
        default=st.session_state.filters['currencies'],
        format_func=lambda x: CURRENCY_DISPLAY.get(x, x),
        help="Filter by transaction currency"
    )
    
    # Validación: al menos una moneda
    if len(selected_currencies) == 0:
        st.sidebar.error("⚠️ Please select at least one currency")
        selected_currencies = all_currencies
    
    st.session_state.filters['currencies'] = selected_currencies
    
    # Status filter
    all_statuses = sorted(df['status'].unique())
    
    if st.session_state.filters['statuses'] is None:
        st.session_state.filters['statuses'] = all_statuses
    
    selected_statuses = st.sidebar.multiselect(
        "Status",
        options=all_statuses,
        default=st.session_state.filters['statuses'],
        help="Filter by transaction status"
    )
    
    if len(selected_statuses) == 0:
        st.sidebar.error("⚠️ Please select at least one status")
        selected_statuses = all_statuses
    
    st.session_state.filters['statuses'] = selected_statuses
    
    st.sidebar.markdown("---")
    
    # Date range filter
    date_range = st.sidebar.date_input(
        "Date Range",
        value=(df['timestamp'].min().date(), df['timestamp'].max().date()),
        min_value=df['timestamp'].min().date(),
        max_value=df['timestamp'].max().date(),
        help="Filter by date range"
    )
    
    st.sidebar.markdown("---")
    
    # ==================== APLICAR FILTROS ====================
    
    df_filtered = df.copy()
    
    # Apply quick filter first
    if quick_filter != "All Time":
        df_filtered = apply_quick_filter(df_filtered, quick_filter)
    
    # Then apply manual filters
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
    
    # Mostrar resumen de filtros
    st.sidebar.markdown("---")
    st.sidebar.metric("Filtered Records", format_number(len(df_filtered)))
    st.sidebar.caption(f"Total available: {format_number(len(df))}")
    
    # Export button
    st.sidebar.markdown("---")
    csv = df_filtered.to_csv(index=False)
    st.sidebar.download_button(
        label="📥 Export to CSV",
        data=csv,
        file_name=f"transactions_{datetime.now().strftime('%Y%m%d')}.csv",
        mime="text/csv",
        use_container_width=True
    )
    
    st.sidebar.markdown("---")
    st.sidebar.markdown("**Exchange Rates**")
    st.sidebar.caption("USD: 1.00 | EUR: 1.08")
    st.sidebar.caption("GBP: 1.27 | COP: 0.00025")
    
    # ==================== VALIDACIÓN DE DATOS FILTRADOS ====================
    
    if len(df_filtered) == 0:
        st.warning("""
        ### ⚠️ No Data Matches Your Filters
        
        Try adjusting:
        - **Date range**: Select a wider period
        - **Currency**: Include more currencies
        - **Status**: Select different statuses
        """)
        
        if st.button("🔄 Reset All Filters", type="primary"):
            st.session_state.filters = {
                'currencies': all_currencies,
                'statuses': all_statuses,
                'date_range': None,
                'quick_filter': 'All Time'
            }
            st.rerun()
        
        return
    
    # ==================== HEADER ====================
    
    render_header(df_filtered)
    
    st.markdown("---")
    
    # ==================== TABS ====================
    
    tab1, tab2, tab3 = st.tabs(["Overview", "Analysis", "Transactions"])
    
    # TAB 1: OVERVIEW
    with tab1:
        # Fila 1: KPIs con Hero metric
        render_kpis_hero(df_filtered)
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        # Fila 2: Gráficos principales en Cards (2/3 y 1/3)
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.markdown('<div class="card">', unsafe_allow_html=True)
            st.plotly_chart(create_trend_area_chart(df_filtered), use_container_width=True, key='trend_overview')
            st.markdown('</div>', unsafe_allow_html=True)
        
        with col2:
            st.markdown('<div class="card">', unsafe_allow_html=True)
            st.plotly_chart(create_status_donut_chart(df_filtered), use_container_width=True, key='donut_overview')
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
            st.plotly_chart(create_currency_bar_chart(df_filtered), use_container_width=True, key='currency_analysis')
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
            
            st.plotly_chart(fig, use_container_width=True, key='device_analysis')
            st.markdown('</div>', unsafe_allow_html=True)
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        # Status breakdown table en Card
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown("### Status Breakdown")
        
        status_summary = df_filtered.groupby('status').agg({
            'amount_usd': ['sum', 'mean', 'count']
        }).round(2)
        status_summary.columns = ['Total Volume', 'Average', 'Count']
        status_summary = status_summary.sort_values('Total Volume', ascending=False)
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
        f'<p class="caption-text" style="text-align: center;">v6.0 UX Enhanced Edition | '
        f'PostgreSQL on Railway | Last updated: {st.session_state.last_refresh.strftime("%Y-%m-%d %H:%M:%S")}</p>',
        unsafe_allow_html=True
    )


if __name__ == "__main__":
    main()
