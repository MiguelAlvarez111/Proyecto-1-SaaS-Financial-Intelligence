"""
Financial Intelligence Dashboard v6.1 - Layout Fixed
Professional card-based dashboard with corrected Streamlit layout.

CRITICAL FIX: Removed HTML div wrappers that were breaking Streamlit layout.
Now uses native Streamlit containers with CSS styling only.

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

# WCAG 2.1 compliant colors
COLOR_PRIMARY = '#6366f1'
COLOR_SUCCESS = '#059669'
COLOR_WARNING = '#d97706'
COLOR_DANGER = '#dc2626'
COLOR_INFO = '#2563eb'
COLOR_GRAY = '#6b7280'

STATUS_COLORS = {
    'COMPLETED': COLOR_SUCCESS,
    'FAILED': COLOR_DANGER,
    'PENDING': COLOR_WARNING,
    'REFUNDED': COLOR_INFO
}

# ==================== CSS FIXED LAYOUT ====================

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
        padding-top: 3rem;
        padding-bottom: 2rem;
        padding-left: 3rem;
        padding-right: 3rem;
    }
    
    /* FIXED: Use Streamlit containers with background instead of wrapping divs */
    [data-testid="stVerticalBlock"] > [data-testid="stVerticalBlock"] {
        background-color: #ffffff;
        border: 1px solid #e2e8f0;
        border-radius: 12px;
        padding: 24px;
        box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.1), 0 1px 2px 0 rgba(0, 0, 0, 0.06);
        margin-bottom: 20px;
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
    
    /* Metrics */
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
    
    /* Focus States - WCAG 2.1 */
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
    
    /* Caption styling */
    .caption-text {
        font-size: 13px;
        color: #6b7280;
        margin-top: 8px;
    }
    
    /* Live indicator badge */
    .live-badge {
        display: inline-flex;
        align-items: center;
        gap: 8px;
        padding: 8px 16px;
        background: #f0fdf4;
        border: 1px solid #86efac;
        border-radius: 20px;
        font-size: 12px;
        color: #166534;
        font-weight: 500;
        margin-top: 4px;
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
    </style>
    """, unsafe_allow_html=True)

# ==================== SESSION STATE ====================

