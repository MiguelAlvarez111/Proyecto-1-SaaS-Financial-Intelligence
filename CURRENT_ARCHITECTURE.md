# Reporte de Arquitectura Actual — Financial Intelligence

Documento para que una tercera parte (p. ej. otra IA) entienda exactamente qué está construido, cómo funciona y cómo se ve el sistema. **Solo describe lo que ya existe en el código; no incluye código nuevo.**

---

## 1. Resumen del Stack Tecnológico

### Backend
- **Framework:** FastAPI (v5.0.0 en la API).
- **Base de datos:** PostgreSQL; acceso vía **SQLAlchemy** (`create_engine`, `pool_pre_ping=True`).
- **Datos en memoria:** **Pandas** para cargar transacciones desde la BD, filtrar, agrupar y calcular KPIs y agregados.
- **Validación y modelos:** **Pydantic** (BaseModel) para los esquemas de request/response.
- **Configuración:** **python-dotenv**; se carga `.env` desde la raíz del proyecto.
- **Servidor:** **Uvicorn** (ASGI); dependencia `psycopg2-binary` para el driver de PostgreSQL.

### Frontend
- **Framework:** **Next.js 16** (App Router), **React 19**.
- **Estilos:** **Tailwind CSS v4** (`@tailwindcss/postcss`, `tailwindcss`); tema oscuro y utilidades custom en `globals.css` (glass-card, metric-card, input-glass, etc.). **No se usa Tremor.**
- **Gráficos:** **Recharts** (AreaChart, BarChart, PieChart, Tooltip, ResponsiveContainer, etc.) en componentes propios dentro de `src/components/charts/`.
- **Animaciones:** **Framer Motion** (motion.div, motion.header, etc.) en layout y tarjetas.
- **Iconos:** **@heroicons/react** (outline y solid).
- **Utilidades:** **clsx** y **tailwind-merge** (función `cn` en `src/lib/utils.ts`), **date-fns** (no usado de forma visible en el reporte; puede usarse en utils), **lucide-react** (en dependencias; uso concreto no revisado en este reporte).

**Conclusión:** Backend = FastAPI + SQLAlchemy + Pandas + Pydantic. Frontend = Next.js + Tailwind + **Recharts** (no Tremor) + Framer Motion + Heroicons.

---

## 2. Arquitectura del Backend (Lógica de Negocio)

### Conexión a la base de datos
- **Variable de entorno:** `DATABASE_URL` (ej. `postgresql://user:pass@host:5432/db`). Se lee desde `.env` en la raíz del proyecto.
- **Función `get_engine()`:** Crea el motor SQLAlchemy con `create_engine(database_url, pool_pre_ping=True)`. Si `DATABASE_URL` no está definida, responde con HTTP 500.
- **Función `load_transactions()`:** Ejecuta un `SELECT` sobre la tabla `transactions` (columnas: id, timestamp, amount, currency, status, client_email, client_ip, client_device, metadata), ordenado por `timestamp DESC`. Filtra filas con `amount <= MIN_VALID_AMOUNT` (0.01), convierte `timestamp` a datetime, **calcula en memoria la columna `amount_usd`** usando un diccionario fijo de tasas (`EXCHANGE_RATES`: USD 1.0, EUR 1.08, GBP 1.27, COP 0.00025), y añade columnas derivadas `date` y `year_month`. Devuelve un `DataFrame` de Pandas.

### Modelo de datos (Schema)
- **Transaction:** id (str), timestamp (datetime), amount (float), currency (str), status (str), amount_usd (float), client_email (str), client_device (str).
- **KPIData:** totalVolume, totalTransactions, avgTicket, successRate, volumeDelta, transactionsDelta, avgTicketDelta (todos numéricos).
- **DailyVolume:** date (str, formato "Jan DD"), volume (float), count (int).
- **StatusDistribution:** status (str), count (int), percentage (float).
- **CurrencyVolume:** currency (str), amount (float), count (int).
- **DeviceVolume:** device (str), amount (float), percentage (float).
- **DashboardData:** agrupa kpis, dailyVolume, statusDistribution, currencyVolume, deviceVolume, recentTransactions (lista de Transaction), lastUpdated (datetime).

