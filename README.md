# API de Gestión de Riesgos

API REST simple para gestionar riesgos empresariales.

## Estructura del Proyecto

```
RiesgosBE/
├── app.py              # Aplicación principal
├── config.py           # Configuración de base de datos
├── requirements.txt    # Dependencias de Python
└── README.md          # Este archivo
```

## Instalación

1. **Instalar Python 3.8+**
2. **Instalar dependencias:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configurar base de datos:**
   - Edita `config.py` y cambia `DATABASE_URL` según tu base de datos
   - Para SQLite (desarrollo): ya está configurado
   - Para PostgreSQL: descomenta y configura la línea correspondiente

4. **Ejecutar la aplicación:**
   ```bash
   python app.py
   ```

## Endpoints de la API

- `GET /api/riesgos` - Obtener todos los riesgos
- `POST /api/riesgos` - Crear nuevo riesgo
- `GET /api/riesgos/{id}` - Obtener riesgo específico
- `PUT /api/riesgos/{id}` - Actualizar riesgo
- `DELETE /api/riesgos/{id}` - Eliminar riesgo
- `GET /api/health` - Verificar estado de la API

## Ejemplo de uso

**Crear un riesgo:**
```bash
curl -X POST http://localhost:5000/api/riesgos \
  -H "Content-Type: application/json" \
  -d '{
    "titulo": "Pérdida de datos",
    "descripcion": "Posible pérdida de información crítica",
    "probabilidad": 0.3,
    "impacto": 0.8,
    "estado": "Abierto"
  }'
```

**Obtener todos los riesgos:**
```bash
curl http://localhost:5000/api/riesgos
```

## Despliegue en CentOS 9

1. **Subir archivos al servidor**
2. **Instalar Python y pip**
3. **Instalar dependencias:** `pip install -r requirements.txt`
4. **Configurar base de datos en `config.py`**
5. **Ejecutar:** `python app.py`

La API estará disponible en `http://tu-servidor:5000`