if 'filters' not in st.session_state:
    st.session_state.filters = {
        'currencies': None,
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
    """Inicializa conexión a PostgreSQL."""
    database_url = os.getenv('DATABASE_URL')
    if not database_url:
        st.error("""
        ### ⚠️ Configuration Error
        
        **DATABASE_URL** not found. Please:
        1. Create a `.env` file
        2. Add: `DATABASE_URL=postgresql://...`
        3. Restart the dashboard
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
        
        **Error:** {str(e)}
        
        **Solutions:**
        1. Check database is running
        2. Verify DATABASE_URL credentials
        3. Check network/firewall settings
        """)
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
        
        if len(df) == 0:
            return pd.DataFrame()
        
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        df['amount_usd'] = df['amount'] * df['currency'].map(EXCHANGE_RATES).fillna(1.0)
        df['date'] = df['timestamp'].dt.date
        df['year_month'] = df['timestamp'].dt.to_period('M').astype(str)
        df['week'] = df['timestamp'].dt.to_period('W').astype(str)
        df['day_of_week'] = df['timestamp'].dt.day_name()
        df['hour'] = df['timestamp'].dt.hour
        
        st.session_state.last_refresh = datetime.now()
        return df
    except Exception as e:
        st.error(f"""
        ### ⚠️ Data Loading Failed
        
        **Error:** {str(e)}
        
        Try running: `python3 etl_pipeline.py`
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


def get_time_ago(dt):
    """Convierte datetime a 'time ago'."""
    now = datetime.now()
    diff = now - dt
    
    total_seconds = int(diff.total_seconds())
    
    if total_seconds < 60:
        return f"{total_seconds}s ago"
    elif total_seconds < 3600:
        return f"{total_seconds // 60}m ago"
    elif total_seconds < 86400:
        return f"{total_seconds // 3600}h ago"
    else:
        return f"{diff.days}d ago"


def apply_quick_filter(df, filter_type):
    """Aplica filtros rápidos."""
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
    else:
        return df

# ==================== COMPONENTES UI ====================

def render_empty_state():
    """Estado vacío."""
    st.warning("""
    ### 📊 No Transactions Found
    
    The transactions table is empty.
    
    **To get started:**
    1. Run: `python3 generate_data.py`
    2. Run: `python3 etl_pipeline.py`
    3. Refresh this page
    """)


def create_trend_area_chart(df):
    """Gráfico de área con gradiente."""
    daily = df.groupby('date').agg({
        'amount_usd': 'sum',
        'id': 'count'
    }).reset_index()
    
    fig = go.Figure()
    
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
    fig.update_yaxes(showgrid=True, gridcolor='#f3f4f6', zeroline=False, tickformat='$,.0f')
    
    return fig


def create_status_donut_chart(df):
    """Donut chart para status."""
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
    """Gráfico de barras por moneda."""
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

# ==================== MAIN ====================

def main():
    """Aplicación principal."""
    
    # Cargar datos
    with st.spinner("Loading data..."):
        df = load_data()
    
    if len(df) == 0:
        render_empty_state()
        return
    
    # ==================== HEADER ====================
    
    # Add spacing at top
    st.markdown("<br>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([5, 3, 2])
    
    with col1:
        st.title("Financial Intelligence")
        st.caption("Real-time transaction analytics with USD normalization")
    
    with col2:
        st.markdown("<br>", unsafe_allow_html=True)
        time_ago = get_time_ago(st.session_state.last_refresh)
        st.markdown(f"""
        <div class="live-badge">
            <div class="live-dot"></div>
            <span>Live • Updated {time_ago}</span>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("❓ Help", use_container_width=True):
            st.session_state.show_help = not st.session_state.show_help
    
    if st.session_state.show_help:
        st.info("""
        **Quick Guide:**
        - Use sidebar filters to explore data
        - All volumes normalized to USD
        - Export data with CSV button
        - Reset filters anytime
        """)
    
    st.divider()
    
    # ==================== SIDEBAR ====================
    
    st.sidebar.markdown("### Filters")
    
    col1, col2 = st.sidebar.columns(2)
    
    with col1:
        if st.button("🔄 Reset", use_container_width=True):
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
            index=0
        )
    
    st.sidebar.divider()
    
    # Currency filter
    all_currencies = sorted(df['currency'].unique())
    
    if st.session_state.filters['currencies'] is None:
        st.session_state.filters['currencies'] = all_currencies
    
    selected_currencies = st.sidebar.multiselect(
        "Currency",
        options=all_currencies,
        default=st.session_state.filters['currencies'],
        format_func=lambda x: CURRENCY_DISPLAY.get(x, x)
    )
    
    if len(selected_currencies) == 0:
        st.sidebar.error("⚠️ Select at least one currency")
        selected_currencies = all_currencies
    
    # Status filter
    all_statuses = sorted(df['status'].unique())
    
    if st.session_state.filters['statuses'] is None:
        st.session_state.filters['statuses'] = all_statuses
    
    selected_statuses = st.sidebar.multiselect(
        "Status",
        options=all_statuses,
        default=st.session_state.filters['statuses']
    )
    
    if len(selected_statuses) == 0:
        st.sidebar.error("⚠️ Select at least one status")
        selected_statuses = all_statuses
    
    st.sidebar.divider()
    
    # Date range
    date_range = st.sidebar.date_input(
        "Date Range",
        value=(df['timestamp'].min().date(), df['timestamp'].max().date()),
        min_value=df['timestamp'].min().date(),
        max_value=df['timestamp'].max().date()
    )
    
    st.sidebar.divider()
    
    # ==================== APLICAR FILTROS ====================
    
    df_filtered = df.copy()
    
    if quick_filter != "All Time":
        df_filtered = apply_quick_filter(df_filtered, quick_filter)
    
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
    
    st.sidebar.metric("Filtered Records", format_number(len(df_filtered)))
    st.sidebar.caption(f"Total: {format_number(len(df))}")
    
    st.sidebar.divider()
    
    # Export
    csv = df_filtered.to_csv(index=False)
    st.sidebar.download_button(
        label="📥 Export CSV",
        data=csv,
        file_name=f"transactions_{datetime.now().strftime('%Y%m%d')}.csv",
        mime="text/csv",
        use_container_width=True
    )
    
    st.sidebar.divider()
    st.sidebar.caption("**Exchange Rates**")
    st.sidebar.caption("USD: 1.00 | EUR: 1.08")
    st.sidebar.caption("GBP: 1.27 | COP: 0.00025")
    
    # ==================== VALIDACIÓN ====================
    
    if len(df_filtered) == 0:
        st.warning("""
        ### ⚠️ No Data Matches Your Filters
        
        Try adjusting your date range, currency, or status filters.
        """)
        if st.button("🔄 Reset All Filters"):
            st.session_state.filters = {
                'currencies': all_currencies,
                'statuses': all_statuses,
                'date_range': None,
                'quick_filter': 'All Time'
            }
            st.rerun()
        return
    
    # ==================== TABS ====================
    
    tab1, tab2, tab3 = st.tabs(["Overview", "Analysis", "Transactions"])
    
    # TAB 1: OVERVIEW
    with tab1:
        # KPIs Row
        col1, col2, col3, col4 = st.columns(4)
        
        # KPI 1: Total Volume
        volume = df_filtered['amount_usd'].sum()
        delta_vol = calculate_delta(df_filtered)
        
        with col1:
            st.metric(
                label="Total Volume",
                value=format_currency(volume),
                delta=f"{delta_vol:+.1f}% MoM" if delta_vol != 0 else None,
                help="Total transaction volume in USD"
            )
        
        # KPI 2: Transactions
        total = len(df_filtered)
        delta_txn = calculate_delta(
            df_filtered.groupby('year_month').size().reset_index(name='count').assign(amount_usd=lambda x: x['count'])
        )
        
        with col2:
            st.metric(
                label="Transactions",
                value=format_number(total),
                delta=f"{delta_txn:+.1f}% MoM" if delta_txn != 0 else None,
                help="Total number of transactions"
            )
        
        # KPI 3: Avg Ticket
        avg = df_filtered['amount_usd'].mean()
        try:
            periods = sorted(df_filtered['year_month'].unique())
            if len(periods) >= 2:
                curr_avg = df_filtered[df_filtered['year_month'] == periods[-1]]['amount_usd'].mean()
                prev_avg = df_filtered[df_filtered['year_month'] == periods[-2]]['amount_usd'].mean()
                delta_avg = ((curr_avg - prev_avg) / prev_avg * 100) if prev_avg > 0 else 0
            else:
                delta_avg = 0
        except:
            delta_avg = 0
        
        with col3:
            st.metric(
                label="Avg Ticket",
                value=format_currency(avg),
                delta=f"{delta_avg:+.1f}% MoM" if delta_avg != 0 else None,
                help="Average transaction amount"
            )
        
        # KPI 4: Success Rate
        completed = len(df_filtered[df_filtered['status'] == 'COMPLETED'])
        success_rate = (completed / len(df_filtered) * 100) if len(df_filtered) > 0 else 0
        
        with col4:
            st.metric(
                label="Success Rate",
                value=f"{success_rate:.1f}%",
                delta=f"{completed:,} successful",
                help="Percentage of completed transactions"
            )
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        # Charts Row
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.plotly_chart(create_trend_area_chart(df_filtered), use_container_width=True)
        
        with col2:
            st.plotly_chart(create_status_donut_chart(df_filtered), use_container_width=True)
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        # Stats Row
        st.markdown("### Key Statistics")
        
        col1, col2, col3, col4 = st.columns(4)
        
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
    
    # TAB 2: ANALYSIS
    with tab2:
        col1, col2 = st.columns(2)
        
        with col1:
            st.plotly_chart(create_currency_bar_chart(df_filtered), use_container_width=True)
        
        with col2:
            device_data = df_filtered.groupby('client_device').agg({
                'amount_usd': 'sum'
            }).reset_index()
            device_data = device_data.sort_values('amount_usd', ascending=True)
            
            fig = go.Figure(go.Bar(
                x=device_data['amount_usd'],
                y=device_data['client_device'],
                orientation='h',
                marker=dict(color=['#10b981', '#6366f1']),
                text=device_data['amount_usd'],
                textposition='outside',
                texttemplate='$%{text:,.0f}',
                hovertemplate='<b>%{y}</b><br>Volume: $%{x:,.0f}<extra></extra>'
            ))
            
            fig.update_layout(
                title=dict(
                    text='Volume by Device (USD)',
                    font=dict(size=16, weight=600, color='#374151')
                ),
                xaxis_title='',
                yaxis_title='',
                height=350,
                margin=dict(l=80, r=100, t=60, b=40),
                template='plotly_white',
                font=dict(family='Inter, sans-serif', size=12),
                showlegend=False,
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)'
            )
            
            fig.update_xaxes(showgrid=True, gridcolor='#f3f4f6', zeroline=False, tickformat='$,.0f')
            fig.update_yaxes(showgrid=False)
            
            st.plotly_chart(fig, use_container_width=True)
        
        st.markdown("<br>", unsafe_allow_html=True)
        
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
    
    # TAB 3: TRANSACTIONS
    with tab3:
        st.markdown("### Recent Transactions")
        st.caption("Last 50 transactions with amounts normalized to USD")
        
        display_df = df_filtered.head(50).copy()
        
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
    
    # Footer
    st.divider()
    st.caption(
        f"v6.1 Layout Fixed | PostgreSQL on Railway | "
        f"Last updated: {st.session_state.last_refresh.strftime('%Y-%m-%d %H:%M:%S')}"
    )


if __name__ == "__main__":
    main()
