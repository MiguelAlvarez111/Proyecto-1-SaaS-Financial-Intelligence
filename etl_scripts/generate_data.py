"""
Script de generación de datos de prueba para sistema financiero SaaS.
Genera 5,000 transacciones con datos intencionalmente "sucios" para testing.

Author: Senior Data Engineer
Date: 2026-01-31
"""

import json
import os
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
    _script_dir = os.path.dirname(os.path.abspath(__file__))
    _project_root = os.path.dirname(_script_dir)
    output_file = os.path.join(_project_root, "raw_transactions.json")
    
    print("\n" + "="*70)
    print("🚀 GENERADOR DE DATOS FINANCIEROS - SaaS Testing")
    print("="*70 + "\n")
    
    # Generar dataset
    transactions = generate_dataset(NUM_RECORDS)
    
    # Guardar a JSON (en la raíz del proyecto)
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
