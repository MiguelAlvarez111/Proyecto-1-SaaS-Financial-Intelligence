# PROJECT CONTEXT — SaaS Financial Intelligence

Documento para revisión de arquitectura. Código fuente: .py, requirements.txt, .toml, .sh.
Excluidos: .json, .csv, .env, __pycache__, .git, venv.

---

## Estructura del Proyecto (File Tree)

```
Proyecto 1- SaaS Financial Intelligence/
├── .streamlit
│   └── config.toml
├── backend
│   ├── main.py
│   └── requirements.txt
├── frontend
│   ├── public
│   │   ├── file.svg
│   │   ├── globe.svg
│   │   ├── next.svg
│   │   ├── vercel.svg
│   │   └── window.svg
│   ├── src
│   │   ├── app
│   │   │   ├── favicon.ico
│   │   │   ├── globals.css
│   │   │   ├── layout.tsx
│   │   │   └── page.tsx
│   │   ├── components
│   │   │   ├── charts
│   │   │   │   ├── AreaChartComponent.tsx
│   │   │   │   ├── DonutChart.tsx
│   │   │   │   └── HorizontalBarChart.tsx
│   │   │   ├── layout
│   │   │   │   ├── Header.tsx
│   │   │   │   └── Sidebar.tsx
│   │   │   └── ui
│   │   │       ├── MetricCard.tsx
│   │   │       └── TransactionTable.tsx
│   │   ├── hooks
│   │   │   └── useDashboard.ts
│   │   ├── lib
│   │   │   └── utils.ts
│   │   └── types
│   │       └── index.ts
│   ├── .gitignore
│   ├── eslint.config.mjs
│   ├── next-env.d.ts
│   ├── next.config.ts
│   ├── package-lock.json
│   ├── package.json
│   ├── postcss.config.mjs
│   ├── README.md
│   ├── tailwind.config.ts
│   └── tsconfig.json
├── .gitignore
├── app.py
├── build_project_context.py
├── DASHBOARD_GUIDE.md
├── etl_pipeline.py
├── generate_data.py
├── PROJECT_CONTEXT.md
├── raw_transactions.json
├── README.md
├── requirements.txt
├── run_dashboard.sh
├── test_etl_transformations.py
├── transformed_sample.json
└── verify_database.py
```

---

## Nombre del Archivo: .streamlit/config.toml

```toml
[theme]
# Color principal (Indigo - matches app.py COLOR_PRIMARY)
primaryColor = "#6366f1"

# Color de fondo
backgroundColor = "#ffffff"

# Color de fondo secundario
secondaryBackgroundColor = "#f0f2f6"

# Color del texto
textColor = "#262730"

# Fuente
font = "sans serif"

[server]
# Puerto por defecto
port = 8501

# Habilitar CORS
enableCORS = false

# Habilitar XSRF protection
enableXsrfProtection = true

[browser]
# Abrir automáticamente el navegador
gatherUsageStats = false
```

## Nombre del Archivo: app.py

