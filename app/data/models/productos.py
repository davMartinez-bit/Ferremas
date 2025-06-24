# app/data/models/productos.py

from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime, Text, Boolean, Numeric, Index, Enum
from sqlalchemy.orm import relationship
from datetime import datetime
from app.data.database import Base


class Categoria(Base):
    __tablename__ = 'categorias'

    id = Column(Integer, primary_key=True, autoincrement=True)
    nombre = Column(String(100), nullable=False, index=True)
    descripcion = Column(Text)
    codigo = Column(String(20), unique=True, nullable=False)
    activo = Column(Boolean, default=True, nullable=False)
    orden = Column(Integer, default=0)
    padre_id = Column(Integer, ForeignKey('categorias.id'), nullable=True)
    padre = relationship("Categoria", remote_side=[id], backref="subcategorias")
    productos = relationship("Producto", back_populates="categoria")
    fecha_creacion = Column(DateTime, default=datetime.utcnow, nullable=False)
    fecha_actualizacion = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class Marca(Base):
    __tablename__ = 'marcas'

    id = Column(Integer, primary_key=True, autoincrement=True)
    nombre = Column(String(100), nullable=False, index=True)
    codigo = Column(String(20), unique=True, nullable=False)
    descripcion = Column(Text)
    activo = Column(Boolean, default=True, nullable=False)
    pais_origen = Column(String(50))
    sitio_web = Column(String(200))
    productos = relationship("Producto", back_populates="marca")
    fecha_creacion = Column(DateTime, default=datetime.utcnow, nullable=False)
    fecha_actualizacion = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class Producto(Base):
    __tablename__ = 'productos'

    id = Column(Integer, primary_key=True, autoincrement=True)
    codigo = Column(String(50), unique=True, nullable=False, index=True)
    nombre = Column(String(200), nullable=False, index=True)
    descripcion = Column(Text)
    stock = Column(Integer, default=0, nullable=False)
    stock_minimo = Column(Integer, default=5, nullable=False)
    unidad_medida = Column(String(20), default="unidad", nullable=False)
    activo = Column(Boolean, default=True, nullable=False)
    destacado = Column(Boolean, default=False, nullable=False)
    en_promocion = Column(Boolean, default=False, nullable=False)
    peso = Column(Numeric(10, 3))
    dimensiones = Column(String(100))
    color = Column(String(50))
    modelo = Column(String(100))
    categoria_id = Column(Integer, ForeignKey('categorias.id'), nullable=True)
    categoria = relationship("Categoria", back_populates="productos")
    marca_id = Column(Integer, ForeignKey('marcas.id'), nullable=True)
    marca = relationship("Marca", back_populates="productos")
    precios = relationship("PrecioHistorico", back_populates="producto", cascade="all, delete-orphan")
    items_carrito = relationship("CarritoItem", back_populates="producto")
    fecha_creacion = Column(DateTime, default=datetime.utcnow, nullable=False)
    fecha_actualizacion = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    __table_args__ = (
        Index('idx_producto_categoria_activo', 'categoria_id', 'activo'),
        Index('idx_producto_marca_activo', 'marca_id', 'activo'),
        Index('idx_producto_stock', 'stock'),
        Index('idx_producto_destacado', 'destacado', 'activo'),
        Index('idx_producto_promocion', 'en_promocion', 'activo'),
    )

    @property
    def precio_actual(self):
        if self.precios:
            precios_ordenados = sorted(self.precios, key=lambda x: x.fecha, reverse=True)
            return float(precios_ordenados[0].valor)
        return None


