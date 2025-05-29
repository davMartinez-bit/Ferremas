# app/api/schemas.py

from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime

# =============================================================================
# 🟦 SCHEMAS PARA PRODUCTOS
# =============================================================================

class ProductoSearch(BaseModel):
    """Schema para búsqueda rápida de productos"""
    nombre: Optional[str] = None
    categoria: Optional[str] = None
    stock_max: Optional[int] = None

class ProductoBasic(BaseModel):
    """Schema básico para listados de productos"""
    codigo: str
    nombre: str
    stock: int
    precio_actual: Optional[float] = None
    categoria: Optional[str] = None
    marca: Optional[str] = None

class ProductoResponse(BaseModel):
    """Schema completo para detalles de producto"""
    id: int
    codigo: str
    nombre: str
    descripcion: Optional[str] = None
    stock: int
    precio_actual: Optional[float] = None
    fecha_creacion: datetime
    categoria: Optional["CategoriaResponse"] = None
    marca: Optional["MarcaResponse"] = None

class ProductoCreate(BaseModel):
    """Schema para crear un producto"""
    codigo: str = Field(..., min_length=3, max_length=20, description="Código único del producto")
    nombre: str = Field(..., min_length=3, max_length=200, description="Nombre del producto")
    descripcion: Optional[str] = Field(None, max_length=1000, description="Descripción del producto")
    stock: int = Field(default=0, ge=0, description="Cantidad en stock")
    precio_actual: float = Field(..., gt=0, description="Precio actual del producto")
    categoria_id: Optional[int] = Field(None, description="ID de la categoría")
    marca_id: Optional[int] = Field(None, description="ID de la marca")

class ProductoUpdate(BaseModel):
    """Schema para actualizar un producto"""
    nombre: Optional[str] = Field(None, min_length=3, max_length=200)
    descripcion: Optional[str] = Field(None, max_length=1000)
    stock: Optional[int] = Field(None, ge=0)
    precio_actual: Optional[float] = Field(None, gt=0)
    categoria_id: Optional[int] = None
    marca_id: Optional[int] = None

class ProductosDestacadosResponse(BaseModel):
    """Schema para productos destacados"""
    promociones: List[ProductoBasic] = []
    lanzamientos: List[ProductoBasic] = []

# =============================================================================
# 🟨 SCHEMAS PARA CATEGORÍAS Y SUBCATEGORÍAS
# =============================================================================

class CategoriaResponse(BaseModel):
    id: int
    nombre: str
    descripcion: Optional[str] = None

class CategoriaCreate(BaseModel):
    nombre: str = Field(..., min_length=2, max_length=100)
    descripcion: Optional[str] = Field(None, max_length=500)
    padre_id: Optional[int] = None

class SubcategoriaResponse(BaseModel):
    """Schema para subcategorías anidadas"""
    id: int
    nombre: str
    descripcion: Optional[str] = None
    subcategorias: List["SubcategoriaResponse"] = []

class CategoriaCompleteResponse(BaseModel):
    """Schema completo para categorías con subcategorías"""
    id: int
    nombre: str
    descripcion: Optional[str] = None
    subcategorias: List[SubcategoriaResponse] = []

SubcategoriaResponse.model_rebuild()

# =============================================================================
# 🟥 SCHEMAS PARA MARCAS
# =============================================================================

class MarcaResponse(BaseModel):
    id: int
    nombre: str
    codigo: Optional[str] = None

class MarcaCreate(BaseModel):
    nombre: str = Field(..., min_length=2, max_length=100)
    codigo: Optional[str] = Field(None, max_length=20)

class MarcaCompleteResponse(BaseModel):
    """Schema completo para marcas con información adicional"""
    id: int
    nombre: str
    codigo: Optional[str] = None
    total_productos: int = 0

# =============================================================================
# 🟪 SCHEMAS PARA PRECIOS
# =============================================================================

class PrecioHistoricoResponse(BaseModel):
    valor: float
    fecha: datetime

class HistorialPreciosResponse(BaseModel):
    """Schema para historial de precios"""
    producto: dict
    precio_actual: Optional[float] = None
    historial: List[PrecioHistoricoResponse]

# =============================================================================
# 🟧 SCHEMAS PARA ESTADÍSTICAS GENERALES
# =============================================================================

class EstadisticasGenerales(BaseModel):
    """Resumen general para dashboard o panel administrativo"""
    total_productos: int
    total_categorias: int
    total_marcas: int
    total_proveedores: int

# =============================================================================
# 🟩 SCHEMAS PARA BÚSQUEDA AVANZADA
# =============================================================================

class FiltrosProducto(BaseModel):
    """Schema para aplicar múltiples filtros en búsquedas"""
    nombre: Optional[str] = None
    categoria_id: Optional[int] = None
    marca_id: Optional[int] = None
    stock_min: Optional[int] = None
    stock_max: Optional[int] = None
    precio_min: Optional[float] = None
    precio_max: Optional[float] = None
    solo_destacados: Optional[bool] = False
    solo_promociones: Optional[bool] = False
    stock_bajo: Optional[bool] = False
    solo_activos: Optional[bool] = True