```python
"""
Financial Intelligence Dashboard v5.0 - Gold Master
Professional card-based dashboard with Glass & Cards architecture.

AUDIT FIXES APPLIED:
- Data Integrity: Filters transactions with amount <= 0.01
- Defensive try/except in calculate_delta
- Custom HTML metric cards for consistent alignment
- Plotly margins fixed to prevent text cutoff
- All emojis removed for professional aesthetic
- Donut chart for status distribution

Author: Senior Full Stack Engineer & Lead Product Designer
Date: 2026-01-31
"""

import os
from datetime import datetime, timedelta

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from dotenv import load_dotenv
from sqlalchemy import create_engine, text

# ==================== CONFIGURATION ====================

st.set_page_config(
    page_title="Financial Intelligence",
    page_icon="chart_with_upwards_trend",
    layout="wide",
    initial_sidebar_state="expanded"
)

load_dotenv()

# ==================== CONSTANTS ====================

EXCHANGE_RATES = {
    'USD': 1.0,
    'EUR': 1.08,
    'GBP': 1.27,
    'COP': 0.00025
}

CURRENCY_DISPLAY = {
    'USD': 'USD - US Dollar',
    'EUR': 'EUR - Euro',
    'GBP': 'GBP - British Pound',
    'COP': 'COP - Colombian Peso'
}

# WCAG 2.1 compliant color palette
COLOR_PRIMARY = '#6366f1'
COLOR_SUCCESS = '#059669'
COLOR_WARNING = '#d97706'
COLOR_DANGER = '#dc2626'
COLOR_INFO = '#2563eb'
COLOR_GRAY = '#6b7280'
COLOR_TEXT_PRIMARY = '#1e293b'
COLOR_TEXT_SECONDARY = '#64748b'
COLOR_BACKGROUND = '#f8fafc'
COLOR_CARD = '#ffffff'
COLOR_BORDER = '#e2e8f0'

STATUS_COLORS = {
    'COMPLETED': COLOR_SUCCESS,
    'FAILED': COLOR_DANGER,
    'PENDING': COLOR_WARNING,
    'REFUNDED': COLOR_INFO
}

# Chart configuration (8px grid system)
CHART_HEIGHT = 350
CHART_MARGIN = dict(l=20, r=30, t=60, b=30)
CHART_MARGIN_BAR = dict(l=70, r=120, t=60, b=30)  # Extra right margin for labels

# Data integrity threshold
MIN_VALID_AMOUNT = 0.01

# ==================== GLASS & CARDS CSS ====================

st.markdown("""
<style>
/* ===== GOOGLE FONTS ===== */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

/* ===== GLOBAL RESET ===== */
html, body, [class*="css"] {
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
    font-size: 14px;
    color: #1e293b;
}

/* ===== APP BACKGROUND ===== */
.main {
    background-color: #f8fafc;
}

.block-container {
    padding-top: 2rem;
    padding-bottom: 2rem;
    padding-left: 2rem;
    padding-right: 2rem;
    max-width: 1400px;
}

/* ===== METRIC CARD SYSTEM ===== */
.metric-card {
    background: #ffffff;
    border: 1px solid #e2e8f0;
    border-radius: 12px;
    padding: 20px 24px;
    box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
    height: 140px;
    display: flex;
    flex-direction: column;
    justify-content: space-between;
    transition: transform 0.2s ease, box-shadow 0.2s ease;
}

.metric-card:hover {
    transform: translateY(-2px);
    box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05);
}

.metric-label {
    font-size: 12px;
    font-weight: 600;
    color: #64748b;
    text-transform: uppercase;
    letter-spacing: 0.5px;
    margin-bottom: 8px;
}

.metric-value {
    font-size: 32px;
    font-weight: 700;
    color: #1e293b;
    font-variant-numeric: tabular-nums;
    line-height: 1.2;
}

.metric-delta {
    font-size: 13px;
    font-weight: 500;
    display: flex;
    align-items: center;
    gap: 4px;
    margin-top: 8px;
}

.metric-delta.positive {
    color: #059669;
}

.metric-delta.negative {
    color: #dc2626;
}

.metric-delta.neutral {
    color: #64748b;
}

/* ===== CHART CARD ===== */
.chart-card {
    background: #ffffff;
    border: 1px solid #e2e8f0;
    border-radius: 12px;
    padding: 20px;
    box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
    margin-bottom: 20px;
}

.chart-title {
    font-size: 16px;
    font-weight: 600;
    color: #374151;
    margin-bottom: 16px;
    padding-bottom: 12px;
    border-bottom: 1px solid #f1f5f9;
}

/* ===== TABLE CARD ===== */
.table-card {
    background: #ffffff;
    border: 1px solid #e2e8f0;
    border-radius: 12px;
    padding: 24px;
    box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
}

.table-title {
    font-size: 18px;
    font-weight: 600;
    color: #1e293b;
    margin-bottom: 4px;
}

.table-subtitle {
    font-size: 13px;
    color: #64748b;
    margin-bottom: 16px;
}

/* ===== TYPOGRAPHY ===== */
h1 {
    font-size: 28px;
    font-weight: 700;
    color: #1e293b;
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
    color: #64748b;
    text-transform: uppercase;
    letter-spacing: 0.5px;
}

/* ===== SIDEBAR ===== */
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #ffffff 0%, #f8fafc 100%);
    border-right: 1px solid #e2e8f0;
}

[data-testid="stSidebar"] .block-container {
    padding: 2rem 1rem;
}

.sidebar-section {
    font-size: 11px;
    font-weight: 700;
    color: #1e293b;
    text-transform: uppercase;
    letter-spacing: 0.8px;
    margin: 20px 0 12px 0;
}

[data-testid="stSidebar"] label {
    font-size: 12px;
    font-weight: 500;
    color: #475569;
}

[data-testid="stSidebar"] .stButton>button {
    background-color: #ffffff;
    border: 1px solid #e2e8f0;
    color: #374151;
    font-size: 13px;
    font-weight: 500;
    border-radius: 8px;
    transition: all 0.2s ease;
}

[data-testid="stSidebar"] .stButton>button:hover {
    background-color: #f8fafc;
    border-color: #cbd5e1;
    transform: translateY(-1px);
}

[data-testid="stSidebar"] .stDownloadButton>button {
    background: linear-gradient(135deg, #6366f1 0%, #4f46e5 100%);
    color: white;
    border: none;
    font-weight: 600;
    border-radius: 8px;
    box-shadow: 0 2px 4px rgba(99, 102, 241, 0.2);
}

[data-testid="stSidebar"] .stDownloadButton>button:hover {
    background: linear-gradient(135deg, #4f46e5 0%, #4338ca 100%);
    transform: translateY(-1px);
    box-shadow: 0 4px 8px rgba(99, 102, 241, 0.3);
}

[data-testid="stSidebar"] [data-testid="stMetricValue"] {
    font-size: 22px !important;
    font-weight: 700 !important;
    color: #6366f1 !important;
}

[data-testid="stSidebar"] [data-testid="stMetricLabel"] {
    font-size: 11px !important;
    color: #64748b !important;
    text-transform: uppercase !important;
}

/* ===== MULTISELECT & INPUTS ===== */
.stMultiSelect [data-baseweb="select"] {
    border-radius: 8px;
    border-color: #e2e8f0;
}

.stMultiSelect [data-baseweb="tag"] {
    background-color: #6366f1;
    border-radius: 6px;
    font-size: 11px;
}

.stSelectbox [data-baseweb="select"],
.stDateInput input {
    border-radius: 8px;
    border-color: #e2e8f0;
}

/* ===== TABS ===== */
.stTabs [data-baseweb="tab-list"] {
    gap: 8px;
    background-color: transparent;
    border-bottom: 2px solid #e2e8f0;
}

.stTabs [data-baseweb="tab"] {
    height: 44px;
    padding: 0 20px;
    background-color: transparent;
    border: none;
    color: #64748b;
    font-weight: 500;
    font-size: 14px;
}

.stTabs [aria-selected="true"] {
    color: #6366f1;
    border-bottom: 2px solid #6366f1;
    margin-bottom: -2px;
}

/* ===== DATAFRAME ===== */
.stDataFrame {
    border-radius: 8px;
    border: 1px solid #e2e8f0;
    font-size: 13px;
}

/* ===== LIVE INDICATOR ===== */
.live-indicator {
    display: inline-flex;
    align-items: center;
    gap: 8px;
    padding: 6px 14px;
    background: #f0fdf4;
    border: 1px solid #bbf7d0;
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
    50% { opacity: 0.4; }
}

/* ===== FOCUS STATES (WCAG 2.1) ===== */
button:focus,
.stMultiSelect:focus-within,
.stDateInput:focus-within,
.stSelectbox:focus-within {
    outline: 2px solid #6366f1 !important;
    outline-offset: 2px !important;
}

/* ===== DIVIDER ===== */
hr {
    border: none;
    border-top: 1px solid #e2e8f0;
    margin: 1.5rem 0;
}

/* ===== HIDE NATIVE METRICS (replaced by custom cards) ===== */
[data-testid="stMetricValue"],
[data-testid="stMetricLabel"],
[data-testid="stMetricDelta"] {
    font-family: 'Inter', sans-serif !important;
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

# ==================== DATABASE CONNECTION ====================

@st.cache_resource
def init_connection():
    """Initialize PostgreSQL connection with error handling."""
    database_url = os.getenv('DATABASE_URL')
    if not database_url:
        st.error("""
        **Configuration Error**
        
        DATABASE_URL not found. Please:
        1. Create a `.env` file
        2. Add: `DATABASE_URL=postgresql://...`
        3. Restart the dashboard
        """)
        st.stop()
    
    try:
        engine = create_engine(
            database_url, 
            pool_pre_ping=True, 
            pool_size=10, 
            max_overflow=20
        )
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        return engine
    except Exception as e:
        st.error(f"""
        **Database Connection Failed**
        
        Error: {str(e)}
        
        Solutions:
        1. Check database is running
        2. Verify DATABASE_URL credentials
        3. Check network/firewall settings
        """)
        st.stop()


@st.cache_data(ttl=300)
def load_data():
    """Load and transform data with integrity checks."""
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
        
        # === DATA INTEGRITY FIX ===
        # Filter out transactions with invalid amounts (noise/test data)
        initial_count = len(df)
        df = df[df['amount'] > MIN_VALID_AMOUNT]
        filtered_count = initial_count - len(df)
        
        if filtered_count > 0:
            st.session_state['filtered_noise'] = filtered_count
        
        # === TYPE CONVERSIONS ===
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        
        # === VECTORIZED USD NORMALIZATION ===
        df['amount_usd'] = df['amount'] * df['currency'].map(EXCHANGE_RATES).fillna(1.0)
        
        # === DERIVED COLUMNS ===
        df['date'] = df['timestamp'].dt.date
        df['year_month'] = df['timestamp'].dt.to_period('M').astype(str)
        df['week'] = df['timestamp'].dt.to_period('W').astype(str)
        df['day_of_week'] = df['timestamp'].dt.day_name()
        df['hour'] = df['timestamp'].dt.hour
        
        st.session_state.last_refresh = datetime.now()
        return df
        
    except Exception as e:
        st.error(f"""
        **Data Loading Failed**
        
        Error: {str(e)}
        
        Try running: `python3 etl_pipeline.py`
        """)
        st.stop()

# ==================== UTILITY FUNCTIONS ====================

def format_currency(value):
    """Format value as USD currency string."""
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
    """Format number with thousand separators."""
    if pd.isna(value):
        return "0"
    return f"{int(value):,}"


def calculate_delta(df, metric_col='amount_usd', period_col='year_month'):
    """Calculate month-over-month delta with defensive error handling."""
    try:
        if df is None or len(df) == 0:
            return 0.0
        
        if period_col not in df.columns:
            return 0.0
        
        if metric_col not in df.columns:
            return 0.0
        
        periods = sorted(df[period_col].dropna().unique())
        
        if len(periods) < 2:
            return 0.0
        
        current_period = periods[-1]
        previous_period = periods[-2]
        
        current_mask = df[period_col] == current_period
        previous_mask = df[period_col] == previous_period
        
        current_value = df.loc[current_mask, metric_col].sum()
        previous_value = df.loc[previous_mask, metric_col].sum()
        
        if previous_value == 0 or pd.isna(previous_value):
            return 0.0
        
        delta = ((current_value - previous_value) / previous_value) * 100
        
        if pd.isna(delta) or abs(delta) > 10000:
            return 0.0
        
        return round(delta, 1)
        
    except Exception:
        return 0.0


def get_time_ago(dt):
    """Convert datetime to human-readable 'time ago' string."""
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
    """Apply quick date filters to dataframe."""
    now = pd.Timestamp.now()
    
    filters = {
        "Last 7 Days": (now - pd.Timedelta(days=7)).date(),
        "Last 30 Days": (now - pd.Timedelta(days=30)).date(),
        "This Month": now.replace(day=1).date(),
    }
    
    if filter_type in filters:
        start_date = filters[filter_type]
        return df[df['date'] >= start_date]
    
    elif filter_type == "Last Month":
        last_month = now.replace(day=1) - pd.Timedelta(days=1)
        start_date = last_month.replace(day=1).date()
        end_date = last_month.date()
        return df[(df['date'] >= start_date) & (df['date'] <= end_date)]
    
    return df

# ==================== UI COMPONENTS ====================

def render_metric_card(label: str, value: str, delta: float = None, delta_label: str = "MoM"):
    """Render a custom HTML metric card for consistent styling."""
    
    # Determine delta styling
    if delta is None or delta == 0:
        delta_html = f'<div class="metric-delta neutral">--</div>'
    elif delta > 0:
        delta_html = f'<div class="metric-delta positive">+{delta:.1f}% {delta_label}</div>'
    else:
        delta_html = f'<div class="metric-delta negative">{delta:.1f}% {delta_label}</div>'
    
    card_html = f"""
    <div class="metric-card">
        <div class="metric-label">{label}</div>
        <div class="metric-value">{value}</div>
        {delta_html}
    </div>
    """
    
    st.markdown(card_html, unsafe_allow_html=True)


def render_stat_card(label: str, value: str):
    """Render a simpler stat card without delta."""
    card_html = f"""
    <div class="metric-card" style="height: 100px;">
        <div class="metric-label">{label}</div>
        <div class="metric-value" style="font-size: 24px;">{value}</div>
    </div>
    """
    st.markdown(card_html, unsafe_allow_html=True)


def render_empty_state():
    """Render empty state when no data available."""
    st.warning("""
    **No Transactions Found**
    
    The transactions table is empty.
    
    To get started:
    1. Run: `python3 generate_data.py`
    2. Run: `python3 etl_pipeline.py`
    3. Refresh this page
    """)


def create_trend_area_chart(df):
    """Create area chart with gradient fill for daily volume."""
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
        line=dict(color=COLOR_PRIMARY, width=2.5),
        fill='tozeroy',
        fillcolor='rgba(99, 102, 241, 0.15)',
        hovertemplate='<b>%{x|%b %d, %Y}</b><br>Volume: $%{y:,.0f}<extra></extra>'
    ))
    
    fig.update_layout(
        title=dict(
            text='Daily Transaction Volume',
            font=dict(size=16, color=COLOR_TEXT_PRIMARY, family='Inter'),
            x=0,
            xanchor='left'
        ),
        xaxis_title='',
        yaxis_title='',
        height=CHART_HEIGHT,
        margin=CHART_MARGIN,
        hovermode='x unified',
        template='plotly_white',
        font=dict(family='Inter, sans-serif', size=12, color=COLOR_TEXT_PRIMARY),
        showlegend=False,
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)'
    )
    
    fig.update_xaxes(
        showgrid=False, 
        zeroline=False,
        tickfont=dict(size=11, color=COLOR_TEXT_SECONDARY)
    )
    fig.update_yaxes(
        showgrid=True, 
        gridcolor='#f1f5f9', 
        zeroline=False, 
        tickformat='$,.0s',
        tickfont=dict(size=11, color=COLOR_TEXT_SECONDARY)
    )
    
    return fig


def create_status_donut_chart(df):
    """Create donut chart for transaction status distribution."""
    status_data = df.groupby('status').size().reset_index(name='count')
    status_data = status_data.sort_values('count', ascending=False)
    
    colors = [STATUS_COLORS.get(s, COLOR_GRAY) for s in status_data['status']]
    
    total = status_data['count'].sum()
    
    fig = go.Figure(go.Pie(
        labels=status_data['status'],
        values=status_data['count'],
        hole=0.65,
        marker=dict(
            colors=colors,
            line=dict(color=COLOR_CARD, width=3)
        ),
        textinfo='percent',
        textposition='outside',
        textfont=dict(size=12, family='Inter', color=COLOR_TEXT_PRIMARY),
        hovertemplate='<b>%{label}</b><br>Count: %{value:,}<br>%{percent}<extra></extra>',
        direction='clockwise',
        sort=False
    ))
    
    # Add center annotation
    fig.add_annotation(
        text=f"<b>{format_number(total)}</b><br><span style='font-size:11px;color:#64748b'>Total</span>",
        x=0.5, y=0.5,
        font=dict(size=20, family='Inter', color=COLOR_TEXT_PRIMARY),
        showarrow=False
    )
    
    fig.update_layout(
        title=dict(
            text='Status Distribution',
            font=dict(size=16, color=COLOR_TEXT_PRIMARY, family='Inter'),
            x=0,
            xanchor='left'
        ),
        height=CHART_HEIGHT,
        margin=dict(l=20, r=20, t=60, b=60),
        template='plotly_white',
        font=dict(family='Inter, sans-serif', size=12),
        showlegend=True,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=-0.2,
            xanchor="center",
            x=0.5,
            font=dict(size=11)
        ),
        paper_bgcolor='rgba(0,0,0,0)'
    )
    
    return fig


def create_currency_bar_chart(df):
    """Create horizontal bar chart for volume by currency."""
    currency_data = df.groupby('currency').agg({
        'amount': 'sum',
        'id': 'count'
    }).reset_index()
    currency_data = currency_data.sort_values('amount', ascending=True)
    
    # Format labels to fit better
    max_val = currency_data['amount'].max()
    
    fig = go.Figure(go.Bar(
        x=currency_data['amount'],
        y=currency_data['currency'],
        orientation='h',
        marker=dict(
            color=COLOR_PRIMARY,
            line=dict(color='#4f46e5', width=0)
        ),
        text=currency_data['amount'].apply(lambda x: f"{x/1_000_000:.1f}M" if x >= 1_000_000 else f"{x/1_000:.0f}K"),
        textposition='outside',
        textfont=dict(size=12, color=COLOR_TEXT_PRIMARY),
        customdata=currency_data['id'],
        hovertemplate='<b>%{y}</b><br>Volume: %{x:,.0f}<br>Transactions: %{customdata:,}<extra></extra>'
    ))
    
    fig.update_layout(
        title=dict(
            text='Volume by Currency (Original)',
            font=dict(size=16, color=COLOR_TEXT_PRIMARY, family='Inter'),
            x=0,
            xanchor='left'
        ),
        xaxis_title='',
        yaxis_title='',
        height=CHART_HEIGHT,
        margin=CHART_MARGIN_BAR,
        template='plotly_white',
        font=dict(family='Inter, sans-serif', size=12),
        showlegend=False,
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)'
    )
    
    fig.update_xaxes(
        showgrid=True, 
        gridcolor='#f1f5f9', 
        zeroline=False,
        tickformat=',.0s',
        tickfont=dict(size=11, color=COLOR_TEXT_SECONDARY)
    )
    fig.update_yaxes(
        showgrid=False,
        tickfont=dict(size=12, color=COLOR_TEXT_PRIMARY)
    )
    
    return fig


def create_device_bar_chart(df):
    """Create horizontal bar chart for volume by device."""
    device_data = df.groupby('client_device').agg({
        'amount_usd': 'sum'
    }).reset_index()
    device_data = device_data.sort_values('amount_usd', ascending=True)
    
    colors = ['#10b981' if d == 'mobile' else COLOR_PRIMARY for d in device_data['client_device']]
    
    fig = go.Figure(go.Bar(
        x=device_data['amount_usd'],
        y=device_data['client_device'].str.capitalize(),
        orientation='h',
        marker=dict(color=colors),
        text=device_data['amount_usd'].apply(lambda x: f"${x/1_000_000:.1f}M" if x >= 1_000_000 else f"${x/1_000:.0f}K"),
        textposition='outside',
        textfont=dict(size=12, color=COLOR_TEXT_PRIMARY),
        hovertemplate='<b>%{y}</b><br>Volume: $%{x:,.0f}<extra></extra>'
    ))
    
    fig.update_layout(
        title=dict(
            text='Volume by Device (USD)',
            font=dict(size=16, color=COLOR_TEXT_PRIMARY, family='Inter'),
            x=0,
            xanchor='left'
        ),
        xaxis_title='',
        yaxis_title='',
        height=CHART_HEIGHT,
        margin=CHART_MARGIN_BAR,
        template='plotly_white',
        font=dict(family='Inter, sans-serif', size=12),
        showlegend=False,
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)'
    )
    
    fig.update_xaxes(
        showgrid=True, 
        gridcolor='#f1f5f9', 
        zeroline=False, 
        tickformat='$,.0s',
        tickfont=dict(size=11, color=COLOR_TEXT_SECONDARY)
    )
    fig.update_yaxes(
        showgrid=False,
        tickfont=dict(size=12, color=COLOR_TEXT_PRIMARY)
    )
    
    return fig

# ==================== MAIN APPLICATION ====================

def main():
    """Main application entry point."""
    
    # Load data with spinner
    with st.spinner("Loading data..."):
        df = load_data()
    
    if len(df) == 0:
        render_empty_state()
        return
    
    # ==================== HEADER ====================
    
    header_col1, header_col2 = st.columns([4, 1])
    
    with header_col1:
        st.markdown("# Financial Intelligence")
        st.markdown(
            '<p style="color: #64748b; font-size: 14px; margin-top: -10px;">'
            'Real-time transaction analytics with USD normalization</p>',
            unsafe_allow_html=True
        )
    
    with header_col2:
        time_ago = get_time_ago(st.session_state.last_refresh)
        st.markdown(f"""
        <div class="live-indicator">
            <div class="live-dot"></div>
            <span>Live - {time_ago}</span>
        </div>
        """, unsafe_allow_html=True)
    
    st.divider()
    
    # ==================== SIDEBAR ====================
    
    with st.sidebar:
        st.markdown('<div class="sidebar-section">Filters</div>', unsafe_allow_html=True)
        
        # Quick Actions
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Reset All", use_container_width=True, key="reset_btn"):
                st.session_state.filters = {
                    'currencies': None,
                    'statuses': None,
                    'date_range': None,
                    'quick_filter': 'All Time'
                }
                st.rerun()
        
        with col2:
            if st.button("Apply", use_container_width=True, key="apply_btn", type="primary"):
                pass
        
        st.markdown("")
        
        # Time Period
        quick_filter = st.selectbox(
            "Time Period",
            ["All Time", "Last 7 Days", "Last 30 Days", "This Month", "Last Month"],
            index=0
        )
        
        st.divider()
        
        # Currency Filter
        st.markdown('<div class="sidebar-section">Currency</div>', unsafe_allow_html=True)
        all_currencies = sorted(df['currency'].unique())
        
        if st.session_state.filters['currencies'] is None:
            st.session_state.filters['currencies'] = all_currencies
        
        selected_currencies = st.multiselect(
            "Select currencies",
            options=all_currencies,
            default=st.session_state.filters['currencies'],
            format_func=lambda x: CURRENCY_DISPLAY.get(x, x),
            label_visibility="collapsed"
        )
        
        if len(selected_currencies) == 0:
            st.error("Select at least one currency")
            selected_currencies = all_currencies
        
        # Status Filter
        st.markdown('<div class="sidebar-section">Status</div>', unsafe_allow_html=True)
        all_statuses = sorted(df['status'].unique())
        
        if st.session_state.filters['statuses'] is None:
            st.session_state.filters['statuses'] = all_statuses
        
        selected_statuses = st.multiselect(
            "Select status",
            options=all_statuses,
            default=st.session_state.filters['statuses'],
            label_visibility="collapsed"
        )
        
        if len(selected_statuses) == 0:
            st.error("Select at least one status")
            selected_statuses = all_statuses
        
        st.divider()
        
        # Date Range
        st.markdown('<div class="sidebar-section">Date Range</div>', unsafe_allow_html=True)
        date_range = st.date_input(
            "Select dates",
            value=(df['timestamp'].min().date(), df['timestamp'].max().date()),
            min_value=df['timestamp'].min().date(),
            max_value=df['timestamp'].max().date(),
            label_visibility="collapsed"
        )
        
        st.divider()
        
        # Results Summary
        st.markdown('<div class="sidebar-section">Results</div>', unsafe_allow_html=True)
    
    # ==================== APPLY FILTERS ====================
    
    df_filtered = df.copy()
    
    # Quick filter
    if quick_filter != "All Time":
        df_filtered = apply_quick_filter(df_filtered, quick_filter)
    
    # Currency filter
    if selected_currencies:
        df_filtered = df_filtered[df_filtered['currency'].isin(selected_currencies)]
    
    # Status filter
    if selected_statuses:
        df_filtered = df_filtered[df_filtered['status'].isin(selected_statuses)]
    
    # Date range filter
    if len(date_range) == 2:
        start, end = date_range
        df_filtered = df_filtered[
            (df_filtered['timestamp'].dt.date >= start) &
            (df_filtered['timestamp'].dt.date <= end)
        ]
    
    # Update sidebar results
    with st.sidebar:
        st.metric(
            "Filtered Records",
            format_number(len(df_filtered)),
            delta=f"of {format_number(len(df))} total"
        )
        
        st.divider()
        
        # Export
        st.markdown('<div class="sidebar-section">Export</div>', unsafe_allow_html=True)
        csv = df_filtered.to_csv(index=False)
        st.download_button(
            label="Download CSV",
            data=csv,
            file_name=f"transactions_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            mime="text/csv",
            use_container_width=True
        )
        
        st.divider()
        
        # Exchange Rates Info
        st.markdown('<div class="sidebar-section">Exchange Rates</div>', unsafe_allow_html=True)
        st.caption("USD: 1.00 | EUR: 1.08")
        st.caption("GBP: 1.27 | COP: 0.00025")
    
    # ==================== VALIDATION ====================
    
    if len(df_filtered) == 0:
        st.warning("""
        **No Data Matches Your Filters**
        
        Try adjusting your date range, currency, or status filters.
        """)
        if st.button("Reset All Filters"):
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
    
    # ==================== TAB 1: OVERVIEW ====================
    
    with tab1:
        
        # === ROW 1: KPI CARDS ===
        
        kpi_col1, kpi_col2, kpi_col3, kpi_col4 = st.columns(4)
        
        # Calculate KPIs
        volume = df_filtered['amount_usd'].sum()
        delta_vol = calculate_delta(df_filtered)
        
        total_txn = len(df_filtered)
        txn_by_month = df_filtered.groupby('year_month').size().reset_index(name='count')
        txn_by_month['amount_usd'] = txn_by_month['count']
        delta_txn = calculate_delta(txn_by_month)
        
        avg_ticket = df_filtered['amount_usd'].mean()
        try:
            periods = sorted(df_filtered['year_month'].unique())
            if len(periods) >= 2:
                curr_avg = df_filtered[df_filtered['year_month'] == periods[-1]]['amount_usd'].mean()
                prev_avg = df_filtered[df_filtered['year_month'] == periods[-2]]['amount_usd'].mean()
                delta_avg = ((curr_avg - prev_avg) / prev_avg * 100) if prev_avg > 0 else 0
            else:
                delta_avg = 0
        except Exception:
            delta_avg = 0
        
        completed = len(df_filtered[df_filtered['status'] == 'COMPLETED'])
        success_rate = (completed / total_txn * 100) if total_txn > 0 else 0
        
        # Render KPI cards
        with kpi_col1:
            render_metric_card("Total Volume", format_currency(volume), delta_vol)
        
        with kpi_col2:
            render_metric_card("Transactions", format_number(total_txn), delta_txn)
        
        with kpi_col3:
            render_metric_card("Avg Ticket", format_currency(avg_ticket), delta_avg)
        
        with kpi_col4:
            render_metric_card("Success Rate", f"{success_rate:.1f}%", None)
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        # === ROW 2: CHARTS ===
        
        chart_col1, chart_col2 = st.columns([2, 1])
        
        with chart_col1:
            st.plotly_chart(create_trend_area_chart(df_filtered), use_container_width=True)
        
        with chart_col2:
            st.plotly_chart(create_status_donut_chart(df_filtered), use_container_width=True)
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        # === ROW 3: STATS ===
        
        st.markdown("### Key Statistics")
        
        stat_col1, stat_col2, stat_col3, stat_col4 = st.columns(4)
        
        valid_amounts = df_filtered[df_filtered['amount_usd'] > MIN_VALID_AMOUNT]['amount_usd']
        
        with stat_col1:
            max_val = valid_amounts.max() if len(valid_amounts) > 0 else 0
            render_stat_card("Max Transaction", format_currency(max_val))
        
        with stat_col2:
            min_val = valid_amounts.min() if len(valid_amounts) > 0 else 0
            render_stat_card("Min Transaction", format_currency(min_val))
        
        with stat_col3:
            unique_clients = df_filtered['client_email'].nunique()
            render_stat_card("Unique Clients", format_number(unique_clients))
        
        with stat_col4:
            mobile_count = len(df_filtered[df_filtered['client_device'] == 'mobile'])
            mobile_pct = (mobile_count / total_txn * 100) if total_txn > 0 else 0
            render_stat_card("Mobile Share", f"{mobile_pct:.1f}%")
    
    # ==================== TAB 2: ANALYSIS ====================
    
    with tab2:
        
        analysis_col1, analysis_col2 = st.columns(2)
        
        with analysis_col1:
            st.plotly_chart(create_currency_bar_chart(df_filtered), use_container_width=True)
        
        with analysis_col2:
            st.plotly_chart(create_device_bar_chart(df_filtered), use_container_width=True)
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        # Status Breakdown Table
        st.subheader("Status Breakdown")
        st.caption("Aggregated metrics by transaction status")
        
        status_summary = df_filtered.groupby('status').agg({
            'amount_usd': ['sum', 'mean', 'count']
        }).round(2)
        status_summary.columns = ['Total Volume', 'Average', 'Count']
        status_summary = status_summary.sort_values('Total Volume', ascending=False)
        status_summary['Total Volume'] = status_summary['Total Volume'].apply(format_currency)
        status_summary['Average'] = status_summary['Average'].apply(format_currency)
        status_summary['Count'] = status_summary['Count'].apply(format_number)
        
        st.dataframe(status_summary, use_container_width=True)
    
    # ==================== TAB 3: TRANSACTIONS ====================
    
    with tab3:
        
        st.subheader("Transaction Ledger")
        st.caption("Recent 50 transactions with amounts normalized to USD")
        
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
            height=450,
            hide_index=True
        )
    
    # ==================== FOOTER ====================
    
    st.divider()
    st.markdown(
        f'<p style="color: #94a3b8; font-size: 12px; text-align: center;">'
        f'v5.0 Gold Master | PostgreSQL on Railway | '
        f'Last updated: {st.session_state.last_refresh.strftime("%Y-%m-%d %H:%M:%S")}'
        f'</p>',
        unsafe_allow_html=True
    )


if __name__ == "__main__":
    main()
```

## Nombre del Archivo: backend/main.py

```python
"""
Financial Intelligence API v5.0
FastAPI backend for the Next.js dashboard.