class PrecioHistorico(Base):
    __tablename__ = 'precios_historicos'

    id = Column(Integer, primary_key=True, autoincrement=True)
    producto_id = Column(Integer, ForeignKey('productos.id', ondelete='CASCADE'), nullable=False)
    valor = Column(Numeric(12, 2), nullable=False)
    fecha = Column(DateTime, default=datetime.utcnow, nullable=False)
    usuario_id = Column(Integer, ForeignKey('usuarios.id', ondelete='SET NULL'), nullable=True)
    motivo = Column(String(200))
    producto = relationship("Producto", back_populates="precios")

    __table_args__ = (
        Index('idx_precio_producto_fecha', 'producto_id', 'fecha'),
        Index('idx_precio_usuario', 'usuario_id'),
    )


class Proveedor(Base):
    __tablename__ = 'proveedores'

    id = Column(Integer, primary_key=True, autoincrement=True)
    nombre = Column(String(100), nullable=False)
    codigo = Column(String(20), unique=True, nullable=False)
    rut = Column(String(12), unique=True)
    telefono = Column(String(20))
    email = Column(String(100))
    direccion = Column(Text)
    activo = Column(Boolean, default=True, nullable=False)
    fecha_creacion = Column(DateTime, default=datetime.utcnow, nullable=False)
    fecha_actualizacion = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


# =====================================================
# NUEVOS MODELOS PARA EL SISTEMA DE CARRITO Y PEDIDOS
# =====================================================

class CarritoItem(Base):
    __tablename__ = 'carrito_items'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    usuario_id = Column(Integer, ForeignKey('usuarios.id', ondelete='CASCADE'), nullable=False)
    producto_id = Column(Integer, ForeignKey('productos.id', ondelete='CASCADE'), nullable=False)
    cantidad = Column(Integer, nullable=False, default=1)
    fecha_agregado = Column(DateTime, default=datetime.utcnow)
    fecha_actualizacion = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    usuario = relationship("Usuario", back_populates="items_carrito")
    producto = relationship("Producto", back_populates="items_carrito")

    __table_args__ = (
        Index('unique_carrito_item', 'usuario_id', 'producto_id', unique=True),
        Index('idx_carrito_usuario', 'usuario_id'),
        Index('idx_carrito_producto', 'producto_id'),
    )


class Pedido(Base):
    __tablename__ = 'pedidos'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    numero_pedido = Column(String(20), unique=True, nullable=False)
    usuario_id = Column(Integer, ForeignKey('usuarios.id', ondelete='CASCADE'), nullable=False)
    total = Column(Numeric(12, 2), nullable=False)
    subtotal = Column(Numeric(12, 2), nullable=False)
    iva = Column(Numeric(12, 2), nullable=False, default=0)
    estado = Column(Enum('PENDIENTE', 'CONFIRMADO', 'ENVIADO', 'ENTREGADO', 'CANCELADO'), default='PENDIENTE')
    metodo_pago = Column(String(50))
    direccion_envio = Column(Text)
    telefono_contacto = Column(String(20))
    email_contacto = Column(String(100))
    notas = Column(Text)
    fecha_creacion = Column(DateTime, default=datetime.utcnow)
    fecha_actualizacion = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    fecha_confirmacion = Column(DateTime)
    fecha_envio = Column(DateTime)
    fecha_entrega = Column(DateTime)
    
    # Relaciones
    usuario = relationship("Usuario", back_populates="pedidos")
    items = relationship("PedidoItem", back_populates="pedido", cascade="all, delete-orphan")
    
    __table_args__ = (
        Index('idx_pedido_usuario', 'usuario_id'),
        Index('idx_pedido_estado', 'estado'),
        Index('idx_pedido_fecha', 'fecha_creacion'),
    )


class PedidoItem(Base):
    __tablename__ = 'pedido_items'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    pedido_id = Column(Integer, ForeignKey('pedidos.id', ondelete='CASCADE'), nullable=False)
    producto_id = Column(Integer, ForeignKey('productos.id', ondelete='CASCADE'), nullable=False)
    cantidad = Column(Integer, nullable=False)
    precio_unitario = Column(Numeric(12, 2), nullable=False)
    subtotal = Column(Numeric(12, 2), nullable=False)
    
    # Relaciones
    pedido = relationship("Pedido", back_populates="items")
    producto = relationship("Producto")
    
    __table_args__ = (
        Index('idx_pedido_item_pedido', 'pedido_id'),
        Index('idx_pedido_item_producto', 'producto_id'),
    )


