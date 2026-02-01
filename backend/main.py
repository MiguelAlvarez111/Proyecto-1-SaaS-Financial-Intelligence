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

# Cargar .env desde la raíz del proyecto
_load_env_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".env")
load_dotenv(_load_env_path)

# ==================== CONFIGURATION ====================

app = FastAPI(
    title="Financial Intelligence API",
    description="Real-time transaction analytics API",
    version="5.0.0"
)

# CORS for Next.js frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "https://proud-essence-production-fc99.up.railway.app",
    ],
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
    limit: int = Query(50, ge=1, le=10000),
    offset: int = Query(0, ge=0),
):
    """Get paginated transactions. Max 10000 for export."""
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
