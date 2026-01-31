#!/bin/bash

# Script para ejecutar el dashboard de Streamlit
# Author: Senior BI Developer

echo "🚀 Iniciando SaaS Financial Intelligence Dashboard..."
echo ""

# Verificar si streamlit está instalado
if ! command -v streamlit &> /dev/null
then
    echo "❌ Streamlit no está instalado."
    echo "📦 Instala las dependencias con: pip3 install streamlit plotly"
    exit 1
fi

# Verificar si existe el archivo .env
if [ ! -f .env ]; then
    echo "⚠️  Archivo .env no encontrado."
    echo "Por favor, crea un archivo .env con tu DATABASE_URL"
    exit 1
fi

# Ejecutar Streamlit
echo "✅ Iniciando dashboard en http://localhost:8501"
echo ""
streamlit run app.py
