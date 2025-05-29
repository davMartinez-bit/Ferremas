from fastapi import FastAPI, Request, status, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse, HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
import logging
from datetime import datetime
from pathlib import Path
import jwt  # Asegúrate de tener instalado PyJWT

from config import settings
from app.core.cors import setup_cors
from app.core.middlewares import setup_middlewares
from app.data.database import get_db
SECRET_KEY = "h3n1234sdfg1234h3n1234sdfg1234h3n1234sdfg1234"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Routers de la API
from app.api import (
    productos_router,
    pagos_router,
    usuarios_router,
    divisas_router
)

app = FastAPI(
    title=settings.APP_NAME,
    description="API para la gestión de productos, usuarios y pagos de ferretería.",
    version=settings.APP_VERSION,
    docs_url="/docs" if settings.DEBUG else None,
    redoc_url="/redoc" if settings.DEBUG else None,
    debug=settings.DEBUG
)

# Seguridad con HTTP Bearer (JWT)
security = HTTPBearer()

# Dependencia para obtener el usuario actual a partir del JWT
def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    try:
        payload = jwt.decode(credentials.credentials, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("sub")
        if user_id is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token inválido")
        # Aquí podrías consultar la base de datos para obtener el usuario si lo necesitas
        return {"user_id": user_id}
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token expirado")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token inválido")

logging.basicConfig(
    level=logging.DEBUG if settings.DEBUG else logging.INFO,
    format='%(asctime)s - %(levelname)s - %(name)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

app = FastAPI(
    title=settings.APP_NAME,
    description="API para la gestión de productos, usuarios y pagos de ferretería.",
    version=settings.APP_VERSION,
    docs_url="/docs" if settings.DEBUG else None,
    redoc_url="/redoc" if settings.DEBUG else None,
    debug=settings.DEBUG
)

# Seguridad con HTTP Bearer (JWT)
security = HTTPBearer()
# Guarda la función original antes de sobrescribirla
original_openapi = app.openapi

def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    openapi_schema = original_openapi()  # Llamada a la función original para evitar recursión
    openapi_schema["components"]["securitySchemes"] = {
        "HTTPBearerAuth": {
            "type": "http",
            "scheme": "bearer",
            "bearerFormat": "JWT",
            "description": "Ingrese el token JWT con el prefijo 'Bearer '"
        }
    }
    # Aplica seguridad global a todas las rutas (opcional)
    for path in openapi_schema["paths"].values():
        for method in path.values():
            method.setdefault("security", []).append({"HTTPBearerAuth": []})

    app.openapi_schema = openapi_schema
    return app.openapi_schema

# Sobrescribe la función openapi con la personalizada
app.openapi = custom_openapi


# Middlewares
setup_middlewares(app)
setup_cors(app)

# Archivos estáticos
app.mount("/static", StaticFiles(directory="frontend/public"), name="static")
app.mount("/css", StaticFiles(directory="frontend/public/src/styles"), name="css")
app.mount("/js", StaticFiles(directory="frontend/public/src/js"), name="js")

# Templates
BASE_DIR = Path(__file__).resolve().parent
templates = Jinja2Templates(directory=str(BASE_DIR / "frontend" / "public" / "src" / "html"))

# Rutas del frontend
@app.get("/", response_class=HTMLResponse, tags=["Frontend"])
async def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@app.get("/dashboard", response_class=HTMLResponse, tags=["Frontend"])
async def dashboard_page(request: Request):
    try:
        return templates.TemplateResponse("dashboard.html", {"request": request})
    except:
        dashboard_html = """
        <!DOCTYPE html>
        <html lang="es">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Dashboard - Ferremas</title>
            <link rel="stylesheet" href="/css/style.css">
        </head>
        <body>
            <div class="header">
                <h1>Dashboard Ferremas</h1>
                <button class="logout" onclick="logout()">Cerrar Sesión</button>
            </div>
            <script>
                function logout() {
                    fetch('/api/usuarios/logout', {
                        method: 'POST'
                    }).finally(() => {
                        window.location.href = '/';
                    });
                }
            </script>
        </body>
        </html>
        """
        return HTMLResponse(dashboard_html)

# Ejemplo: proteger rutas incluyendo en los routers
app.include_router(
    productos_router,
    prefix="/api/productos",
    tags=["Productos"],
      # Aquí se aplica la seguridad a todo el router
)

app.include_router(
    pagos_router,
    prefix="/api/pagos",
    tags=["Pagos"],
    
)

app.include_router(
    usuarios_router,
    prefix="/api/usuarios",
    tags=["Usuarios"],
    
)

app.include_router(
    divisas_router,
    prefix="/api/divisas",
    tags=["Divisas"],
    
)

# Exception handler
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    logger.warning(f"Error de validación en {request.url}: {exc.errors()}")
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={"detail": exc.errors(), "body": exc.body},
    )

# Startup event
@app.on_event("startup")
async def startup_event():
    try:
        logger.info("🚀 Iniciando aplicación en modo %s", settings.APP_ENV.upper())
        db = next(get_db())
        result = db.execute(text("SELECT 1")).fetchone()
        if result:
            logger.info("✅ Conexión a la base de datos establecida correctamente")
    except SQLAlchemyError as e:
        logger.error(f"❌ Error al conectar con la base de datos: {e}")
        raise
    except Exception as e:
        logger.error(f"❌ Error durante el startup: {e}")
        raise
    finally:
        if 'db' in locals():
            db.close()

# Health check
@app.get("/health", tags=["General"])
def health_check():
    try:
        db = next(get_db())
        db.execute(text("SELECT 1"))
        db_status = "ok"
    except Exception as e:
        logger.error(f"Database health check failed: {e}")
        db_status = "error"
    finally:
        if 'db' in locals():
            db.close()
    
    return {
        "status": "healthy" if db_status == "ok" else "degraded",
        "version": settings.APP_VERSION,
        "database": db_status,
        "timestamp": datetime.utcnow().isoformat()
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG,
        log_level="debug" if settings.DEBUG else "info"
    )
