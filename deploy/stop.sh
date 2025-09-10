#!/bin/bash

# Script para detener los servicios de la aplicación

echo "🛑 Deteniendo servicios de Riesgos API..."

# Detener servicios
docker-compose down

echo "✅ Servicios detenidos!"
echo ""
echo "🔄 Para iniciar nuevamente:"
echo "   ./deploy/start.sh"
