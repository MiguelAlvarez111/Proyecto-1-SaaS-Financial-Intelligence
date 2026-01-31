# 💰 SaaS Financial Intelligence - Data Generator

Generador de datos de prueba para sistema financiero SaaS con datos intencionalmente "sucios" para testing y validación.

## 🎯 Características

- **5,000 registros** de transacciones financieras
- **Datos sucios intencionales** (duplicados, nulos, formatos mezclados)
- **Múltiples formatos de moneda** (USD, EUR, COP, GBP, MXN)
- **Timestamps mezclados** (70% ISO 8601, 30% formato local)
- **Estructura anidada** (client_details como JSON nested)

## 📋 Requisitos

- Python 3.8+
- pip

## 🚀 Instalación

```bash
pip install -r requirements.txt
```

O instala las dependencias manualmente:

```bash
pip install faker pandas
```

## 💻 Uso

Ejecuta el script:

```bash
python3 generate_data.py
```

> **Nota para macOS**: Usa `python3` en lugar de `python`

El script generará automáticamente:
- Un archivo `raw_transactions.json` con 5,000 transacciones
- Un resumen detallado en consola con estadísticas

## 📊 Estructura de Datos

Cada registro contiene:

```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "timestamp": "2025-06-15T14:30:45.123456",
  "amount_str": "$1,200.50",
  "status": "COMPLETED",
  "client_details": {
    "email": "user@example.com",
    "ip_address": "192.168.1.1",
    "device": "mobile"
  },
  "metadata": "Cliente VIP - prioridad alta"
}
```

## 🐛 Complejidades Intencionales

El script introduce intencionalmente:

1. **Duplicados (5%)**: IDs repetidos simulando reintentos
2. **Nulos (2%)**: Amounts vacíos o None
3. **Formatos mezclados**:
   - Timestamps: ISO 8601 vs DD/MM/YYYY HH:mm
   - Monedas: $1,200.50, 1.200,50 €, COP 50000, etc.
4. **Metadata variable**: Puede ser null o contener notas

## 📈 Estadísticas Esperadas

- Total registros: 5,000
- IDs únicos: ~4,750
- Duplicados: ~250 (5%)
- Amounts nulos: ~100 (2%)
- ISO timestamps: ~3,500 (70%)
- Local timestamps: ~1,500 (30%)

## 👨‍💻 Autor

Senior Data Engineer
