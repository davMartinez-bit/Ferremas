from .productos import router as productos_router
from .pagos import router as pagos_router
from .usuarios import router as usuarios_router
from .divisas import router as divisas_router

__all__ = ["productos_router", "pagos_router", "usuarios_router", "divisas_router"]