# SaaS Financial Intelligence

Dashboard de analytics financiero con arquitectura **Next.js (frontend) + FastAPI (backend)** y pipeline ETL para datos de transacciones.

## Estructura del proyecto

```
├── backend/          # API FastAPI (Puerto 8000)
├── frontend/         # App Next.js (Puerto 3000)
├── etl_scripts/      # Scripts ETL y generación de datos
├── requirements.txt  # Dependencias Python para ETL (raíz)
└── README.md
```

## Requisitos

- **Python 3.8+** (backend y ETL)
- **Node.js 18+** (frontend)
- **PostgreSQL** (datos de transacciones)

## Configuración

### 1. Variables de entorno

Crea un archivo **`.env`** en la **raíz del proyecto** con:

```bash
DATABASE_URL=postgresql://usuario:password@host:5432/database
```

Para el frontend, en **`frontend/`** copia el ejemplo y crea **`.env.local`**:

```bash
cd frontend
cp .env.example .env.local
# Opcional: edita .env.local si tu API no corre en localhost:8000
# NEXT_PUBLIC_API_URL=http://localhost:8000
```

---

## Cómo ejecutar la aplicación

### Backend (FastAPI)

```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

API disponible en: **http://localhost:8000**  
Documentación: **http://localhost:8000/docs**

### Frontend (Next.js)

```bash
cd frontend
npm install
npm run dev
```

Dashboard en: **http://localhost:3000**

El frontend consume la API por defecto en **http://localhost:8000**. Si usas otro host/puerto, define `NEXT_PUBLIC_API_URL` en `frontend/.env.local`.

### Orden recomendado

1. Levantar PostgreSQL y tener `DATABASE_URL` en `.env`.
2. (Opcional) Generar y cargar datos con los scripts ETL (ver más abajo).
3. Iniciar el backend: `cd backend && uvicorn main:app --reload --port 8000`.
4. Iniciar el frontend: `cd frontend && npm run dev`.

---

## Scripts ETL (`etl_scripts/`)

Los scripts de generación de datos y carga a PostgreSQL están en **`etl_scripts/`**. Ejecutarlos desde la **raíz del proyecto** (para que encuentren `.env` y `raw_transactions.json` en la raíz).

### Dependencias ETL

Desde la raíz:

```bash
pip install -r requirements.txt
```

O solo para ETL:

```bash
pip install -r etl_scripts/requirements.txt
```

### 1. Generar datos de prueba

Genera `raw_transactions.json` en la raíz (5.000 transacciones con datos “sucios” para testing):

```bash
python3 etl_scripts/generate_data.py
```

### 2. Ejecutar pipeline ETL (cargar a PostgreSQL)

Requiere `DATABASE_URL` en `.env`:

```bash
python3 etl_scripts/etl_pipeline.py
```

### 3. Probar transformaciones (sin base de datos)

```bash
python3 etl_scripts/test_etl_transformations.py
```

### 4. Verificar datos en PostgreSQL

```bash
python3 etl_scripts/verify_database.py
```

---

## API (FastAPI)

- **GET /** — Health check  
- **GET /api/dashboard** — Datos del dashboard (KPIs, volumen diario, status, monedas, dispositivos, transacciones recientes)  
- **GET /api/transactions** — Listado paginado de transacciones  
- **GET /api/filters** — Opciones de filtros (monedas, status, rango de fechas)

Query params opcionales en `/api/dashboard`: `currencies`, `statuses`, `start_date`, `end_date` (formato `YYYY-MM-DD`).

---

## Tecnologías

- **Frontend:** Next.js, React, Tailwind CSS, Recharts, Framer Motion  
- **Backend:** FastAPI, SQLAlchemy, Pandas, Pydantic  
- **Datos:** PostgreSQL  
- **ETL:** Python, Pandas, Faker (generación), SQLAlchemy (carga)
