from fastapi import FastAPI, Request, status, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse, HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.openapi.utils import get_openapi
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
import logging
from datetime import datetime
from pathlib import Path
import jwt
import traceback
import sys

from config import settings
from app.core.cors import setup_cors
from app.core.middlewares import setup_middlewares
from app.data.database import get_db

# Importaciones directas de routers
from app.api.productos import router as productos_router
from app.api.pagos import router as pagos_router
from app.api.usuarios import router as usuarios_router
from app.api.divisas import router as divisas_router
from app.api.carrito import router as carrito_router
from app.api.pedidos import router as pedidos_router
from app.api.mensajes import router as mensajes_router
from app.api.admin import router as admin_router
from app.api.login import router as login_router
from app.api.favoritos import router as favoritos_router
from app.api.chat import router as chat_router
from app.api import (
    usuarios, productos, carrito, pedidos, 
    favoritos, mensajes, pagos
)

SECRET_KEY = settings.SECRET_KEY
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Configuración de logging
logging.basicConfig(
    level=logging.DEBUG if settings.DEBUG else logging.INFO,
    format='%(asctime)s - %(levelname)s - %(name)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

# Crear la aplicación FastAPI
app = FastAPI(
    title=settings.APP_NAME,
    description="API para la gestión de productos, usuarios y pagos de ferretería.",
    version=settings.APP_VERSION,
    docs_url="/docs" if settings.DEBUG else None,
    redoc_url="/redoc" if settings.DEBUG else None,
    debug=settings.DEBUG
)

# Seguridad con HTTP Bearer (JWT) - DESACTIVADO PARA DESARROLLO
# security = HTTPBearer()

# def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
#     try:
#         payload = jwt.decode(credentials.credentials, SECRET_KEY, algorithms=[ALGORITHM])
#         user_id = payload.get("sub")
#         if user_id is None:
#             raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token inválido")
#         return {"user_id": user_id}
#     except jwt.ExpiredSignatureError:
#         raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token expirado")
#     except jwt.InvalidTokenError:
#         raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token inválido")

# Función OpenAPI personalizada
def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    
    openapi_schema = get_openapi(
        title=app.title,
        version=app.version,
        description=app.description,
        routes=app.routes,
    )
    
    # DESACTIVADO COMPLETAMENTE PARA DESARROLLO:
    # openapi_schema["components"]["securitySchemes"] = {
    #     "HTTPBearerAuth": {
    #         "type": "http",
    #         "scheme": "bearer",
    #         "bearerFormat": "JWT",
    #         "description": "Ingrese el token JWT con el prefijo 'Bearer '"
    #     }
    # }
    
    app.openapi_schema = openapi_schema
    return app.openapi_schema

# Asignar la función OpenAPI personalizada
app.openapi = custom_openapi

# Middlewares
setup_middlewares(app)
setup_cors(app)

# Archivos estáticos
# app.mount("/", StaticFiles(directory="frontend", html=True), name="root-static")  # QUITADO para evitar conflictos
app.mount("/static", StaticFiles(directory="frontend"), name="static")
app.mount("/css", StaticFiles(directory="frontend/css"), name="css")
app.mount("/js", StaticFiles(directory="frontend/js"), name="js")
app.mount("/html", StaticFiles(directory="frontend/html"), name="html")

# Templates
BASE_DIR = Path(__file__).resolve().parent
templates = Jinja2Templates(directory=str(BASE_DIR / "frontend"))

# Rutas del frontend - RESTAURADAS con rutas .html
@app.get("/index.html", response_class=HTMLResponse, tags=["Frontend"])
async def home_page(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/", response_class=HTMLResponse, tags=["Frontend"])
async def home_page_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/login.html", response_class=HTMLResponse, tags=["Frontend"])
async def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@app.get("/login", response_class=HTMLResponse, tags=["Frontend"])
async def login_page_root(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@app.get("/productos.html", response_class=HTMLResponse, tags=["Frontend"])
async def productos_page(request: Request):
    return templates.TemplateResponse("productos.html", {"request": request})

@app.get("/productos", response_class=HTMLResponse, tags=["Frontend"])
async def productos_page_root(request: Request):
    return templates.TemplateResponse("productos.html", {"request": request})

@app.get("/register.html", response_class=HTMLResponse, tags=["Frontend"])
async def register_page(request: Request):
    return templates.TemplateResponse("register.html", {"request": request})

@app.get("/register", response_class=HTMLResponse, tags=["Frontend"])
async def register_page_root(request: Request):
    return templates.TemplateResponse("register.html", {"request": request})

# Incluir routers - SIN autenticación global
app.include_router(
    productos_router,
    prefix="/api/productos",
    tags=["Productos"],
      # Solo productos requiere auth
)

app.include_router(
    pagos_router,
    prefix="/api/pagos",
    tags=["Pagos"],
    # Sin dependencies - pagos será público
)

app.include_router(
    usuarios_router,
    prefix="/api/usuarios",
    tags=["Usuarios"],
    # Sin dependencies - login/register son públicos
)

app.include_router(
    divisas_router,
    prefix="/api/divisas",
    tags=["Divisas"],
    # Sin dependencies por ahora
)

# 🆕 NUEVOS ROUTERS
app.include_router(
    carrito_router,
    tags=["Carrito"],
    # Con autenticación requerida
)

app.include_router(
    pedidos_router,
    tags=["Pedidos"],
    # Con autenticación requerida
)

app.include_router(
    mensajes_router,
    tags=["Mensajes"],
    # Con autenticación requerida
)

app.include_router(
    admin_router,
    tags=["Admin"],
    # Con autenticación y permisos de admin requeridos
)

app.include_router(login_router, prefix="/api", tags=["Login"])
app.include_router(favoritos_router, tags=["Favoritos"])
app.include_router(chat_router, tags=["Chat"])

# Exception handler
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    logger.warning(f"Error de validación en {request.url}: {exc.errors()}")
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={"detail": exc.errors(), "body": exc.body},
    )

# Manejador de excepciones general para capturar traceback
@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    # Obtener el traceback completo
    exc_type, exc_value, exc_traceback = sys.exc_info()
    tb_list = traceback.format_exception(exc_type, exc_value, exc_traceback)
    tb_str = ''.join(tb_list)
    
    # Log del error completo
    logger.error(f"❌ Error 500 en {request.url}:")
    logger.error(f"Tipo de error: {type(exc).__name__}")
    logger.error(f"Mensaje: {str(exc)}")
    logger.error(f"Traceback completo:\n{tb_str}")
    
    # En desarrollo, devolver el traceback completo
    if settings.DEBUG:
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "detail": "Error interno del servidor",
                "error_type": type(exc).__name__,
                "error_message": str(exc),
                "traceback": tb_str,
                "url": str(request.url)
            }
        )
    else:
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"detail": "Error interno del servidor"}
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