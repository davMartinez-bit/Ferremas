# app/api/__init__.py
from .productos import router as productos_router
from .pagos import router as pagos_router
from .usuarios import router as usuarios_router
from .divisas import router as divisas_router
from .carrito import router as carrito_router
from .pedidos import router as pedidos_router
from .mensajes import router as mensajes_router
from .admin import router as admin_router

__all__ = [
    "productos_router",
    "pagos_router", 
    "usuarios_router",
    "divisas_router",
    "carrito_router",
    "pedidos_router",
    "mensajes_router",
    "admin_router"
]