### Transformación “al vuelo”
- **Normalización a USD:** En `load_transactions()`, cada fila obtiene `amount_usd = amount * EXCHANGE_RATES[currency]` (monedas no definidas se tratan como 1.0).
- **Deltas mes a mes:** La función `calculate_delta(df, metric_col)` compara el último periodo (`year_month`) con el anterior y devuelve el porcentaje de cambio; se usa para volumen, número de transacciones y ticket medio.
- **Agregados:** Tras aplicar filtros opcionales (monedas, estados, rango de fechas), el backend agrupa con Pandas para generar dailyVolume (por fecha), statusDistribution (por status), currencyVolume (por moneda, amount en moneda original), deviceVolume (por client_device, amount en USD), y recentTransactions (primeras 50 filas).

### Endpoints principales (`main.py`)

| Método y ruta | Descripción | Datos que devuelve |
|---------------|-------------|--------------------|
| `GET /` | Health check | `{ "status": "healthy", "version": "5.0.0" }` |
| `GET /api/dashboard` | Datos completos del dashboard (con filtros opcionales) | **DashboardData** (KPIs, dailyVolume, statusDistribution, currencyVolume, deviceVolume, recentTransactions, lastUpdated). Query params: `currencies`, `statuses`, `start_date`, `end_date`. |
| `GET /api/transactions` | Listado paginado de transacciones | Lista de **Transaction**. Query params: `limit` (1–10000), `offset`. No aplica filtros por moneda/estado en el backend actual. |
| `GET /api/filters` | Opciones disponibles para filtros | Objeto con `currencies` (lista), `statuses` (lista), `dateRange` (min/max en ISO). |

Errores típicos: 404 si no hay transacciones o no hay datos que cumplan filtros; 500 si falla la BD o no está configurada `DATABASE_URL`.

---

## 3. Arquitectura del Frontend (UX/UI y Distribución)

### Estructura de la aplicación
- **App Router:** `src/app/layout.tsx` (HTML, body, importa `globals.css`), `page.tsx` (página principal del dashboard, "use client"), `loading.tsx` (estado de carga con mensaje “Loading…”).
- **Página principal (`page.tsx`):** Contenedor en flex horizontal: **Sidebar** fijo a la izquierda; a la derecha un bloque flex vertical con **Header** arriba y **main** debajo. Dentro de `main`: primero la **FilterBar**, luego avisos opcionales (error de API o “demo data”), y después el contenido según la pestaña activa (**overview**, **analysis**, **transactions**).

### Distribución visual del dashboard

1. **Sidebar (izquierda, ancho fijo ~256px)**  
   - Logo “Financial Intelligence” con icono.  
   - Sección DASHBOARD: tres ítems de navegación — Overview, Analysis, Transactions (uno activo resaltado).  
   - Sección ACTIONS: Refresh Data, Export CSV.  
   - Footer: Settings, texto “v5.0 Gold Master”, “Next.js + Framer Motion”.  
   - Estilos: clase `sidebar`, fondos oscuros, bordes sutiles; animaciones con Framer Motion.

2. **Header (arriba del contenido principal)**  
   - Izquierda: título “Dashboard”, subtítulo “Real-time transaction analytics”.  
   - Derecha: barra de búsqueda (“Search transactions…” con icono de lupa), indicador “Live • X ago” (getTimeAgo(lastUpdated)), icono de notificaciones, avatar “MA”.  
   - Estilos: borde inferior, fondo semitransparente, altura fija.

3. **Área principal (main)**  
   - **FilterBar** (arriba, colapsable): etiqueta “Filtros”, chips para Moneda (USD, EUR, GBP, COP), chips para Estado (COMPLETED, FAILED, PENDING, REFUNDED), dos inputs de fecha (desde/hasta), botón “Limpiar filtros” cuando hay filtros activos.  
   - Avisos: si hay error de API, mensaje tipo “Backend no disponible…”; si no hay error pero no hay datos de API, mensaje tipo “Connect the backend… Showing demo data.”  
   - Contenido según pestaña:

**Pestaña Overview**  
- **Fila de 4 tarjetas KPI** (grid responsive 1/2/4 columnas): Total Volume, Transactions, Avg Ticket, Success Rate. Cada una muestra valor principal y delta “vs last month” (flecha y color). Componente: **MetricCard** (Framer Motion, clases tipo metric-card, glass).  
- **Fila de 2 gráficos** (grid 2 columnas en xl):  
  - **Volumen diario (USD):** gráfico de área (Recharts AreaChart). Componente: **AreaChartComponent**.  
  - **Distribución por estado:** donut (Recharts PieChart con innerRadius). Componente: **DonutChart**; en el centro muestra total de transacciones.  