Author: Senior Full Stack Engineer
Date: 2026-01-31
"""

import os
from datetime import datetime, timedelta
from typing import List, Optional

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv
import pandas as pd
from sqlalchemy import create_engine, text

load_dotenv()

# ==================== CONFIGURATION ====================

app = FastAPI(
    title="Financial Intelligence API",
    description="Real-time transaction analytics API",
    version="5.0.0"
)

# CORS for Next.js frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Exchange rates
EXCHANGE_RATES = {
    'USD': 1.0,
    'EUR': 1.08,
    'GBP': 1.27,
    'COP': 0.00025
}

MIN_VALID_AMOUNT = 0.01

# ==================== DATABASE ====================

def get_engine():
    """Get SQLAlchemy engine."""
    database_url = os.getenv('DATABASE_URL')
    if not database_url:
        raise HTTPException(status_code=500, detail="DATABASE_URL not configured")
    return create_engine(database_url, pool_pre_ping=True)


def load_transactions() -> pd.DataFrame:
    """Load transactions from database."""
    engine = get_engine()
    
    query = """
    SELECT id, timestamp, amount, currency, status,
           client_email, client_ip, client_device, metadata
    FROM transactions
    ORDER BY timestamp DESC
    """
    
    df = pd.read_sql(query, engine)
    
    if len(df) == 0:
        return pd.DataFrame()
    
    # Filter invalid amounts
    df = df[df['amount'] > MIN_VALID_AMOUNT]
    
    # Convert timestamp
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    
    # Calculate USD amount
    df['amount_usd'] = df['amount'] * df['currency'].map(EXCHANGE_RATES).fillna(1.0)
    
    # Derived columns
    df['date'] = df['timestamp'].dt.date
    df['year_month'] = df['timestamp'].dt.to_period('M').astype(str)
    
    return df

# ==================== MODELS ====================

class Transaction(BaseModel):
    id: str
    timestamp: datetime
    amount: float
    currency: str
    status: str
    amount_usd: float
    client_email: str
    client_device: str

class KPIData(BaseModel):
    totalVolume: float
    totalTransactions: int
    avgTicket: float
    successRate: float
    volumeDelta: float
    transactionsDelta: float
    avgTicketDelta: float

class DailyVolume(BaseModel):
    date: str
    volume: float
    count: int

class StatusDistribution(BaseModel):
    status: str
    count: int
    percentage: float

class CurrencyVolume(BaseModel):
    currency: str
    amount: float
    count: int

class DeviceVolume(BaseModel):
    device: str
    amount: float
    percentage: float

class DashboardData(BaseModel):
    kpis: KPIData
    dailyVolume: List[DailyVolume]
    statusDistribution: List[StatusDistribution]
    currencyVolume: List[CurrencyVolume]
    deviceVolume: List[DeviceVolume]
    recentTransactions: List[Transaction]
    lastUpdated: datetime

# ==================== HELPERS ====================

def calculate_delta(df: pd.DataFrame, metric_col: str = 'amount_usd') -> float:
    """Calculate month-over-month delta."""
    try:
        if len(df) == 0 or 'year_month' not in df.columns:
            return 0.0
        
        periods = sorted(df['year_month'].unique())
        if len(periods) < 2:
            return 0.0
        
        current = df[df['year_month'] == periods[-1]][metric_col].sum()
        previous = df[df['year_month'] == periods[-2]][metric_col].sum()
        
        if previous == 0:
            return 0.0
        
        delta = ((current - previous) / previous) * 100
        return round(delta, 1)
    except Exception:
        return 0.0

# ==================== ENDPOINTS ====================

@app.get("/")
async def root():
    """Health check."""
    return {"status": "healthy", "version": "5.0.0"}


@app.get("/api/dashboard", response_model=DashboardData)
async def get_dashboard_data(
    currencies: Optional[str] = Query(None, description="Comma-separated currencies"),
    statuses: Optional[str] = Query(None, description="Comma-separated statuses"),
    start_date: Optional[str] = Query(None, description="Start date YYYY-MM-DD"),
    end_date: Optional[str] = Query(None, description="End date YYYY-MM-DD"),
):
    """Get complete dashboard data."""
    try:
        df = load_transactions()
        
        if len(df) == 0:
            raise HTTPException(status_code=404, detail="No transactions found")
        
        # Apply filters
        if currencies:
            currency_list = [c.strip() for c in currencies.split(",")]
            df = df[df['currency'].isin(currency_list)]
        
        if statuses:
            status_list = [s.strip() for s in statuses.split(",")]
            df = df[df['status'].isin(status_list)]
        
        if start_date:
            start = pd.to_datetime(start_date).date()
            df = df[df['date'] >= start]
        
        if end_date:
            end = pd.to_datetime(end_date).date()
            df = df[df['date'] <= end]
        
        if len(df) == 0:
            raise HTTPException(status_code=404, detail="No data matches filters")
        
        # Calculate KPIs
        total_volume = df['amount_usd'].sum()
        total_transactions = len(df)
        avg_ticket = df['amount_usd'].mean()
        completed = len(df[df['status'] == 'COMPLETED'])
        success_rate = (completed / total_transactions * 100) if total_transactions > 0 else 0
        
        volume_delta = calculate_delta(df)
        
        # Transaction count delta
        txn_by_month = df.groupby('year_month').size().reset_index(name='count')
        txn_by_month['amount_usd'] = txn_by_month['count']
        txn_delta = calculate_delta(txn_by_month)
        
        # Avg ticket delta
        try:
            periods = sorted(df['year_month'].unique())
            if len(periods) >= 2:
                curr_avg = df[df['year_month'] == periods[-1]]['amount_usd'].mean()
                prev_avg = df[df['year_month'] == periods[-2]]['amount_usd'].mean()
                avg_delta = ((curr_avg - prev_avg) / prev_avg * 100) if prev_avg > 0 else 0
            else:
                avg_delta = 0
        except Exception:
            avg_delta = 0
        
        kpis = KPIData(
            totalVolume=round(total_volume, 2),
            totalTransactions=total_transactions,
            avgTicket=round(avg_ticket, 2),
            successRate=round(success_rate, 1),
            volumeDelta=volume_delta,
            transactionsDelta=txn_delta,
            avgTicketDelta=round(avg_delta, 1)
        )
        
        # Daily volume
        daily = df.groupby('date').agg({
            'amount_usd': 'sum',
            'id': 'count'
        }).reset_index()
        daily_volume = [
            DailyVolume(
                date=row['date'].strftime('%b %d'),
                volume=round(row['amount_usd'], 2),
                count=int(row['id'])
            )
            for _, row in daily.iterrows()
        ]
        
        # Status distribution
        status_counts = df.groupby('status').size().reset_index(name='count')
        total = status_counts['count'].sum()
        status_distribution = [
            StatusDistribution(
                status=row['status'],
                count=int(row['count']),
                percentage=round(row['count'] / total * 100, 1)
            )
            for _, row in status_counts.iterrows()
        ]
        
        # Currency volume
        currency_data = df.groupby('currency').agg({
            'amount': 'sum',
            'id': 'count'
        }).reset_index()
        currency_volume = [
            CurrencyVolume(
                currency=row['currency'],
                amount=round(row['amount'], 2),
                count=int(row['id'])
            )
            for _, row in currency_data.iterrows()
        ]
        
        # Device volume
        device_data = df.groupby('client_device').agg({
            'amount_usd': 'sum'
        }).reset_index()
        device_total = device_data['amount_usd'].sum()
        device_volume = [
            DeviceVolume(
                device=row['client_device'].capitalize(),
                amount=round(row['amount_usd'], 2),
                percentage=round(row['amount_usd'] / device_total * 100, 1)
            )
            for _, row in device_data.iterrows()
        ]
        
        # Recent transactions
        recent = df.head(50)
        recent_transactions = [
            Transaction(
                id=str(row['id']),
                timestamp=row['timestamp'],
                amount=round(row['amount'], 2),
                currency=row['currency'],
                status=row['status'],
                amount_usd=round(row['amount_usd'], 2),
                client_email=row['client_email'],
                client_device=row['client_device']
            )
            for _, row in recent.iterrows()
        ]
        
        return DashboardData(
            kpis=kpis,
            dailyVolume=daily_volume,
            statusDistribution=status_distribution,
            currencyVolume=currency_volume,
            deviceVolume=device_volume,
            recentTransactions=recent_transactions,
            lastUpdated=datetime.now()
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/transactions", response_model=List[Transaction])
async def get_transactions(
    limit: int = Query(50, ge=1, le=500),
    offset: int = Query(0, ge=0),
):
    """Get paginated transactions."""
    try:
        df = load_transactions()
        
        if len(df) == 0:
            return []
        
        df = df.iloc[offset:offset + limit]
        
        return [
            Transaction(
                id=str(row['id']),
                timestamp=row['timestamp'],
                amount=round(row['amount'], 2),
                currency=row['currency'],
                status=row['status'],
                amount_usd=round(row['amount_usd'], 2),
                client_email=row['client_email'],
                client_device=row['client_device']
            )
            for _, row in df.iterrows()
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/filters")
async def get_filter_options():
    """Get available filter options."""
    try:
        df = load_transactions()
        
        if len(df) == 0:
            return {
                "currencies": [],
                "statuses": [],
                "dateRange": None
            }
        
        return {
            "currencies": sorted(df['currency'].unique().tolist()),
            "statuses": sorted(df['status'].unique().tolist()),
            "dateRange": {
                "min": df['date'].min().isoformat(),
                "max": df['date'].max().isoformat()
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
```

## Nombre del Archivo: backend/requirements.txt

```text
# Financial Intelligence API - Backend Dependencies
fastapi>=0.109.0
uvicorn[standard]>=0.27.0
python-dotenv>=1.0.0
pandas>=2.2.0
sqlalchemy>=2.0.25
psycopg2-binary>=2.9.9
pydantic>=2.6.0
```

## Nombre del Archivo: etl_pipeline.py

```python
"""
ETL Pipeline para datos financieros SaaS.
Lee JSON con datos sucios, limpia y carga a PostgreSQL.

