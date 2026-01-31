# 📊 Guía Rápida del Dashboard

## 🚀 Inicio Rápido

### 1. Instalación de Dependencias

```bash
pip3 install streamlit plotly
```

Si tienes problemas con SSL:
```bash
pip3 install --trusted-host pypi.org --trusted-host files.pythonhosted.org streamlit plotly
```

### 2. Configuración

Asegúrate de tener el archivo `.env` con tu DATABASE_URL:
```bash
DATABASE_URL=postgresql://user:password@host:port/database
```

### 3. Ejecutar el Dashboard

**Opción A: Script automático**
```bash
./run_dashboard.sh
```

**Opción B: Comando directo**
```bash
streamlit run app.py
```

El dashboard se abrirá en: **http://localhost:8501**

---

## 📈 Características del Dashboard

### 🎯 KPIs Principales (Arriba)

Tres métricas clave en tiempo real:

1. **📊 Total Transacciones**: Número total de transacciones
2. **💰 Volumen Total**: Suma total de todas las transacciones (con formato K/M/B)
3. **🎯 Ticket Promedio**: Valor promedio por transacción

### 🔍 Filtros Interactivos (Sidebar)

**Filtros disponibles:**

1. **💵 Monedas** (Multiselect)
   - USD (Dólares)
   - EUR (Euros)
   - GBP (Libras)
   - COP (Pesos Colombianos)
   - Por defecto: Todas seleccionadas

2. **📊 Status** (Multiselect)
   - COMPLETED (Completadas)
   - FAILED (Fallidas)
   - PENDING (Pendientes)
   - REFUNDED (Reembolsadas)
   - Por defecto: Todas seleccionadas

3. **📅 Rango de Fechas** (Date picker)
   - Selecciona inicio y fin
   - Por defecto: Todo el rango disponible

**Nota:** Todos los gráficos y métricas se actualizan automáticamente al cambiar los filtros.

---

## 📊 Visualizaciones

### 1. 💵 Volumen de Ventas por Moneda (Gráfico de Barras)

- **Qué muestra**: Volumen total de transacciones agrupado por moneda
- **Colores**: Cada moneda tiene su color distintivo
- **Interacción**: Hover para ver el valor exacto
- **Uso**: Identificar qué moneda genera más volumen

### 2. 📊 Distribución de Status (Gráfico Donut)

- **Qué muestra**: Porcentaje de transacciones por estado
- **Colores**:
  - Verde: COMPLETED ✅
  - Rojo: FAILED ❌
  - Naranja: PENDING ⏳
  - Morado: REFUNDED 💰
- **Interacción**: Hover para ver cantidad y porcentaje
- **Uso**: Monitorear tasa de éxito y fallos

### 3. 📈 Tendencia de Transacciones (Gráfico de Línea Dual)

- **Qué muestra**: 
  - Eje Y izquierdo (azul): Volumen total por día
  - Eje Y derecho (naranja): Número de transacciones por día
- **Interacción**: Hover para ver ambos valores
- **Uso**: Identificar tendencias temporales y estacionalidad

### 4. 📱 Transacciones por Dispositivo (Barras Horizontales)

- **Qué muestra**: Cantidad de transacciones por tipo de dispositivo
- **Colores**:
  - Naranja: Mobile 📱
  - Azul: Desktop 💻
- **Uso**: Entender el comportamiento por plataforma

---

## 📋 Tabla de Datos

**Ubicación**: Final del dashboard

**Características:**
- Muestra las últimas 100 transacciones
- Columnas visibles:
  - Fecha/Hora
  - Monto
  - Moneda
  - Status
  - Cliente (email)
  - Dispositivo
- **Scrolleable**: Puedes navegar por todas las filas
- **Ordenable**: Click en headers para ordenar

---

## 📊 Estadísticas Detalladas

Debajo de los gráficos principales encontrarás 4 métricas adicionales:

1. **💵 Transacción Máxima**: El monto más alto registrado
2. **💵 Transacción Mínima**: El monto más bajo registrado
3. **✅ Tasa de Éxito**: % de transacciones completadas
4. **👥 Clientes Únicos**: Número de clientes diferentes

