# Sistema de Gestión de Encomiendas

Proyecto Django con API REST construida sobre la aplicación existente de encomiendas.

## Descripción

Este proyecto gestiona clientes, rutas, empleados y encomiendas. Además de las vistas web existentes, incluye una API REST segura con JWT y documentación OpenAPI/Swagger.

## Tecnologías

- Django
- Django REST Framework
- Simple JWT
- django-filter
- drf-spectacular
- django-cors-headers
- PostgreSQL (Docker)

## Configuración rápida

1. Copiar `.env.example` a `.env`:
   ```bash
   copy .env.example .env
   ```

2. Levantar los servicios:
   ```bash
   docker compose up --build -d
   ```

3. Instalar dependencias localmente (opcional):
   ```bash
   python -m pip install -r requirements.txt
   ```

4. Ejecutar migraciones:
   ```bash
   docker compose exec web python manage.py migrate
   ```

5. Crear superusuario:
   ```bash
   docker compose exec web python manage.py createsuperuser
   ```

6. Abrir la aplicación:
   - Web: `http://localhost:8000/`
   - Admin: `http://localhost:8000/admin/`
   - Swagger: `http://localhost:8000/api/docs/`
   - Redoc: `http://localhost:8000/api/redoc/`
   - Esquema: `http://localhost:8000/api/schema/`

## Endpoints de API principales

- `POST /api/v1/auth/token/` - obtener `access` y `refresh`
- `POST /api/v1/auth/token/refresh/` - refrescar token
- `GET /api/v1/encomiendas/` - lista de encomiendas
- `GET /api/v1/encomiendas/{id}/` - detalle de encomienda
- `POST /api/v1/encomiendas/` - crear encomienda
- `PATCH /api/v1/encomiendas/{id}/` - actualizar encomienda
- `DELETE /api/v1/encomiendas/{id}/` - eliminar encomienda
- `POST /api/v1/encomiendas/{id}/cambiar_estado/` - cambiar estado
- `GET /api/v1/encomiendas/con_retraso/` - encomiendas retrasadas
- `GET /api/v1/encomiendas/pendientes/` - encomiendas pendientes
- `GET /api/v1/encomiendas/{id}/historial/` - historial de estados
- `GET /api/v1/encomiendas/estadisticas/` - estadísticas
- `GET /api/v1/clientes/` - lista de clientes activos
- `GET /api/v1/rutas/` - lista de rutas
- `GET /api/v2/encomiendas/` - versión 2 resumida de encomiendas
- `GET /api/v2/encomiendas/{id}/` - detalle resumido de encomienda

## Endpoints de demostración DRF

- `GET/POST /api/v1/fbv/encomiendas/`
- `GET/PATCH/DELETE /api/v1/fbv/encomiendas/{id}/`
- `GET/POST /api/v1/apiview/encomiendas/`
- `GET/PATCH/DELETE /api/v1/apiview/encomiendas/{id}/`
- `GET/POST /api/v1/mixins/encomiendas/`
- `GET/PATCH/DELETE /api/v1/mixins/encomiendas/{id}/`
- `GET/POST /api/v1/generic/encomiendas/`
- `GET/PATCH/DELETE /api/v1/generic/encomiendas/{id}/`

## Autorización JWT en Swagger

1. Obtener token en `/api/v1/auth/token/`.
2. En Swagger, usar el botón "Authorize".
3. Ingresar `Bearer <access_token>`.

## Correr tests

```bash
python manage.py test
```

## Notas adicionales

- El proyecto mantiene las vistas web originales y añade la capa API sin reemplazarla.
- Para CORS en desarrollo se usa `CORS_ALLOW_ALL_ORIGINS = True`; en producción conviene cambiar a `CORS_ALLOWED_ORIGINS`.