Author: Senior Data Engineer
Date: 2026-01-31
"""

import json
import os
import re
from datetime import datetime
from typing import Dict, Tuple, Optional

import pandas as pd
from dotenv import load_dotenv
from sqlalchemy import (
    create_engine,
    Column,
    String,
    Float,
    DateTime,
    Integer,
    Table,
    MetaData,
    text
)
from sqlalchemy.types import TIMESTAMP, NUMERIC, VARCHAR

# Configuración
load_dotenv()


class ETLPipeline:
    """Pipeline ETL para procesamiento de transacciones financieras."""
    
    # Mapeo de símbolos de moneda a códigos ISO
    CURRENCY_SYMBOLS = {
        '$': 'USD',
        '€': 'EUR',
        '£': 'GBP',
        'COP': 'COP',
    }
    
    # Monedas con formato europeo (coma como decimal)
    EUROPEAN_FORMAT_CURRENCIES = {'EUR', 'COP'}
    
    def __init__(self, input_file: str, database_url: str):
        """
        Inicializa el pipeline ETL.
        
        Args:
            input_file: Ruta al archivo JSON de entrada
            database_url: URL de conexión a PostgreSQL
        """
        self.input_file = input_file
        self.database_url = database_url
        self.engine = None
        self.stats = {
            'total_read': 0,
            'null_amounts_removed': 0,
            'duplicates_removed': 0,
            'final_loaded': 0,
            'parse_errors': 0
        }
    
    def connect_database(self):
        """Establece conexión con la base de datos PostgreSQL."""
        try:
            self.engine = create_engine(
                self.database_url,
                pool_pre_ping=True,
                pool_size=10,
                max_overflow=20
            )
            # Test de conexión
            with self.engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            print("✅ Conexión exitosa a PostgreSQL")
        except Exception as e:
            print(f"❌ Error al conectar a la base de datos: {e}")
            raise
    
    def load_json(self) -> pd.DataFrame:
        """
        Carga el archivo JSON a un DataFrame de pandas.
        
        Returns:
            DataFrame con los datos crudos
        """
        print(f"\n📂 Cargando datos desde {self.input_file}...")
        
        try:
            with open(self.input_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            df = pd.DataFrame(data)
            self.stats['total_read'] = len(df)
            print(f"  ✓ {len(df):,} registros cargados")
            
            return df
        
        except FileNotFoundError:
            print(f"❌ Error: No se encontró el archivo {self.input_file}")
            raise
        except json.JSONDecodeError as e:
            print(f"❌ Error al parsear JSON: {e}")
            raise
    
    def flatten_nested_fields(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Desanida el campo 'client_details' en columnas separadas.
        
        Args:
            df: DataFrame con datos crudos
            
        Returns:
            DataFrame con campos desanidados
        """
        print("\n🔄 Desanidando campos nested (client_details)...")
        
        # Extraer campos anidados
        df['client_email'] = df['client_details'].apply(
            lambda x: x.get('email') if isinstance(x, dict) else None
        )
        df['client_ip'] = df['client_details'].apply(
            lambda x: x.get('ip_address') if isinstance(x, dict) else None
        )
        df['client_device'] = df['client_details'].apply(
            lambda x: x.get('device') if isinstance(x, dict) else None
        )
        
        # Eliminar columna original
        df = df.drop('client_details', axis=1)
        
        print("  ✓ Campos desanidados: client_email, client_ip, client_device")
        
        return df
    
    def parse_timestamp(self, timestamp_str: str) -> Optional[datetime]:
        """
        Parsea timestamps en formato mixto (ISO 8601 o DD/MM/YYYY HH:mm).
        
        Args:
            timestamp_str: String con el timestamp
            
        Returns:
            Objeto datetime o None si falla el parseo
        """
        if pd.isna(timestamp_str) or timestamp_str == '':
            return None
        
        try:
            # Intentar formato ISO 8601 primero
            if 'T' in str(timestamp_str):
                return pd.to_datetime(timestamp_str, format='ISO8601', utc=True)
            else:
                # Formato local DD/MM/YYYY HH:mm
                return pd.to_datetime(
                    timestamp_str, 
                    format='%d/%m/%Y %H:%M',
                    utc=True
                )
        except Exception as e:
            self.stats['parse_errors'] += 1
            return None
    
    def detect_currency_and_format(self, amount_str: str) -> Tuple[Optional[str], bool]:
        """
        Detecta la moneda y el formato (europeo vs US) de un string de monto.
        
        Args:
            amount_str: String con el monto y símbolo de moneda
            
        Returns:
            Tupla (código_moneda, es_formato_europeo)
        """
        if pd.isna(amount_str) or amount_str == '':
            return None, False
        
        amount_str = str(amount_str).strip()
        
        # Detectar COP (caso especial, tiene el código explícito)
        if 'COP' in amount_str:
            return 'COP', True
        
        # Detectar por símbolos
        for symbol, currency_code in self.CURRENCY_SYMBOLS.items():
            if symbol in amount_str:
                is_european = currency_code in self.EUROPEAN_FORMAT_CURRENCIES
                return currency_code, is_european
        
        return None, False
    
    def parse_amount(self, amount_str: str) -> Tuple[Optional[float], Optional[str]]:
        """
        Parsea un string de monto con formato mixto a float y código de moneda.
        
        Maneja formatos como:
        - "$1,200.50" (US) -> 1200.50, USD
        - "1.200,50 €" (EU) -> 1200.50, EUR
        - "COP 50000" (COL) -> 50000.0, COP
        
        Args:
            amount_str: String con el monto
            
        Returns:
            Tupla (monto_float, código_moneda)
        """
        if pd.isna(amount_str) or amount_str == '':
            return None, None
        
        try:
            amount_str = str(amount_str).strip()
            
            # Detectar moneda y formato
            currency, is_european_format = self.detect_currency_and_format(amount_str)
            
            if currency is None:
                return None, None
            
            # Extraer solo los dígitos, comas y puntos
            numeric_str = re.sub(r'[^\d,.]', '', amount_str)
            
            if not numeric_str:
                return None, None
            
            # Parsear según el formato
            if is_european_format:
                # Formato europeo: 1.200,50 (punto=miles, coma=decimal)
                # Remover puntos (separador de miles) y reemplazar coma por punto
                numeric_str = numeric_str.replace('.', '')
                numeric_str = numeric_str.replace(',', '.')
            else:
                # Formato US: 1,200.50 (coma=miles, punto=decimal)
                # Remover comas (separador de miles)
                numeric_str = numeric_str.replace(',', '')
            
            amount = float(numeric_str)
            return amount, currency
        
        except (ValueError, AttributeError):
            return None, None
    
    def clean_timestamps(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Limpia y normaliza la columna de timestamps.
        
        Args:
            df: DataFrame con datos crudos
            
        Returns:
            DataFrame con timestamps limpios
        """
        print("\n🕐 Limpiando timestamps...")
        
        df['timestamp'] = df['timestamp'].apply(self.parse_timestamp)
        
        # Contar nulos después del parseo
        null_timestamps = df['timestamp'].isna().sum()
        
        print(f"  ✓ Timestamps parseados correctamente")
        if null_timestamps > 0:
            print(f"  ⚠️  {null_timestamps} timestamps no pudieron ser parseados")
        
        return df
    
    def clean_amounts(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Limpia y normaliza la columna de montos.
        Crea columnas 'amount' (float) y 'currency' (string).
        
        Args:
            df: DataFrame con datos crudos
            
        Returns:
            DataFrame con montos limpios
        """
        print("\n💰 Limpiando montos y detectando monedas...")
        
        # Aplicar parsing de montos
        parsed_amounts = df['amount_str'].apply(self.parse_amount)
        
        df['amount'] = parsed_amounts.apply(lambda x: x[0])
        df['currency'] = parsed_amounts.apply(lambda x: x[1])
        
        # Contar y eliminar filas con montos nulos
        null_amounts_before = df['amount'].isna().sum()
        df = df.dropna(subset=['amount'])
        self.stats['null_amounts_removed'] = null_amounts_before
        
        print(f"  ✓ Montos parseados y normalizados")
        print(f"  ✓ Columnas creadas: 'amount' (float), 'currency' (string)")
        print(f"  ✓ {null_amounts_before:,} filas con montos nulos eliminadas")
        
        # Mostrar distribución de monedas
        currency_dist = df['currency'].value_counts()
        print(f"\n  📊 Distribución de monedas:")
        for curr, count in currency_dist.items():
            print(f"     • {curr}: {count:,} ({count/len(df)*100:.1f}%)")
        
        return df
    
    def remove_duplicates(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Elimina registros duplicados basándose en el ID.
        Mantiene la última ocurrencia (más reciente).
        
        Args:
            df: DataFrame con datos
            
        Returns:
            DataFrame sin duplicados
        """
        print("\n🔄 Eliminando duplicados...")
        
        duplicates_before = df.duplicated(subset=['id'], keep='last').sum()
        df = df.drop_duplicates(subset=['id'], keep='last')
        self.stats['duplicates_removed'] = duplicates_before
        
        print(f"  ✓ {duplicates_before:,} registros duplicados eliminados")
        print(f"  ✓ Se mantuvieron las últimas ocurrencias")
        
        return df
    
    def transform(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Ejecuta todas las transformaciones de limpieza.
        
        Args:
            df: DataFrame con datos crudos
            
        Returns:
            DataFrame limpio y transformado
        """
        print("\n" + "="*70)
        print("🔧 INICIANDO TRANSFORMACIONES")
        print("="*70)
        
        # 1. Flatten nested fields
        df = self.flatten_nested_fields(df)
        
        # 2. Limpiar timestamps
        df = self.clean_timestamps(df)
        
        # 3. Limpiar montos
        df = self.clean_amounts(df)
        
        # 4. Eliminar duplicados
        df = self.remove_duplicates(df)
        
        # 5. Reordenar columnas para mejor legibilidad
        column_order = [
            'id', 'timestamp', 'amount', 'currency', 'status',
            'client_email', 'client_ip', 'client_device', 'metadata'
        ]
        # Mantener solo las columnas que existen
        column_order = [col for col in column_order if col in df.columns]
        df = df[column_order]
        
        # Eliminar la columna amount_str original
        if 'amount_str' in df.columns:
            df = df.drop('amount_str', axis=1)
        
        self.stats['final_loaded'] = len(df)
        
        print("\n✅ Transformaciones completadas")
        
        return df
    
    def load_to_database(self, df: pd.DataFrame, table_name: str = 'transactions'):
        """
        Carga el DataFrame limpio a PostgreSQL.
        
        Args:
            df: DataFrame limpio
            table_name: Nombre de la tabla destino
        """
        print("\n" + "="*70)
        print("📤 CARGANDO A BASE DE DATOS")
        print("="*70)
        
        try:
            # Definir tipos de datos SQL explícitamente
            dtype_mapping = {
                'id': VARCHAR(36),
                'timestamp': TIMESTAMP(timezone=True),
                'amount': NUMERIC(15, 2),
                'currency': VARCHAR(3),
                'status': VARCHAR(20),
                'client_email': VARCHAR(255),
                'client_ip': VARCHAR(45),
                'client_device': VARCHAR(20),
                'metadata': VARCHAR(500)
            }
            
            # Filtrar solo los tipos que existen en el DataFrame
            dtype_mapping = {k: v for k, v in dtype_mapping.items() if k in df.columns}
            
            print(f"\n📊 Cargando {len(df):,} registros a tabla '{table_name}'...")
            
            # Cargar a PostgreSQL
            df.to_sql(
                name=table_name,
                con=self.engine,
                if_exists='replace',
                index=False,
                dtype=dtype_mapping,
                method='multi',
                chunksize=1000
            )
            
            print(f"  ✅ {len(df):,} registros cargados exitosamente")
            
            # Verificar la carga
            with self.engine.connect() as conn:
                result = conn.execute(text(f"SELECT COUNT(*) FROM {table_name}"))
                count = result.fetchone()[0]
                print(f"  ✅ Verificación: {count:,} registros en la tabla")
        
        except Exception as e:
            print(f"  ❌ Error al cargar datos: {e}")
            raise
    
    def print_summary(self):
        """Imprime un resumen del proceso ETL."""
        print("\n" + "="*70)
        print("📊 RESUMEN DEL PIPELINE ETL")
        print("="*70)
        print(f"\n📥 Total de registros leídos:          {self.stats['total_read']:,}")
        print(f"❌ Registros con montos nulos (removidos): {self.stats['null_amounts_removed']:,}")
        print(f"🔄 Registros duplicados (removidos):      {self.stats['duplicates_removed']:,}")
        
        if self.stats['parse_errors'] > 0:
            print(f"⚠️  Errores de parseo de timestamps:      {self.stats['parse_errors']:,}")
        
        total_removed = (
            self.stats['null_amounts_removed'] + 
            self.stats['duplicates_removed']
        )
        print(f"\n📊 Total de registros removidos:       {total_removed:,}")
        print(f"✅ Registros cargados exitosamente:    {self.stats['final_loaded']:,}")
        
        # Calcular porcentajes
        if self.stats['total_read'] > 0:
            success_rate = (self.stats['final_loaded'] / self.stats['total_read']) * 100
            print(f"\n📈 Tasa de éxito: {success_rate:.2f}%")
        
        print("="*70 + "\n")
    
    def run(self):
        """Ejecuta el pipeline ETL completo."""
        print("\n" + "="*70)
        print("🚀 ETL PIPELINE - FINANCIAL SAAS DATA")
        print("="*70)
        
        try:
            # 1. Conectar a la base de datos
            self.connect_database()
            
            # 2. Extraer (Load JSON)
            df = self.load_json()
            
            # 3. Transformar (Clean & Transform)
            df_clean = self.transform(df)
            
            # 4. Cargar (Load to PostgreSQL)
            self.load_to_database(df_clean)
            
            # 5. Resumen
            self.print_summary()
            
            print("✨ Pipeline ETL completado exitosamente!\n")
            
        except Exception as e:
            print(f"\n❌ Error crítico en el pipeline: {e}")
            raise


def main():
    """Función principal."""
    # Configuración
    INPUT_FILE = 'raw_transactions.json'
    DATABASE_URL = os.getenv('DATABASE_URL')
    
    # Validar que existe la variable de entorno
    if not DATABASE_URL:
        print("❌ Error: Variable de entorno DATABASE_URL no configurada")
        print("   Por favor, configura DATABASE_URL en el archivo .env")
        return
    
    # Ejecutar pipeline
    pipeline = ETLPipeline(INPUT_FILE, DATABASE_URL)
    pipeline.run()


if __name__ == "__main__":
    main()
```

## Nombre del Archivo: generate_data.py

```python
"""
Script de generación de datos de prueba para sistema financiero SaaS.
Genera 5,000 transacciones con datos intencionalmente "sucios" para testing.

Author: Senior Data Engineer
Date: 2026-01-31
"""

import json
import random
import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional

import pandas as pd
from faker import Faker

# Configuración
fake = Faker(['es_ES', 'en_US', 'de_DE'])
random.seed(42)  # Para reproducibilidad
Faker.seed(42)

# Constantes
NUM_RECORDS = 5000
DUPLICATE_RATE = 0.05  # 5% duplicados
NULL_AMOUNT_RATE = 0.02  # 2% amounts nulos
ISO_FORMAT_RATE = 0.70  # 70% timestamps en ISO 8601

STATUSES = ['COMPLETED', 'FAILED', 'PENDING', 'REFUNDED']
DEVICES = ['mobile', 'desktop']
CURRENCY_FORMATS = [
    ('USD', '$', ',', '.', True),   # $1,200.50
    ('EUR', '€', '.', ',', False),  # 1.200,50 €
    ('COP', 'COP ', ',', '.', True), # COP 50,000
    ('GBP', '£', ',', '.', True),   # £1,200.50
    ('MXN', '$', ',', '.', True),   # $1,200.50 MXN
]

METADATA_OPTIONS = [
    None,
    "Transacción automática",
    "Cliente VIP - prioridad alta",
    "Nota: verificar documento",
    "",
    "Reintento de pago anterior",
    "Campaña Q4 2025",
    "Usuario nuevo - primera transacción",
]


def generate_random_timestamp(start_year: int = 2024, end_year: int = 2026) -> datetime:
    """Genera un timestamp aleatorio entre start_year y end_year."""
    start_date = datetime(start_year, 1, 1)
    end_date = datetime(end_year, 12, 31, 23, 59, 59)
    
    time_between = end_date - start_date
    days_between = time_between.days
    random_days = random.randrange(days_between)
    random_seconds = random.randrange(86400)  # Segundos en un día
    
    random_date = start_date + timedelta(days=random_days, seconds=random_seconds)
    return random_date


def format_timestamp(dt: datetime, use_iso: bool = True) -> str:
    """
    Formatea el timestamp en ISO 8601 o formato local DD/MM/YYYY HH:mm.
    
    Args:
        dt: Objeto datetime
        use_iso: Si True, usa ISO 8601; si False, usa formato local
    """
    if use_iso:
        return dt.isoformat()
    else:
        return dt.strftime('%d/%m/%Y %H:%M')


def format_amount(amount: float) -> str:
    """
    Formatea el monto con diferentes formatos de moneda.
    
    Args:
        amount: Monto numérico
        
    Returns:
        String formateado con símbolo de moneda y formato regional
    """
    currency, symbol, thousands_sep, decimal_sep, symbol_first = random.choice(CURRENCY_FORMATS)
    
    # Formatear el número
    amount_str = f"{amount:,.2f}"
    
    # Ajustar separadores según el formato de moneda
    if thousands_sep != ',' or decimal_sep != '.':
        amount_str = amount_str.replace(',', 'TEMP')
        amount_str = amount_str.replace('.', decimal_sep)
        amount_str = amount_str.replace('TEMP', thousands_sep)
    
    # Agregar símbolo de moneda
    if symbol_first:
        if currency == 'COP':
            return f"{symbol}{amount_str.split(decimal_sep)[0]}"  # COP sin decimales
        elif currency == 'MXN':
            return f"{symbol}{amount_str} {currency}"
        else:
            return f"{symbol}{amount_str}"
    else:
        return f"{amount_str} {symbol}"


def generate_transaction(transaction_id: Optional[str] = None) -> Dict[str, Any]:
    """
    Genera un registro de transacción individual.
    
    Args:
        transaction_id: ID opcional para generar duplicados
        
    Returns:
        Diccionario con los datos de la transacción
    """
    # Generar o usar ID proporcionado
    record_id = transaction_id if transaction_id else str(uuid.uuid4())
    
    # Generar timestamp con formato mezclado
    dt = generate_random_timestamp()
    use_iso = random.random() < ISO_FORMAT_RATE
    timestamp = format_timestamp(dt, use_iso)
    
    # Generar amount con posibilidad de nulo
    if random.random() < NULL_AMOUNT_RATE:
        amount_str = None if random.random() < 0.5 else ""
    else:
        amount = round(random.uniform(10, 50000), 2)
        amount_str = format_amount(amount)
    
    # Generar datos del cliente (nested JSON)
    client_details = {
        "email": fake.email(),
        "ip_address": fake.ipv4(),
        "device": random.choice(DEVICES)
    }
    
    # Generar metadata con posibilidad de nulo
    metadata = random.choice(METADATA_OPTIONS)
    
    # Construir el registro
    transaction = {
        "id": record_id,
        "timestamp": timestamp,
        "amount_str": amount_str,
        "status": random.choice(STATUSES),
        "client_details": client_details,
        "metadata": metadata
    }
    
    return transaction


def generate_dataset(num_records: int) -> List[Dict[str, Any]]:
    """
    Genera el dataset completo con duplicados intencionales.
    
    Args:
        num_records: Número total de registros a generar
        
    Returns:
        Lista de diccionarios con transacciones
    """
    transactions = []
    duplicate_ids = []
    
    print(f"🔄 Generando {num_records} registros de transacciones...")
    
    # Calcular cuántos duplicados generar
    num_duplicates = int(num_records * DUPLICATE_RATE)
    
    # Generar registros únicos primero
    unique_records = num_records - num_duplicates
    
    for i in range(unique_records):
        transaction = generate_transaction()
        transactions.append(transaction)
        
        # Guardar algunos IDs para duplicar
        if i < num_duplicates:
            duplicate_ids.append(transaction['id'])
        
        # Progreso
        if (i + 1) % 1000 == 0:
            print(f"  ✓ Generados {i + 1}/{unique_records} registros únicos")
    
    # Generar duplicados
    print(f"🔄 Generando {num_duplicates} registros duplicados...")
    for dup_id in duplicate_ids:
        duplicate_transaction = generate_transaction(transaction_id=dup_id)
        transactions.append(duplicate_transaction)
    
    # Mezclar para distribuir duplicados
    random.shuffle(transactions)
    
    return transactions


def analyze_dataset(transactions: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Analiza el dataset generado y retorna estadísticas.
    
    Args:
        transactions: Lista de transacciones
        
    Returns:
        Diccionario con estadísticas del dataset
    """
    df = pd.DataFrame(transactions)
    
    # Contar duplicados
    duplicate_count = df['id'].duplicated().sum()
    unique_ids = df['id'].nunique()
    
    # Contar nulos en amount_str
    null_amounts = df['amount_str'].isna().sum()
    empty_amounts = (df['amount_str'] == "").sum()
    total_null_empty = null_amounts + empty_amounts
    
    # Contar formatos de timestamp
    iso_timestamps = df['timestamp'].str.contains(r'T', na=False).sum()
    local_timestamps = len(df) - iso_timestamps
    
    # Distribución de status
    status_distribution = df['status'].value_counts().to_dict()
    
    # Metadata nulos
    null_metadata = df['metadata'].isna().sum()
    
    stats = {
        "total_records": len(df),
        "unique_ids": unique_ids,
        "duplicate_records": duplicate_count,
        "null_empty_amounts": total_null_empty,
        "iso_timestamps": iso_timestamps,
        "local_timestamps": local_timestamps,
        "status_distribution": status_distribution,
        "null_metadata": null_metadata,
    }
    
    return stats


def print_summary(stats: Dict[str, Any], output_file: str):
    """
    Imprime un resumen detallado de la generación de datos.
    
    Args:
        stats: Diccionario con estadísticas
        output_file: Nombre del archivo de salida
    """
    print("\n" + "="*70)
    print("📊 RESUMEN DE GENERACIÓN DE DATOS")
    print("="*70)
    print(f"\n✅ Total de registros generados: {stats['total_records']:,}")
    print(f"🔑 IDs únicos: {stats['unique_ids']:,}")
    print(f"🔄 Registros duplicados: {stats['duplicate_records']:,} ({stats['duplicate_records']/stats['total_records']*100:.1f}%)")
    print(f"❌ Amounts nulos/vacíos: {stats['null_empty_amounts']:,} ({stats['null_empty_amounts']/stats['total_records']*100:.1f}%)")
    
    print(f"\n📅 Formatos de Timestamp:")
    print(f"  • ISO 8601: {stats['iso_timestamps']:,} ({stats['iso_timestamps']/stats['total_records']*100:.1f}%)")
    print(f"  • Local (DD/MM/YYYY): {stats['local_timestamps']:,} ({stats['local_timestamps']/stats['total_records']*100:.1f}%)")
    
    print(f"\n📈 Distribución de Status:")
    for status, count in sorted(stats['status_distribution'].items()):
        print(f"  • {status}: {count:,} ({count/stats['total_records']*100:.1f}%)")
    
    print(f"\n📝 Metadata nulos: {stats['null_metadata']:,} ({stats['null_metadata']/stats['total_records']*100:.1f}%)")
    
    print(f"\n💾 Archivo generado: {output_file}")
    print("="*70 + "\n")


def main():
    """Función principal del script."""
    output_file = "raw_transactions.json"
    
    print("\n" + "="*70)
    print("🚀 GENERADOR DE DATOS FINANCIEROS - SaaS Testing")
    print("="*70 + "\n")
    
    # Generar dataset
    transactions = generate_dataset(NUM_RECORDS)
    
    # Guardar a JSON
    print(f"\n💾 Guardando datos en {output_file}...")
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(transactions, f, ensure_ascii=False, indent=2)
    print(f"  ✓ Archivo guardado exitosamente")
    
    # Analizar y mostrar resumen
    stats = analyze_dataset(transactions)
    print_summary(stats, output_file)
    
    print("✨ Proceso completado exitosamente!\n")


if __name__ == "__main__":
    main()
```

## Nombre del Archivo: requirements.txt

```text
faker==22.6.0
pandas==2.1.4
sqlalchemy==2.0.25
psycopg2-binary==2.9.9
python-dotenv==1.0.0
streamlit==1.31.0
plotly==5.18.0
```

## Nombre del Archivo: run_dashboard.sh

```bash
#!/bin/bash

# Script para ejecutar el dashboard de Streamlit
# Author: Senior BI Developer

echo "🚀 Iniciando SaaS Financial Intelligence Dashboard..."
echo ""

# Verificar si streamlit está instalado
if ! command -v streamlit &> /dev/null
then
    echo "❌ Streamlit no está instalado."
    echo "📦 Instala las dependencias con: pip3 install streamlit plotly"
    exit 1
fi

# Verificar si existe el archivo .env
if [ ! -f .env ]; then
    echo "⚠️  Archivo .env no encontrado."
    echo "Por favor, crea un archivo .env con tu DATABASE_URL"
    exit 1
fi

# Ejecutar Streamlit
echo "✅ Iniciando dashboard en http://localhost:8501"
echo ""
streamlit run app.py
```

## Nombre del Archivo: test_etl_transformations.py

```python
"""
Script de prueba para el ETL Pipeline (sin conexión a base de datos).
Demuestra las transformaciones de datos sin necesidad de PostgreSQL.

Author: Senior Data Engineer
Date: 2026-01-31
"""

import json
import pandas as pd
from etl_pipeline import ETLPipeline


def test_transformations():
    """Prueba las transformaciones del ETL sin cargar a base de datos."""
    
    print("\n" + "="*70)
    print("🧪 TEST: ETL TRANSFORMATIONS (Sin conexión a DB)")
    print("="*70)
    
    # Crear instancia del pipeline (sin conectar a DB)
    pipeline = ETLPipeline('raw_transactions.json', 'dummy_url')
    
    # 1. Cargar JSON
    df = pipeline.load_json()
    print(f"\n📊 Muestra de datos CRUDOS (primeras 3 filas):")
    print("-" * 70)
    
    # Mostrar algunos registros crudos
    for idx, row in df.head(3).iterrows():
        print(f"\nRegistro {idx + 1}:")
        print(f"  ID: {row['id']}")
        print(f"  Timestamp (crudo): {row['timestamp']}")
        print(f"  Amount (crudo): {row['amount_str']}")
        print(f"  Status: {row['status']}")
        print(f"  Client details: {row['client_details']}")
    
    # 2. Aplicar transformaciones
    df_clean = pipeline.transform(df)
    
    # 3. Mostrar resultados
    print("\n" + "="*70)
    print("✨ DATOS TRANSFORMADOS (primeras 5 filas)")
    print("="*70 + "\n")
    
    # Configurar pandas para mejor visualización
    pd.set_option('display.max_columns', None)
    pd.set_option('display.width', None)
    pd.set_option('display.max_colwidth', 50)
    
    print(df_clean.head(5).to_string(index=False))
    
    # 4. Estadísticas adicionales
    print("\n" + "="*70)
    print("📊 ESTADÍSTICAS DE TRANSFORMACIÓN")
    print("="*70)
    
    print(f"\n💰 Distribución por moneda:")
    currency_stats = df_clean.groupby('currency').agg({
        'amount': ['count', 'sum', 'mean', 'min', 'max']
    }).round(2)
    print(currency_stats)
    
    print(f"\n📈 Distribución por status:")
    status_stats = df_clean['status'].value_counts()
    print(status_stats)
    
    print(f"\n📱 Distribución por dispositivo:")
    device_stats = df_clean['client_device'].value_counts()
    print(device_stats)
    
    print(f"\n📅 Rango de fechas:")
    print(f"  • Fecha más antigua: {df_clean['timestamp'].min()}")
    print(f"  • Fecha más reciente: {df_clean['timestamp'].max()}")
    
    # 5. Calidad de datos
    print("\n" + "="*70)
    print("✅ VALIDACIÓN DE CALIDAD DE DATOS")
    print("="*70)
    
    print(f"\n🔍 Valores nulos por columna:")
    null_counts = df_clean.isnull().sum()
    for col, count in null_counts.items():
        if count > 0:
            print(f"  • {col}: {count} ({count/len(df_clean)*100:.2f}%)")
    
    if null_counts.sum() == 0:
        print("  ✅ No hay valores nulos en el dataset transformado")
    
    print(f"\n🔑 Duplicados por ID:")
    duplicates = df_clean['id'].duplicated().sum()
    if duplicates == 0:
        print("  ✅ No hay duplicados (correctamente eliminados)")
    else:
        print(f"  ⚠️  {duplicates} duplicados encontrados")
    
    print(f"\n💵 Validación de montos:")
    print(f"  • Montos negativos: {(df_clean['amount'] < 0).sum()}")
    print(f"  • Montos = 0: {(df_clean['amount'] == 0).sum()}")
    print(f"  • Montos positivos: {(df_clean['amount'] > 0).sum()}")
    print(f"  • Monto promedio: ${df_clean['amount'].mean():.2f}")
    print(f"  • Monto total: ${df_clean['amount'].sum():,.2f}")
    
    # 6. Guardar sample transformado
    sample_output = 'transformed_sample.json'
    df_clean.head(100).to_json(sample_output, orient='records', indent=2, date_format='iso')
    print(f"\n💾 Muestra transformada guardada en: {sample_output}")
    
    # 7. Resumen final
    pipeline.print_summary()
    
    print("✨ Test de transformaciones completado exitosamente!\n")
    
    return df_clean


if __name__ == "__main__":
    test_transformations()
```

## Nombre del Archivo: verify_database.py

```python
"""
Script para verificar los datos cargados en PostgreSQL.

Author: Senior Data Engineer
Date: 2026-01-31
"""

import os
import pandas as pd
from dotenv import load_dotenv
from sqlalchemy import create_engine, text

load_dotenv()

def verify_data():
    """Verifica los datos en PostgreSQL."""
    
    DATABASE_URL = os.getenv('DATABASE_URL')
    
    if not DATABASE_URL:
        print("❌ Error: DATABASE_URL no configurado")
        return
    
    print("\n" + "="*70)
    print("🔍 VERIFICACIÓN DE DATOS EN POSTGRESQL")
    print("="*70)
    
    # Conectar a la base de datos
    engine = create_engine(DATABASE_URL)
    
    try:
        # 1. Contar registros totales
        with engine.connect() as conn:
            result = conn.execute(text("SELECT COUNT(*) FROM transactions"))
            total = result.fetchone()[0]
            print(f"\n📊 Total de registros: {total:,}")
        
        # 2. Mostrar primeros 5 registros
        print("\n📋 Primeros 5 registros:")
        print("-" * 70)
        df = pd.read_sql("SELECT * FROM transactions LIMIT 5", engine)
        pd.set_option('display.max_columns', None)
        pd.set_option('display.width', None)
        print(df.to_string(index=False))
        
        # 3. Estadísticas por moneda
        print("\n\n💰 Estadísticas por Moneda:")
        print("-" * 70)
        query = """
        SELECT 
            currency,
            COUNT(*) as count,
            ROUND(AVG(amount), 2) as avg_amount,
            ROUND(MIN(amount), 2) as min_amount,
            ROUND(MAX(amount), 2) as max_amount,
            ROUND(SUM(amount), 2) as total_amount
        FROM transactions
        GROUP BY currency
        ORDER BY count DESC
        """
        df_stats = pd.read_sql(query, engine)
        print(df_stats.to_string(index=False))
        
        # 4. Distribución por status
        print("\n\n📈 Distribución por Status:")
        print("-" * 70)
        query = "SELECT status, COUNT(*) as count FROM transactions GROUP BY status ORDER BY count DESC"
        df_status = pd.read_sql(query, engine)
        print(df_status.to_string(index=False))
        
        # 5. Distribución por dispositivo
        print("\n\n📱 Distribución por Dispositivo:")
        print("-" * 70)
        query = "SELECT client_device, COUNT(*) as count FROM transactions GROUP BY client_device ORDER BY count DESC"
        df_device = pd.read_sql(query, engine)
        print(df_device.to_string(index=False))
        
        # 6. Rango de fechas
        print("\n\n📅 Rango de Fechas:")
        print("-" * 70)
        query = "SELECT MIN(timestamp) as earliest, MAX(timestamp) as latest FROM transactions"
        df_dates = pd.read_sql(query, engine)
        print(f"  • Fecha más antigua: {df_dates['earliest'][0]}")
        print(f"  • Fecha más reciente: {df_dates['latest'][0]}")
        
        # 7. Top 10 transacciones más grandes
        print("\n\n💎 Top 10 Transacciones Más Grandes:")
        print("-" * 70)
        query = """
        SELECT id, timestamp, amount, currency, status, client_email
        FROM transactions
        ORDER BY amount DESC
        LIMIT 10
        """
        df_top = pd.read_sql(query, engine)
        print(df_top.to_string(index=False))
        
        print("\n" + "="*70)
        print("✅ Verificación completada exitosamente")
        print("="*70 + "\n")
        
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        engine.dispose()


if __name__ == "__main__":
    verify_data()
```