**Pestaña Analysis**  
- Texto explicativo: “Desglose por moneda y dispositivo. Para KPIs y tendencia temporal, usa Overview.”  
- **Fila de 2 gráficos de barras horizontales** (grid 2 columnas en xl): Volumen por moneda, Volumen por dispositivo. Componente: **HorizontalBarChart** (Recharts BarChart layout vertical).  

**Pestaña Transactions**  
- **Tabla de transacciones:** columnas Date/Time, Amount, Currency, Amount USD, Status, Device. Componente: **TransactionTable**; estilos tipo `data-table`, badges de estado (COMPLETED, FAILED, etc.). No es Tremor; es una tabla nativa con estilos en `globals.css`.

### Componentes visuales utilizados
- **Tarjetas KPI:** Componente propio **MetricCard** (no Tremor Cards); fondo glass, borde, animaciones Framer Motion, indicador de delta.  
- **Gráficos:** Todos con **Recharts** — AreaChart (volumen diario), PieChart (donut de estados), BarChart horizontal (moneda y dispositivo). Tooltips custom; en barras se desactiva el cursor gris con `cursor={false}`.  
- **Tabla:** **TransactionTable**; `<table>` con clases `.data-table`, celdas, badges de estado.  
- **Filtros:** **FilterBar**; chips clicables (no Tremor), inputs `type="date"`, botón limpiar.  
- **Layout:** **Sidebar** y **Header** propios; iconos de **Heroicons**.  

**Resumen:** No hay Tremor. Se usan Recharts para gráficos, componentes propios para tarjetas y tabla, Tailwind + clases globales para el aspecto, y Framer Motion para animaciones.

### Datos mostrados
- Los datos vienen del hook **useDashboard(filters)** que llama a `GET /api/dashboard` con query params derivados de `filters` (currencies, statuses, start_date, end_date). Si la petición falla, la página usa **DEMO_DATA** definido en `page.tsx` (KPIs, series, donut, barras y tabla de ejemplo) para que el dashboard siempre sea usable. El mismo `displayData` se usa para Overview, Analysis y Transactions (recentTransactions para la tabla).

---

## 4. Flujo de Datos

1. **PostgreSQL**  
   La tabla `transactions` almacena id, timestamp, amount, currency, status, client_email, client_ip, client_device, metadata.

2. **FastAPI (backend)**  
   - `load_transactions()` usa SQLAlchemy para leer la tabla y Pandas para construir un DataFrame.  
   - Se filtra por `amount > MIN_VALID_AMOUNT`, se convierte timestamp, se añade **amount_usd** con `EXCHANGE_RATES` y columnas `date` y `year_month`.  
   - Para `GET /api/dashboard`, se aplican filtros opcionales (currencies, statuses, start_date, end_date) sobre el DataFrame, se calculan KPIs, agregados (diario, por estado, por moneda, por dispositivo) y las últimas 50 transacciones, y se devuelve un JSON que cumple el schema **DashboardData**.  
   - Para `GET /api/transactions`, se devuelve un slice del DataFrame según `limit` y `offset` como lista de **Transaction** (sin filtros por moneda/estado en el backend actual).

3. **Next.js (frontend)**  
   - **useDashboard(filters)** hace `fetch` a `NEXT_PUBLIC_API_URL/api/dashboard` (por defecto `http://localhost:8000`) con los query params construidos desde `filters`.  
   - La respuesta JSON se guarda en estado (`data`, `lastUpdated`); en caso de error se guarda el mensaje y `data` queda null.  
   - **page.tsx** usa `displayData = data ?? DEMO_DATA`, así que siempre hay datos para renderizar. Los filtros se pasan desde el estado local (FilterBar) al hook, por lo que cambiar filtros dispara un nuevo fetch.  
   - **Export CSV:** `exportTransactions(filters)` llama a `GET /api/transactions` con `limit=10000`, opcionalmente currencies/statuses (el backend actual no los usa), convierte la respuesta JSON a CSV en el cliente y dispara la descarga del archivo.

4. **Usuario**  
   - Ve el dashboard (Overview, Analysis o Transactions) con datos de la API o con datos de demo.  
   - Puede cambiar filtros (moneda, estado, fechas) y refrescar datos o exportar CSV desde el Sidebar.

En conjunto: **PostgreSQL → SQLAlchemy/Pandas (y transformación USD + filtros) → FastAPI (JSON) → fetch en Next.js → estado React → componentes (Recharts, MetricCard, TransactionTable, etc.) → usuario.**
