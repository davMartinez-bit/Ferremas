# app/data/models/webpay.py

from sqlalchemy import Column, Integer, String, Numeric, Boolean, DateTime, Text, ForeignKey, Enum, Index
from sqlalchemy.orm import relationship
from datetime import datetime
from app.data.database import Base


class Mensaje(Base):
    __tablename__ = 'mensajes'

    id = Column(Integer, primary_key=True, autoincrement=True)
    usuario_id = Column(Integer, ForeignKey('usuarios.id', ondelete='SET NULL'), nullable=True)
    pedido_id = Column(Integer, ForeignKey('pedidos.id', ondelete='SET NULL'), nullable=True)
    producto_id = Column(Integer, ForeignKey('productos.id', ondelete='SET NULL'), nullable=True)
    cliente_nombre = Column(String(100), nullable=False)
    cliente_email = Column(String(100), nullable=False)
    cliente_telefono = Column(String(20))
    vendedor_id = Column(Integer, nullable=True)
    asunto = Column(String(200))
    contenido = Column(Text, nullable=False)
    fecha = Column(DateTime, default=datetime.utcnow, nullable=False)
    leido = Column(Boolean, default=False, nullable=False)
    respondido = Column(Boolean, default=False, nullable=False)
    tipo = Column(Enum('CONSULTA', 'SOPORTE', 'VENTA', 'GENERAL'), default='GENERAL')
    prioridad = Column(Enum('BAJA', 'MEDIA', 'ALTA'), default='MEDIA')
    
    usuario = relationship('Usuario', foreign_keys=[usuario_id])
    pedido = relationship('Pedido', foreign_keys=[pedido_id])
    producto = relationship('Producto', foreign_keys=[producto_id])
    
    __table_args__ = (
        Index('idx_mensaje_usuario', 'usuario_id'),
        Index('idx_mensaje_tipo', 'tipo'),
        Index('idx_mensaje_prioridad', 'prioridad'),
        Index('idx_mensaje_pedido', 'pedido_id'),
        Index('idx_mensaje_producto', 'producto_id'),
    )


class Pago(Base):
    __tablename__ = 'pagos'

    id = Column(Integer, primary_key=True, autoincrement=True)
    token = Column(String(100), unique=True, nullable=False)
    orden_id = Column(String(50), unique=True, nullable=False)
    monto = Column(Numeric(12, 2), nullable=False)
    estado = Column(String(20), default='PENDIENTE', nullable=False)
    metodo_pago = Column(String(50))
    cliente_email = Column(String(100))
    cliente_nombre = Column(String(100))
    return_url = Column(String(500))
    fecha_creacion = Column(DateTime, default=datetime.utcnow, nullable=False)
    fecha_actualizacion = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    fecha_confirmacion = Column(DateTime)
    usuario_id = Column(Integer, ForeignKey('usuarios.id', ondelete='SET NULL'), nullable=True)
    pedido_id = Column(Integer, ForeignKey('pedidos.id', ondelete='SET NULL'), nullable=True)
    
    usuario = relationship('Usuario', foreign_keys=[usuario_id])
    pedido = relationship('Pedido', foreign_keys=[pedido_id])
    