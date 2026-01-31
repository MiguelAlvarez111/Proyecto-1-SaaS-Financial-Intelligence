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
