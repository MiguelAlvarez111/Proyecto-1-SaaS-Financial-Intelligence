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
