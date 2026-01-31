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
