# El Admin

Sistema de administración de edificios residenciales construido con **Django 6** y **Tabler UI**.

Fue creado para dar claridad y empoderar a los residentes, cuentas claras amistades largas.

## Características

- **Torres y Apartamentos** — Gestión de torres, pisos y unidades con cuotas de mantenimiento configurables por torre.
- **Residentes** — Registro de propietarios e inquilinos con soporte de múltiples apartamentos, fotos y contactos de emergencia.
- **Invitaciones** — Envío de invitaciones por correo para que los residentes completen su propio registro.
- **Pagos** — Seguimiento de pagos de mantenimiento con estados (pendiente, en revisión, pagado, vencido), carga de comprobantes y confirmación por staff.
- **Reportes de incidencias** — Creación y seguimiento de reportes por categoría, prioridad y estado. Soporte de duplicados con referencia al reporte original.
- **Anuncios** — Publicación de comunicados para residentes.
- **Configuración** — Generación automática de pagos mensuales, revisión de vencidos y cuotas de mantenimiento por torre.
- **Roles** — Administrador, Staff y Residente con permisos diferenciados.
- **Notificaciones por correo** — Alertas automáticas al staff y residentes en eventos clave.

## Stack

| Capa | Tecnología |
|------|-----------|
| Backend | Django 6.0, Python 3.14 |
| Base de datos | SQLite (desarrollo) |
| Frontend | Tabler UI (Bootstrap 5) |
| Tareas programadas | APScheduler |
| Correo | Django Email (SMTP configurable) |

## Instalación

```bash
git clone https://github.com/Brunux/elAdmin.git
cd elAdmin
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Copia el archivo de entorno y configura tus variables:

```bash
cp .env.example .env
```

Aplica las migraciones y carga datos de prueba:

```bash
python manage.py migrate
python manage.py seed        # opcional — carga torres, apartamentos, residentes y pagos de ejemplo
python manage.py runserver
```

## Variables de entorno

| Variable | Descripción |
|----------|-------------|
| `SECRET_KEY` | Clave secreta de Django |
| `DEBUG` | `True` en desarrollo |
| `ALLOWED_HOSTS` | Hosts permitidos |
| `EMAIL_HOST` | Servidor SMTP |
| `EMAIL_PORT` | Puerto SMTP |
| `EMAIL_HOST_USER` | Usuario SMTP |
| `EMAIL_HOST_PASSWORD` | Contraseña SMTP |
| `DEFAULT_FROM_EMAIL` | Dirección remitente |

## Credenciales de prueba (seed)

| Usuario | Contraseña | Rol |
|---------|-----------|-----|
| `admin@eladmin.com` | `admin123` | Administrador |
| `staff@eladmin.com` | `staff123` | Staff |

## Licencia

MIT