class ProductoProveedor(Base):
    __tablename__ = 'producto_proveedor'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    producto_id = Column(Integer, ForeignKey('productos.id', ondelete='CASCADE'), nullable=False)
    proveedor_id = Column(Integer, ForeignKey('proveedores.id', ondelete='CASCADE'), nullable=False)
    precio_proveedor = Column(Numeric(12, 2))
    codigo_proveedor = Column(String(50))
    stock_proveedor = Column(Integer, default=0)
    activo = Column(Boolean, default=True)
    fecha_creacion = Column(DateTime, default=datetime.utcnow)
    fecha_actualizacion = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    __table_args__ = (
        Index('unique_producto_proveedor', 'producto_id', 'proveedor_id', unique=True),
        Index('idx_producto_proveedor_producto', 'producto_id'),
        Index('idx_producto_proveedor_proveedor', 'proveedor_id'),
    )


class Favorito(Base):
    __tablename__ = 'favoritos'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    usuario_id = Column(Integer, ForeignKey('usuarios.id', ondelete='CASCADE'), nullable=False)
    producto_id = Column(Integer, ForeignKey('productos.id', ondelete='CASCADE'), nullable=False)
    fecha_agregado = Column(DateTime, default=datetime.utcnow)
    
    # Relaciones
    usuario = relationship("Usuario", back_populates="favoritos")
    producto = relationship("Producto")
    
    __table_args__ = (
        Index('unique_favorito', 'usuario_id', 'producto_id', unique=True),
        Index('idx_favorito_usuario', 'usuario_id'),
        Index('idx_favorito_producto', 'producto_id'),
    )


class Reseña(Base):
    __tablename__ = 'reseñas'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    usuario_id = Column(Integer, ForeignKey('usuarios.id', ondelete='CASCADE'), nullable=False)
    producto_id = Column(Integer, ForeignKey('productos.id', ondelete='CASCADE'), nullable=False)
    pedido_id = Column(Integer, ForeignKey('pedidos.id', ondelete='SET NULL'))
    calificacion = Column(Integer, nullable=False)  # 1-5
    comentario = Column(Text)
    activo = Column(Boolean, default=True)
    fecha_creacion = Column(DateTime, default=datetime.utcnow)
    fecha_actualizacion = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relaciones
    usuario = relationship("Usuario", back_populates="reseñas")
    producto = relationship("Producto")
    pedido = relationship("Pedido")
    
    __table_args__ = (
        Index('unique_reseña', 'usuario_id', 'producto_id', 'pedido_id', unique=True),
        Index('idx_reseña_usuario', 'usuario_id'),
        Index('idx_reseña_producto', 'producto_id'),
        Index('idx_reseña_calificacion', 'calificacion'),
    )


class Notificacion(Base):
    __tablename__ = 'notificaciones'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    usuario_id = Column(Integer, ForeignKey('usuarios.id', ondelete='CASCADE'), nullable=False)
    titulo = Column(String(200), nullable=False)
    mensaje = Column(Text, nullable=False)
    tipo = Column(Enum('INFO', 'SUCCESS', 'WARNING', 'ERROR'), default='INFO')
    leida = Column(Boolean, default=False)
    fecha_creacion = Column(DateTime, default=datetime.utcnow)
    fecha_lectura = Column(DateTime)
    
    # Relaciones
    usuario = relationship("Usuario", back_populates="notificaciones")
    
    __table_args__ = (
        Index('idx_notificacion_usuario', 'usuario_id'),
        Index('idx_notificacion_leida', 'leida'),
        Index('idx_notificacion_fecha', 'fecha_creacion'),
    )