---

## 🎨 Personalización

### Cambiar Colores

Edita el archivo `.streamlit/config.toml`:

```toml
[theme]
primaryColor = "#1f77b4"  # Color principal
backgroundColor = "#ffffff"  # Fondo
secondaryBackgroundColor = "#f0f2f6"  # Fondo secundario
textColor = "#262730"  # Color del texto
```

### Cambiar Puerto

Por defecto usa el puerto 8501. Para cambiarlo:

```bash
streamlit run app.py --server.port 8502
```

O edita `.streamlit/config.toml`:

```toml
[server]
port = 8502
```

---

## 🔄 Cache y Rendimiento

El dashboard usa dos tipos de cache:

1. **@st.cache_data** (TTL: 5 minutos)
   - Cachea los datos de PostgreSQL
   - Se refresca automáticamente cada 5 minutos
   - Puedes forzar refresh con: Ctrl + R (o presiona "C" en el dashboard)

2. **@st.cache_resource**
   - Cachea la conexión a la base de datos
   - Persiste durante toda la sesión

### Limpiar Cache Manualmente

En el dashboard:
1. Click en el menú (☰) arriba a la derecha
2. Selecciona "Clear cache"
3. Click en "Clear cache" nuevamente

---

## 🐛 Troubleshooting

### Error: "DATABASE_URL no configurado"

**Solución**: Verifica que existe el archivo `.env` con:
```bash
DATABASE_URL=postgresql://...
```

### Error: "ModuleNotFoundError: No module named 'streamlit'"

**Solución**: Instala las dependencias:
```bash
pip3 install streamlit plotly
```

### Dashboard muy lento

**Soluciones**:
1. Reduce el rango de fechas en los filtros
2. Selecciona menos monedas/status
3. El cache debería mejorar la velocidad en la segunda carga

### No aparecen datos

**Verificaciones**:
1. Revisa que la base de datos tenga datos:
   ```bash
   python3 verify_database.py
   ```
2. Verifica los filtros en el sidebar
3. Asegúrate de que DATABASE_URL es correcto

---

## 💡 Tips de Uso

1. **Análisis rápido**: Usa los filtros para enfocarte en segmentos específicos
2. **Comparaciones**: Selecciona diferentes monedas para compararlas
3. **Tendencias**: Usa el gráfico de línea para identificar patrones temporales
4. **Export**: Puedes hacer screenshot de los gráficos (hover → icono de cámara)
5. **Mobile**: El dashboard es responsive y funciona en tablets

---

## 🎯 Casos de Uso Comunes

### 1. Análisis de Tasa de Éxito

**Objetivo**: ¿Qué porcentaje de transacciones son exitosas?

**Pasos**:
1. Ve al gráfico donut "Distribución de Status"
2. Observa el porcentaje de COMPLETED (verde)
3. Usa la métrica "Tasa de Éxito" para el valor exacto

### 2. Comparar Monedas

**Objetivo**: ¿Qué moneda genera más volumen?

**Pasos**:
1. Ve al gráfico de barras "Volumen por Moneda"
2. La barra más alta es la moneda dominante
3. Hover para ver valores exactos

### 3. Detectar Tendencias

**Objetivo**: ¿Hay días con más transacciones?

**Pasos**:
1. Ve al gráfico de línea de tendencias
2. Busca picos en la línea naranja (# transacciones)
3. Correlaciona con volumen (línea azul)

### 4. Análisis por Dispositivo

**Objetivo**: ¿Los usuarios prefieren mobile o desktop?

**Pasos**:
1. Ve al gráfico "Transacciones por Dispositivo"
2. Compara las barras horizontales
3. Considera optimizar la plataforma dominante

---

## 📚 Recursos Adicionales

- **Streamlit Docs**: https://docs.streamlit.io
- **Plotly Docs**: https://plotly.com/python/
- **Dashboard Repo**: https://github.com/MiguelAlvarez111/Proyecto-1-SaaS-Financial-Intelligence

---

**¿Preguntas?** Revisa el README.md principal o contacta al equipo de BI.
