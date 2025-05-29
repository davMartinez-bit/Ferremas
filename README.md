# 🔧 Sistema de Gestión Ferremas

Sistema web completo para la gestión de productos, usuarios, pagos y divisas de una ferretería, desarrollado con **FastAPI** y **MySQL**.

## 📋 Tabla de Contenidos

- [Características](#-características)
- [Tecnologías](#-tecnologías)
- [Requisitos del Sistema](#-requisitos-del-sistema)
- [Instalación Paso a Paso](#-instalación-paso-a-paso)
- [Configuración de Base de Datos](#-configuración-de-base-de-datos)
- [Configuración del Proyecto](#-configuración-del-proyecto)
- [Estructura del Proyecto](#-estructura-del-proyecto)
- [Ejecución](#-ejecución)
- [API Endpoints](#-api-endpoints)
- [Troubleshooting](#-troubleshooting)

## 🚀 Características

- ✅ **API REST** completa con FastAPI
- ✅ **Frontend web** integrado con templates Jinja2
- ✅ **Autenticación** de usuarios
- ✅ **Gestión de productos** y inventario
- ✅ **Sistema de pagos** y divisas
- ✅ **Base de datos MySQL** con SQLAlchemy
- ✅ **Documentación automática** con Swagger
- ✅ **CORS configurado** para desarrollo
- ✅ **Middlewares** de seguridad y logging

## 🛠 Tecnologías

| Tecnología | Versión | Propósito |
|------------|---------|-----------|
| **Python** | 3.8+ | Lenguaje principal |
| **FastAPI** | 0.104+ | Framework web |
| **SQLAlchemy** | 2.0+ | ORM para base de datos |
| **MySQL** | 8.0+ | Base de datos |
| **Uvicorn** | 0.24+ | Servidor ASGI |
| **Jinja2** | 3.1+ | Motor de templates |
| **DBeaver** | - | Administración de BD |

## 💻 Requisitos del Sistema

### Software Requerido

1. **Python 3.8 o superior**
   - [Descargar Python](https://www.python.org/downloads/)
   - Verificar: `python --version`

2. **MySQL Server 8.0+**
   - [Descargar MySQL](https://dev.mysql.com/downloads/mysql/)
   - O usar XAMPP/WAMP que incluye MySQL

3. **Git** (opcional pero recomendado)
   - [Descargar Git](https://git-scm.com/downloads/)

4. **DBeaver** (recomendado para administrar la BD)
   - [Descargar DBeaver](https://dbeaver.io/download/)

### Especificaciones Mínimas

- **RAM**: 4GB mínimo, 8GB recomendado
- **Espacio**: 2GB libres
- **SO**: Windows 10+, macOS 10.14+, Ubuntu 18.04+

## 📦 Instalación Paso a Paso

### 1. Clonar el Proyecto

```bash
# Si tienes Git instalado
git clone https://github.com/tu-usuario/ferremas-system.git
cd ferremas-system

# O descargar y extraer el ZIP del proyecto
```

### 2. Crear Entorno Virtual

```bash
# Crear entorno virtual
python -m venv venv

# Activar entorno virtual
# En Windows:
venv\Scripts\activate

# En macOS/Linux:
source venv/bin/activate

# Verificar que está activado (debe aparecer (venv) al inicio)
```

### 3. Instalar Dependencias

```bash
# Actualizar pip
pip install --upgrade pip

# Instalar dependencias principales
pip install fastapi==0.104.1
pip install uvicorn==0.24.0
pip install sqlalchemy==2.0.23
pip install pymysql==1.1.0
pip install cryptography==41.0.7
pip install python-multipart==0.0.6
pip install jinja2==3.1.2
pip install python-dotenv==1.0.0
pip install passlib==1.7.4
pip install bcrypt==4.1.2
pip install python-jose==3.3.0

# O crear un archivo requirements.txt con:
```

**Crear archivo `requirements.txt`:**

```text
fastapi==0.104.1
uvicorn==0.24.0
sqlalchemy==2.0.23
pymysql==1.1.0
cryptography==41.0.7
python-multipart==0.0.6
jinja2==3.1.2
python-dotenv==1.0.0
passlib==1.7.4
bcrypt==4.1.2
python-jose==3.3.0
```

```bash
# Instalar desde requirements.txt
pip install -r requirements.txt
```

## 🗄️ Configuración de Base de Datos

### 1. Instalar y Configurar MySQL

#### Opción A: MySQL Server Standalone

1. **Descargar e instalar MySQL Server**
   - Ir a: https://dev.mysql.com/downloads/mysql/
   - Descargar para tu sistema operativo
   - Durante la instalación, recordar la contraseña de `root`

2. **Configurar MySQL** (puerto por defecto: 3306)

#### Opción B: Usar XAMPP (Más fácil para principiantes)

1. **Descargar XAMPP**
   - Ir a: https://www.apachefriends.org/download.html
   - Instalar y ejecutar

2. **Iniciar servicios**
   - Abrir XAMPP Control Panel
   - Iniciar **Apache** y **MySQL**

### 2. Crear Base de Datos

#### Usando DBeaver (Recomendado)

1. **Instalar DBeaver**
   - Descargar desde: https://dbeaver.io/download/
   - Instalar siguiendo el asistente

2. **Conectar a MySQL**
   - Abrir DBeaver
   - Click en "Nueva Conexión" → MySQL
   - Configurar:
     ```
     Host: localhost
     Puerto: 3306
     Usuario: root
     Contraseña: [tu contraseña de MySQL]
     ```
   - Probar conexión → Aceptar

3. **Crear Base de Datos**
   ```sql
   CREATE DATABASE ferremas_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
   ```

#### Usando Línea de Comandos

```bash
# Conectar a MySQL
mysql -u root -p

# Crear base de datos
CREATE DATABASE ferremas_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

# Crear usuario (opcional)
CREATE USER 'ferremas_user'@'localhost' IDENTIFIED BY 'tu_contraseña_segura';
GRANT ALL PRIVILEGES ON ferremas_db.* TO 'ferremas_user'@'localhost';
FLUSH PRIVILEGES;

# Salir
EXIT;
```

### 3. Verificar Conexión

```bash
# Probar conexión desde Python
python -c "
import pymysql
try:
    conn = pymysql.connect(host='localhost', user='root', password='tu_contraseña', database='ferremas_db')
    print('✅ Conexión exitosa a MySQL')
    conn.close()
except Exception as e:
    print(f'❌ Error de conexión: {e}')
"
```

## ⚙️ Configuración del Proyecto

### 1. Crear Archivo de Configuración

Crear archivo `.env` en la raíz del proyecto:

```bash
# .env
# ===== CONFIGURACIÓN DE LA APLICACIÓN =====
APP_NAME=Ferremas System
APP_VERSION=1.0.0
APP_ENV=development
DEBUG=True

# ===== CONFIGURACIÓN DE BASE DE DATOS =====
# Para MySQL local
DATABASE_URL=mysql+pymysql://root:tu_contraseña@localhost:3306/ferremas_db

# O si creaste un usuario específico:
# DATABASE_URL=mysql+pymysql://ferremas_user:tu_contraseña_segura@localhost:3306/ferremas_db

# ===== CONFIGURACIÓN DE SEGURIDAD =====
SECRET_KEY=tu_clave_secreta_muy_segura_aqui_cambiala
JWT_SECRET_KEY=otra_clave_secreta_para_jwt_tokens

# ===== CONFIGURACIÓN DE CORS =====
ALLOWED_ORIGINS=["http://localhost:3000", "http://localhost:8000", "http://127.0.0.1:3000", "http://127.0.0.1:8000"]

# ===== CONFIGURACIÓN DEL SERVIDOR =====
HOST=0.0.0.0
PORT=8000
```

### 2. Crear Archivo config.py

```python
# config.py
import os
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

class Settings:
    # Aplicación
    APP_NAME: str = os.getenv("APP_NAME", "Ferremas System")
    APP_VERSION: str = os.getenv("APP_VERSION", "1.0.0")
    APP_ENV: str = os.getenv("APP_ENV", "development")
    DEBUG: bool = os.getenv("DEBUG", "False").lower() == "true"
    
    # Base de datos
    DATABASE_URL: str = os.getenv("DATABASE_URL", "mysql+pymysql://root:password@localhost:3306/ferremas_db")
    
    # Seguridad
    SECRET_KEY: str = os.getenv("SECRET_KEY", "your-secret-key-change-this")
    JWT_SECRET_KEY: str = os.getenv("JWT_SECRET_KEY", "your-jwt-secret-change-this")
    
    # CORS
    ALLOWED_ORIGINS: list = [
        "http://localhost:3000",
        "http://localhost:8000", 
        "http://127.0.0.1:3000",
        "http://127.0.0.1:8000"
    ]
    
    # Servidor
    HOST: str = os.getenv("HOST", "0.0.0.0")
    PORT: int = int(os.getenv("PORT", 8000))

settings = Settings()
```

## 📁 Estructura del Proyecto

```
ferremas-system/
├── 📄 main.py                     # Punto de entrada principal
├── 📄 config.py                   # Configuración de la aplicación
├── 📄 requirements.txt            # Dependencias de Python
├── 📄 .env                        # Variables de entorno (crear)
├── 📄 README.md                   # Este archivo
│
├── 📁 app/                        # Código principal de la aplicación
│   ├── 📁 api/                    # Endpoints de la API
│   │   ├── 📄 __init__.py
│   │   ├── 📄 productos.py        # API de productos
│   │   ├── 📄 usuarios.py         # API de usuarios/auth
│   │   ├── 📄 pagos.py           # API de pagos
│   │   └── 📄 divisas.py         # API de divisas
│   │
│   ├── 📁 core/                   # Configuraciones centrales
│   │   ├── 📄 __init__.py
│   │   ├── 📄 cors.py            # Configuración CORS
│   │   └── 📄 middlewares.py     # Middlewares personalizados
│   │
│   ├── 📁 data/                   # Capa de datos
│   │   ├── 📄 __init__.py
│   │   ├── 📄 database.py        # Configuración de BD
│   │   └── 📄 models.py          # Modelos SQLAlchemy
│   │
│   └── 📁 services/               # Lógica de negocio
│       ├── 📄 __init__.py
│       ├── 📄 auth_service.py    # Servicio de autenticación
│       └── 📄 product_service.py # Servicio de productos
│
├── 📁 frontend/                   # Archivos del frontend
│   └── 📁 public/
│       └── 📁 src/
│           ├── 📁 html/          # Templates HTML
│           │   ├── 📄 login.html
│           │   └── 📄 dashboard.html
│           ├── 📁 css/           # Estilos CSS  
│           │   └── 📄 style.css
│           └── 📁 js/            # JavaScript
│               └── 📄 login.js
│
└── 📁 venv/                      # Entorno virtual (se crea automáticamente)
```

## 🚀 Ejecución

### 1. Verificar Configuración

```bash
# Verificar que el entorno virtual esté activado
# Debe aparecer (venv) al inicio de la línea de comandos

# Verificar instalación de dependencias
pip list | grep fastapi
pip list | grep sqlalchemy
pip list | grep pymysql
```

### 2. Crear Estructura de Directorios

```bash
# Crear directorios necesarios
mkdir -p frontend/public/src/html
mkdir -p frontend/public/src/css
mkdir -p frontend/public/src/js
mkdir -p app/api
mkdir -p app/core
mkdir -p app/data
mkdir -p app/services
```

### 3. Inicializar Base de Datos

```python
# crear_tablas.py (archivo temporal para crear tablas)
from app.data.database import engine, Base
from app.data.models import *  # Importar todos los modelos

# Crear todas las tablas
Base.metadata.create_all(bind=engine)
print("✅ Tablas creadas exitosamente")
```

```bash
# Ejecutar creación de tablas
python crear_tablas.py
```

### 4. Ejecutar la Aplicación

```bash
# Método 1: Usando uvicorn directamente
uvicorn main:app --host 0.0.0.0 --port 8000 --reload

# Método 2: Ejecutando main.py
python main.py

# Método 3: Con configuraciones específicas
uvicorn main:app --host 127.0.0.1 --port 8000 --reload --log-level debug
```

### 5. Verificar que Funciona

1. **Abrir navegador** en: http://localhost:8000
2. **Verificar API docs** en: http://localhost:8000/docs
3. **Verificar health check** en: http://localhost:8000/health

## 🔗 API Endpoints

### Documentación Automática
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### Endpoints Principales

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| `GET` | `/` | Página de login |
| `POST` | `/login` | Procesar login del frontend |
| `GET` | `/dashboard` | Dashboard principal |
| `GET` | `/health` | Estado de la aplicación |
| `GET` | `/api` | Información de la API |

### API REST

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| `POST` | `/api/usuarios/login` | Login API |
| `GET` | `/api/usuarios/me` | Info del usuario actual |
| `GET` | `/api/productos` | Listar productos |
| `POST` | `/api/productos` | Crear producto |
| `GET` | `/api/pagos` | Listar pagos |
| `POST` | `/api/pagos` | Crear pago |
| `GET` | `/api/divisas` | Listar divisas |

## 🐛 Troubleshooting

### Problemas Comunes

#### 1. Error de Conexión a MySQL

**Error**: `Can't connect to MySQL server`

**Soluciones**:
```bash
# Verificar que MySQL esté ejecutándose
# En Windows (XAMPP):
# - Abrir XAMPP Control Panel
# - Iniciar MySQL

# En Windows (Servicio):
net start mysql80

# En macOS:
sudo /usr/local/mysql/support-files/mysql.server start

# En Linux:
sudo systemctl start mysql
```

#### 2. Error de Módulos No Encontrados

**Error**: `ModuleNotFoundError: No module named 'fastapi'`

**Solución**:
```bash
# Verificar que el entorno virtual esté activado
# Reinstalar dependencias
pip install -r requirements.txt
```

#### 3. Error de Puerto en Uso

**Error**: `Address already in use`

**Solución**:
```bash
# Cambiar puerto
uvicorn main:app --port 8001

# O matar proceso en puerto 8000
# Windows:
netstat -ano | findstr :8000
taskkill /PID [PID_NUMBER] /F

# macOS/Linux:
lsof -ti:8000 | xargs kill -9
```

#### 4. Error de CORS

**Error**: Requests bloqueadas por CORS

**Solución**:
- Verificar configuración en `app/core/cors.py`
- Agregar tu dominio a `ALLOWED_ORIGINS`

#### 5. Error de Templates

**Error**: `TemplateNotFound`

**Solución**:
```bash
# Verificar estructura de directorios
ls -la frontend/public/src/html/

# Crear archivos faltantes
touch frontend/public/src/html/login.html
```

### Logs y Debugging

```bash
# Ejecutar con logs detallados
uvicorn main:app --log-level debug --reload

# Ver logs en tiempo real
tail -f logs/app.log  # Si tienes logging a archivo configurado
```

### Comandos Útiles

```bash
# Ver procesos Python activos
ps aux | grep python

# Ver qué está usando el puerto 8000
netstat -tulpn | grep :8000

# Verificar variables de entorno
python -c "from config import settings; print(settings.DATABASE_URL)"

# Probar conexión a BD
python -c "from app.data.database import get_db; next(get_db())"
```

## 📚 Recursos Adicionales

- [Documentación de FastAPI](https://fastapi.tiangolo.com/)
- [SQLAlchemy Tutorial](https://docs.sqlalchemy.org/en/20/tutorial/)
- [MySQL Documentation](https://dev.mysql.com/doc/)
- [DBeaver User Guide](https://dbeaver.io/docs/)

## 📝 Notas Importantes

1. **Seguridad**: Cambiar las claves secretas en producción
2. **Base de Datos**: Hacer respaldos regulares
3. **CORS**: Configurar orígenes específicos en producción
4. **SSL**: Usar HTTPS en producción
5. **Logs**: Configurar rotación de logs en producción

## 🤝 Soporte

Si tienes problemas:
1. Verificar que todos los prerequisitos están instalados
2. Revisar los logs de error
3. Consultar la sección de Troubleshooting
4. Verificar la configuración de `.env`

---

**¡Listo! Tu sistema Ferremas debería estar funcionando correctamente.** 🎉
