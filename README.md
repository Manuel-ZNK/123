# Sistema de Ventas e Inventario

Sistema completo de gestión de ventas e inventario construido con Django, Bootstrap y MySQL.

## Características

- **Autenticación** – Roles de Administrador y Vendedor
- **Gestión de Productos** – CRUD con categorías e imágenes
- **Control de Inventario** – Entradas, salidas y ajustes de stock
- **Registro de Ventas** – Ventas con múltiples productos (formset)
- **Reportes** – Dashboard, reporte de ventas y reporte de inventario

## Arquitectura

```
sales_inventory/   ← Configuración del proyecto
accounts/          ← Autenticación y gestión de usuarios
products/          ← Productos y categorías
inventory/         ← Inventario y movimientos de stock
sales/             ← Ventas y detalles de venta
reports/           ← Dashboard y reportes
templates/         ← Plantillas HTML con Bootstrap 5
static/            ← Archivos estáticos (CSS, JS, imágenes)
```

## Modelos de Base de Datos

| Modelo | App | Descripción |
|---|---|---|
| `User` | accounts | Usuario extendido con rol |
| `Category` | products | Categoría de productos |
| `Product` | products | Producto del catálogo |
| `Inventory` | inventory | Stock actual por producto |
| `InventoryMovement` | inventory | Historial de movimientos de stock |
| `Sale` | sales | Cabecera de venta |
| `SaleDetail` | sales | Línea de detalle de venta |

## Requisitos

- Python 3.10+
- MySQL 8.0+ (o SQLite para desarrollo rápido)

## Instalación y configuración

### 1. Clonar el repositorio

```bash
git clone https://github.com/Manuel-ZNK/123.git
cd 123
```

### 2. Crear y activar un entorno virtual

```bash
python -m venv venv
# Linux/Mac:
source venv/bin/activate
# Windows:
venv\Scripts\activate
```

### 3. Instalar dependencias

```bash
pip install -r requirements.txt
```

### 4. Configurar la base de datos

#### Opción A – SQLite (desarrollo rápido, sin configuración extra)

Por defecto el proyecto usa SQLite. No necesitas cambiar nada.

#### Opción B – MySQL (producción)

1. Crea la base de datos en MySQL:
   ```sql
   CREATE DATABASE sales_inventory_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
   CREATE USER 'sales_user'@'localhost' IDENTIFIED BY 'tu_password_segura';
   GRANT ALL PRIVILEGES ON sales_inventory_db.* TO 'sales_user'@'localhost';
   FLUSH PRIVILEGES;
   ```

2. Crea un archivo `.env` en la raíz del proyecto:
   ```
   DATABASE_ENGINE=django.db.backends.mysql
   DATABASE_NAME=sales_inventory_db
   DATABASE_USER=sales_user
   DATABASE_PASSWORD=tu_password_segura
   DATABASE_HOST=127.0.0.1
   DATABASE_PORT=3306
   DJANGO_SECRET_KEY=cambia-esto-por-una-clave-larga-y-aleatoria
   DJANGO_DEBUG=False
   ```

3. Carga las variables de entorno antes de ejecutar Django:
   ```bash
   export $(cat .env | xargs)
   ```

### 5. Aplicar migraciones

```bash
python manage.py makemigrations
python manage.py migrate
```

### 6. Crear superusuario administrador

```bash
python manage.py createsuperuser
```

> Cuando se te pregunte, puedes asignar el rol `admin` desde el admin de Django
> en `/admin/` → Usuarios → editar el usuario → cambiar rol a **Administrador**.

### 7. Ejecutar el servidor de desarrollo

```bash
python manage.py runserver
```

Abre tu navegador en: **http://127.0.0.1:8000/**

## Comandos de Django útiles

```bash
# Crear migraciones después de cambios en modelos
python manage.py makemigrations

# Aplicar migraciones
python manage.py migrate

# Recolectar archivos estáticos (para producción)
python manage.py collectstatic

# Abrir shell interactivo
python manage.py shell

# Cargar datos de prueba (si existe un fixture)
python manage.py loaddata fixtures/demo.json
```

## Subir cambios a GitHub

```bash
git add .
git commit -m "Descripción de los cambios"
git push origin main
```

## Variables de entorno (resumen)

| Variable | Valor por defecto | Descripción |
|---|---|---|
| `DJANGO_SECRET_KEY` | valor de desarrollo | Clave secreta de Django |
| `DJANGO_DEBUG` | `True` | Modo debug |
| `DJANGO_ALLOWED_HOSTS` | `localhost 127.0.0.1` | Hosts permitidos |
| `DATABASE_ENGINE` | `django.db.backends.sqlite3` | Motor de BD |
| `DATABASE_NAME` | `sales_inventory_db` | Nombre de la BD (MySQL) |
| `DATABASE_USER` | `root` | Usuario de MySQL |
| `DATABASE_PASSWORD` | *(vacío)* | Contraseña de MySQL |
| `DATABASE_HOST` | `127.0.0.1` | Host de MySQL |
| `DATABASE_PORT` | `3306` | Puerto de MySQL |

## Roles de usuario

| Rol | Permisos |
|---|---|
| **Administrador** | Acceso total: usuarios, productos, inventario, ventas, reportes, cancelar ventas |
| **Vendedor** | Crear ventas, ver productos, ver inventario, ver reportes |
