# 🛠️ Ferremas - API de Ferretería

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115.12-green.svg)](https://fastapi.tiangolo.com/)
[![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-2.0.41-red.svg)](https://www.sqlalchemy.org/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

## 📋 Descripción

**Ferremas** es una aplicación web completa para la gestión de una ferretería, desarrollada con FastAPI en el backend y HTML/CSS/JavaScript en el frontend. El sistema incluye gestión de productos, usuarios, carrito de compras, pedidos, pagos con Webpay, y más.

## ✨ Características Principales

### 🔐 Autenticación y Usuarios
- Sistema de login/registro con JWT
- Roles de usuario: Cliente, Vendedor, Administrador
- Gestión de perfiles de usuario
- Recuperación de contraseñas

### 🛍️ Gestión de Productos
- Catálogo completo de productos
- Categorías y marcas
- Gestión de stock y precios
- Productos destacados y en promoción
- Búsqueda y filtros

### 🛒 Carrito de Compras
- Agregar/eliminar productos
- Modificar cantidades
- Cálculo automático de totales
- Persistencia de carrito por usuario

### ❤️ Favoritos
- Lista de productos favoritos
- Toggle de favoritos
- Vista de productos guardados

### 📦 Gestión de Pedidos
- Creación de pedidos desde el carrito
- Estados de pedido (Pendiente, Confirmado, Enviado, Entregado)
- Historial de pedidos por usuario
- Detalles completos de pedidos

### 💳 Sistema de Pagos
- Integración con Webpay (Transbank)
- Procesamiento de pagos seguros
- Confirmación de transacciones
- Manejo de errores de pago

### 💬 Chat y Mensajería
- Sistema de chat en tiempo real
- Soporte al cliente
- Mensajes entre usuarios y administradores
- Notificaciones

### 📊 Panel de Administración
- Dashboard administrativo
- Gestión de productos y categorías
- Gestión de usuarios
- Reportes y estadísticas
- Configuración del sistema

### 💱 Divisas
- Integración con API del Banco Central de Chile
- Conversión de precios en tiempo real
- Múltiples monedas soportadas

## 🏗️ Arquitectura del Proyecto

```
ferreteria-api/
├── app/                    # Código principal de la aplicación
│   ├── api/               # Endpoints de la API
│   │   ├── admin.py       # Endpoints administrativos
│   │   ├── carrito.py     # Gestión del carrito
│   │   ├── chat.py        # Sistema de chat
│   │   ├── divisas.py     # Conversión de divisas
│   │   ├── favoritos.py   # Gestión de favoritos
│   │   ├── login.py       # Autenticación
│   │   ├── mensajes.py    # Sistema de mensajería
│   │   ├── pagos.py       # Procesamiento de pagos
│   │   ├── pedidos.py     # Gestión de pedidos
│   │   ├── productos.py   # Gestión de productos
│   │   ├── schemas.py     # Esquemas de datos
│   │   └── usuarios.py    # Gestión de usuarios
│   ├── core/              # Configuración central
│   │   ├── cors.py        # Configuración CORS
│   │   ├── middlewares.py # Middlewares personalizados
│   │   ├── pagos.py       # Lógica de pagos
│   │   ├── productos.py   # Lógica de productos
│   │   └── security.py    # Autenticación y seguridad
│   ├── data/              # Capa de datos
│   │   ├── database.py    # Configuración de base de datos
│   │   ├── models/        # Modelos SQLAlchemy
│   │   ├── repositories/  # Repositorios de datos
│   │   └── schemas/       # Esquemas de validación
│   ├── integrations/      # Integraciones externas
│   │   ├── banco_central.py # API del Banco Central
│   │   └── webpay.py      # Integración Webpay
│   ├── services/          # Lógica de negocio
│   └── utils/             # Utilidades
├── frontend/              # Interfaz de usuario
│   ├── components/        # Componentes reutilizables
│   ├── css/              # Estilos CSS
│   ├── html/             # Páginas HTML
│   ├── js/               # JavaScript del frontend
│   └── public/           # Archivos públicos
├── main.py               # Punto de entrada de la aplicación
├── config.py             # Configuración de la aplicación
├── requirements.txt      # Dependencias de Python
└── test_flujo_completo.py # Test de flujo completo
```

## 🚀 Instalación y Configuración

### Prerrequisitos

- Python 3.8 o superior
- MySQL 8.0 o superior (opcional, también soporta SQLite)
- Git

### 1. Clonar el Repositorio

```bash
git clone https://github.com/davMartinez-bit/Ferremas.git
cd ferreteria-api
```

### 2. Crear Entorno Virtual

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

### 3. Instalar Dependencias

```bash
pip install -r requirements.txt
```

### 4. Configurar Variables de Entorno

Crear un archivo `.env` en la raíz del proyecto:

```env
# Configuración de la aplicación
APP_ENV=development
DEBUG=true
SECRET_KEY=tu_super_secret_key_muy_segura_para_jwt_tokens_2025

# Configuración de base de datos MySQL
DB_HOST=localhost
DB_PORT=3306
DB_USER=root
DB_PASSWORD=tu_password
DB_NAME=ferreteria_db

# Configuración Webpay (Transbank)
WEBPAY_COMMERCE_CODE=597055555532
WEBPAY_API_KEY=tu_api_key_webpay
WEBPAY_ENV=INTEGRACION
WEBPAY_SIMULATOR=true

# Configuración Banco Central
BANCO_CENTRAL_API_KEY=tu_api_key_banco_central
```

### 5. Configurar Base de Datos

#### Opción A: MySQL
```sql
CREATE DATABASE ferreteria_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

#### Opción B: SQLite (por defecto)
La aplicación usará automáticamente SQLite si no hay configuración de MySQL.

### 6. Ejecutar la Aplicación

```bash
python main.py
```

La aplicación estará disponible en: `http://localhost:8000`

## 📖 Uso de la API

### Endpoints Principales

#### Autenticación
- `POST /api/login` - Iniciar sesión
- `POST /api/usuarios/register` - Registrar usuario
- `GET /api/usuarios/me` - Obtener perfil del usuario

#### Productos
- `GET /api/productos/` - Listar productos
- `GET /api/productos/{id}` - Obtener producto específico
- `POST /api/productos/` - Crear producto (admin)
- `PUT /api/productos/{id}` - Actualizar producto (admin)

#### Carrito
- `GET /api/carrito/` - Obtener carrito del usuario
- `POST /api/carrito/agregar` - Agregar producto al carrito
- `DELETE /api/carrito/{producto_id}` - Eliminar producto del carrito

#### Pedidos
- `GET /api/pedidos/` - Listar pedidos del usuario
- `POST /api/pedidos/` - Crear nuevo pedido
- `GET /api/pedidos/{id}` - Obtener detalles del pedido

#### Pagos
- `POST /api/pagos/crear` - Crear transacción de pago
- `POST /api/pagos/confirmar` - Confirmar pago con Webpay

### Documentación de la API

Una vez que la aplicación esté ejecutándose, puedes acceder a:
- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`

## 🧪 Testing

### Ejecutar Test de Flujo Completo

```bash
python test_flujo_completo.py
```

Este test verifica:
- Conexión al servidor
- Autenticación de usuarios
- Gestión de productos
- Funcionalidad del carrito
- Sistema de favoritos
- Procesamiento de pagos
- Acceso al dashboard

## 🔧 Configuración de Desarrollo

### Estructura de Desarrollo

El proyecto está organizado siguiendo las mejores prácticas:

- **Separación de responsabilidades**: API, servicios, modelos, etc.
- **Inyección de dependencias**: Uso de FastAPI Depends
- **Validación de datos**: Pydantic schemas
- **Manejo de errores**: Middlewares personalizados
- **Logging**: Sistema de logs configurado

### Variables de Entorno de Desarrollo

```env
APP_ENV=development
DEBUG=true
DATABASE_URL=sqlite:///./ferreteria.db
```

## 🚀 Despliegue

### Producción

Para desplegar en producción:

1. Configurar variables de entorno de producción
2. Usar un servidor WSGI como Gunicorn
3. Configurar un proxy reverso (Nginx)
4. Configurar base de datos MySQL
5. Configurar SSL/TLS

### Docker (Opcional)

```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

## 🤝 Contribución

1. Fork el proyecto
2. Crea una rama para tu feature (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abre un Pull Request

## 📝 Licencia

Este proyecto está bajo la Licencia MIT. Ver el archivo `LICENSE` para más detalles.

## 👨‍💻 Autor

**David Martínez**
- GitHub: [@davMartinez-bit](https://github.com/davMartinez-bit)

## 🙏 Agradecimientos

- [FastAPI](https://fastapi.tiangolo.com/) - Framework web moderno
- [SQLAlchemy](https://www.sqlalchemy.org/) - ORM para Python
- [Webpay](https://www.transbank.cl/) - Pasarela de pagos
- [Banco Central de Chile](https://www.bcentral.cl/) - API de divisas

## 📞 Soporte

Si tienes alguna pregunta o necesitas ayuda:

1. Revisa la documentación de la API en `/docs`
2. Ejecuta el test de flujo completo
3. Revisa los logs de la aplicación
4. Abre un issue en GitHub

---

**¡Gracias por usar Ferremas! 🛠️** 