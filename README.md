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

---

## 🔄 ETL Pipeline

### Pipeline de Transformación y Carga

El script `etl_pipeline.py` procesa los datos crudos y los carga a PostgreSQL.

### 🎯 Funcionalidades

1. **Carga de datos**: Lee `raw_transactions.json`
2. **Flattening**: Desanida campos nested (`client_details`)
3. **Limpieza de timestamps**: Convierte formatos mixtos (ISO 8601 y DD/MM/YYYY) a UTC
4. **Parsing inteligente de monedas**: 
   - Detecta automáticamente el formato (US vs Europeo)
   - Extrae montos numéricos y códigos de moneda
   - Soporta: USD, EUR, GBP, COP
5. **Deduplicación**: Elimina duplicados por ID (mantiene última ocurrencia)
6. **Carga a PostgreSQL**: Con tipos de datos SQL explícitos

### 📋 Configuración

1. Crea un archivo `.env` en la raíz del proyecto:

```bash
DATABASE_URL=postgresql://usuario:password@host:5432/database
```

**⚠️ Importante para Railway:**
- La URL con hostname `postgres.railway.internal` solo funciona **dentro** de los servicios de Railway
- Para conectarte desde tu máquina local, necesitas la **URL pública** de PostgreSQL
- Ve a tu proyecto en Railway → PostgreSQL → Variables → Busca `DATABASE_PUBLIC_URL` o similar

2. Instala las dependencias adicionales:

```bash
pip3 install sqlalchemy psycopg2-binary python-dotenv
```

O usa el requirements.txt actualizado:

```bash
pip3 install -r requirements.txt
```

### 💻 Ejecución

**Opción 1: Pipeline completo (requiere PostgreSQL)**
```bash
python3 etl_pipeline.py
```

**Opción 2: Solo probar transformaciones (sin DB)**
```bash
python3 test_etl_transformations.py
```

Este script de prueba ejecuta todas las transformaciones y muestra:
- Muestra de datos antes/después
- Estadísticas de limpieza
- Validación de calidad de datos
- Guarda una muestra transformada en `transformed_sample.json`

**Opción 3: Verificar datos en PostgreSQL**
```bash
python3 verify_database.py
```

Este script consulta la base de datos y muestra:
- Total de registros cargados
- Estadísticas por moneda, status y dispositivo
- Top 10 transacciones más grandes
- Rango de fechas

### 📊 Output Esperado

El pipeline mostrará:
- Total de registros leídos
- Registros eliminados (nulos, duplicados)
- Distribución de monedas detectadas
- Registros cargados exitosamente a PostgreSQL
- Tasa de éxito del proceso

### 🗄️ Tabla PostgreSQL

**Nombre**: `transactions`

**Columnas**:
- `id` (VARCHAR 36): ID único de transacción
- `timestamp` (TIMESTAMP): Fecha/hora en UTC
- `amount` (NUMERIC 15,2): Monto numérico
- `currency` (VARCHAR 3): Código ISO de moneda
- `status` (VARCHAR 20): Estado de la transacción
- `client_email` (VARCHAR 255): Email del cliente
- `client_ip` (VARCHAR 45): IP del cliente
- `client_device` (VARCHAR 20): Tipo de dispositivo
- `metadata` (VARCHAR 500): Notas adicionales

---

## 📊 Dashboard Interactivo v2.0 (Streamlit)

### Dashboard Profesional de Business Intelligence

El archivo `app.py` contiene un dashboard interactivo profesional con arquitectura mejorada, normalización de monedas y UI/UX de nivel empresarial.

### 🎯 Características del Dashboard v2.0

**✨ NUEVAS MEJORAS:**
- **💱 Normalización de Monedas**: Todos los KPIs globales usan USD normalizado con tasas fijas
- **📊 KPIs con Deltas**: Comparación automática vs período anterior (+/-% change)
- **🎨 Estructura con Tabs**: Navegación organizada en 3 secciones
- **📋 Tabla Avanzada**: Column config con formato profesional
- **🎨 Colores Consistentes**: Paleta unificada en todas las visualizaciones

**📈 Visualizaciones:**
- KPIs principales con deltas comparativos (mes actual vs anterior)
- Gráfico de tendencia temporal con doble eje Y
- Gráfico donut de distribución de status
- Gráfico de barras: Volumen por moneda (en moneda original)
- Gráfico de barras: Volumen por dispositivo (normalizado USD)
- Heatmap: Transacciones por día y hora
- Tabla interactiva avanzada con últimas 100 transacciones

**🔍 Filtros Interactivos:**
- Multiselect de Monedas (USD, EUR, GBP, COP)
- Multiselect de Status (COMPLETED, FAILED, PENDING, REFUNDED)
- Selector de rango de fechas
- Todos los gráficos reaccionan en tiempo real

**⚡ Optimización y UX:**
- Cache optimizado (@st.cache_data con TTL 5min)
- Cache de conexión (@st.cache_resource)
- Layout wide para máxima visualización
- CSS personalizado con gradientes y sombras
- Tabs para mejor organización del contenido
- Descarga de datos en CSV

### 📋 Instalación de Dependencias

```bash
pip3 install streamlit plotly
```

O instala todas las dependencias:

```bash
pip3 install -r requirements.txt
```

### 💻 Ejecución del Dashboard

**Opción 1: Usando el script de inicio**
```bash
./run_dashboard.sh
```

**Opción 2: Comando directo**
```bash
streamlit run app.py
```

El dashboard se abrirá automáticamente en tu navegador en: **http://localhost:8501**

### 🎨 Características Técnicas

- **Framework**: Streamlit 1.31.0
- **Gráficos**: Plotly Express & Plotly Graph Objects
- **Datos**: PostgreSQL vía SQLAlchemy
- **Estilo**: CSS personalizado con diseño moderno
- **Responsive**: Layout adaptable (wide mode)

---

## 👨‍💻 Autores

- **Data Engineer**: Generación y ETL de datos
- **BI Developer**: Dashboard y visualizaciones
