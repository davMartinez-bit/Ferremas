# app/data/models/productos.py

from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime, Text, Boolean, Numeric, Index
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
    usuario_id = Column(Integer, nullable=True)
    motivo = Column(String(200))
    producto = relationship("Producto", back_populates="precios")

    __table_args__ = (
        Index('idx_precio_producto_fecha', 'producto_id', 'fecha'),
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
