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

    class Config:
        from_attributes = True

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
    
    class Config:
        from_attributes = True

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

    class Config:
        from_attributes = True

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

# =============================================================================
# 🛒 SCHEMAS PARA CARRITO
# =============================================================================

class CarritoItemCreate(BaseModel):
    """Schema para agregar item al carrito"""
    producto_id: int = Field(..., gt=0, description="ID del producto")
    cantidad: int = Field(..., gt=0, description="Cantidad a agregar")

class CarritoItemUpdate(BaseModel):
    """Schema para actualizar cantidad en carrito"""
    cantidad: int = Field(..., gt=0, description="Nueva cantidad")

class CarritoItemResponse(BaseModel):
    """Schema para respuesta de item del carrito"""
    id: int
    usuario_id: int
    producto_id: int
    cantidad: int
    fecha_agregado: datetime
    fecha_actualizacion: datetime
    producto: Optional[ProductoResponse] = None

    class Config:
        from_attributes = True

# =============================================================================
# 📦 SCHEMAS PARA PEDIDOS
# =============================================================================

class PedidoCreate(BaseModel):
    """Schema para crear un pedido"""
    direccion_entrega: str = Field(..., min_length=10, max_length=500)
    telefono_contacto: str = Field(..., min_length=8, max_length=20)
    notas: Optional[str] = Field(None, max_length=1000)

class PedidoUpdate(BaseModel):
    """Schema para actualizar un pedido"""
    estado: str = Field(..., description="Nuevo estado del pedido")
    notas: Optional[str] = Field(None, max_length=1000)

class PedidoResponse(BaseModel):
    """Schema para respuesta de pedido"""
    id: int
    usuario_id: int
    total: float
    estado: str
    direccion_entrega: Optional[str] = None
    telefono_contacto: Optional[str] = None
    notas: Optional[str] = None
    fecha_creacion: datetime
    fecha_actualizacion: datetime
    numero_pedido: Optional[str] = None
    subtotal: Optional[float] = None
    iva: Optional[float] = None
    metodo_pago: Optional[str] = None
    email_contacto: Optional[str] = None
    direccion_envio: Optional[str] = None
    items: Optional[List["PedidoItemResponse"]] = []

    class Config:
        from_attributes = True

class PedidoItemResponse(BaseModel):
    """Schema para item de pedido"""
    id: int
    pedido_id: int
    producto_id: int
    cantidad: int
    precio_unitario: float
    subtotal: float
    producto: Optional[ProductoResponse] = None

    class Config:
        from_attributes = True

# =============================================================================
# 💬 SCHEMAS PARA MENSAJES
# =============================================================================

class MensajeCreate(BaseModel):
    """Schema para crear un mensaje"""
    cliente_nombre: str = Field(..., min_length=2, max_length=100)
    cliente_email: str = Field(..., description="Email del cliente")
    cliente_telefono: Optional[str] = Field(None, max_length=20)
    vendedor_id: Optional[int] = Field(None, description="ID del vendedor")
    asunto: Optional[str] = Field(None, max_length=200)
    contenido: str = Field(..., min_length=1, max_length=2000)
    pedido_id: Optional[int] = Field(None, description="ID del pedido relacionado")
    producto_id: Optional[int] = Field(None, description="ID del producto relacionado")

class MensajeUpdate(BaseModel):
    """Schema para actualizar un mensaje"""
    contenido: str = Field(..., min_length=1, max_length=2000)

class MensajeResponse(BaseModel):
    """Schema para respuesta de mensaje"""
    id: int
    cliente_nombre: str
    cliente_email: str
    cliente_telefono: Optional[str] = None
    vendedor_id: Optional[int] = None
    asunto: Optional[str] = None
    contenido: str
    fecha: datetime
    leido: bool
    respondido: bool
    pedido_id: Optional[int] = None
    producto_id: Optional[int] = None

    class Config:
        from_attributes = True

# =============================================================================
# 👤 SCHEMAS PARA USUARIOS
# =============================================================================

class UsuarioResponse(BaseModel):
    """Schema para respuesta de usuario"""
    id: int
    nombre: Optional[str] = None
    email: str
    # telefono: Optional[str] = None  # TEMPORALMENTE COMENTADO
    rol: str
    activo: bool
    fecha_creacion: datetime

    class Config:
        from_attributes = True

class PerfilUpdate(BaseModel):
    """Schema para actualizar perfil de usuario"""
    nombre: Optional[str] = Field(None, min_length=2, max_length=100)
    telefono: Optional[str] = Field(None, max_length=20)
    # direccion: Optional[str] = Field(None, max_length=500)  # TEMPORALMENTE COMENTADO

class PasswordUpdate(BaseModel):
    """Schema para cambiar contraseña"""
    password_actual: str = Field(..., min_length=6)
    password_nuevo: str = Field(..., min_length=6)

# =============================================================================
# 📊 SCHEMAS PARA ADMIN
# =============================================================================

class AdminStats(BaseModel):
    """Schema para estadísticas del dashboard admin"""
    total_pedidos: int
    pedidos_pendientes: int
    pedidos_entregados: int
    ventas_mes: float
    total_usuarios: int
    usuarios_nuevos_mes: int
    total_productos: int
    productos_bajo_stock: int
    total_pagos: int
    pagos_exitosos: int

# =============================================================================
# ❤️ SCHEMAS PARA FAVORITOS
# =============================================================================

class FavoritoCreate(BaseModel):
    """Schema para crear un favorito"""
    producto_id: int = Field(..., gt=0, description="ID del producto")

class FavoritoResponse(BaseModel):
    """Schema para respuesta de favorito"""
    id: int
    usuario_id: int
    producto_id: int
    fecha_agregado: datetime
    producto_nombre: Optional[str] = None
    producto_precio: Optional[float] = None
    producto_imagen: Optional[str] = None

    class Config:
        from_attributes = True

# =============================================================================
# 💬 SCHEMAS PARA CHAT DE SOPORTE
# =============================================================================

class ChatCreate(BaseModel):
    """Schema para crear un chat"""
    asunto: Optional[str] = Field(None, max_length=200, description="Asunto de la consulta")

class ChatResponse(BaseModel):
    """Schema para respuesta de chat"""
    id: int
    cliente_id: int
    admin_id: Optional[int] = None
    asunto: Optional[str] = None
    estado: str
    leido_cliente: bool
    leido_admin: bool
    fecha_creacion: datetime
    fecha_ultima_actividad: datetime
    cliente_nombre: Optional[str] = None
    admin_nombre: Optional[str] = None
    total_mensajes: int = 0
    mensajes_no_leidos: int = 0

    class Config:
        from_attributes = True

class ChatMensajeCreate(BaseModel):
    """Schema para crear un mensaje de chat"""
    contenido: str = Field(..., min_length=1, max_length=2000, description="Contenido del mensaje")

class ChatMensajeResponse(BaseModel):
    """Schema para respuesta de mensaje de chat"""
    id: int
    chat_id: int
    remitente_id: int
    contenido: str
    tipo: str
    leido: bool
    fecha_envio: datetime
    remitente_nombre: Optional[str] = None
    remitente_rol: Optional[str] = None

    class Config:
        from_attributes = True

class ChatListResponse(BaseModel):
    """Schema para lista de chats (admin)"""
    chats: List[ChatResponse]
    total: int
    no_leidos: int
