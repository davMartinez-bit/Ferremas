from sqlalchemy import Column, Integer, String, Boolean, DateTime, Enum, Text, ForeignKey, Float, DECIMAL
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime
from enum import Enum as PyEnum
from app.data.database import Base

class RolEnum(PyEnum):
    cliente = "cliente"
    empleado = "empleado"
    admin = "admin"

class Usuario(Base):
    __tablename__ = 'usuarios'

    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(50), unique=True, nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    rol = Column(Enum(RolEnum), default=RolEnum.cliente, nullable=False)
    activo = Column(Boolean, default=True)
    nombre = Column(String(100), nullable=True)
    apellidos = Column(String(100), nullable=True)
    telefono = Column(String(20), nullable=True)
    direccion = Column(Text, nullable=True)
    fecha_creacion = Column(DateTime(timezone=True), server_default=func.now())
    fecha_actualizacion = Column(DateTime(timezone=True), onupdate=func.now())

    items_carrito = relationship("CarritoItem", back_populates="usuario")
    pedidos = relationship("Pedido", back_populates="usuario")
    favoritos = relationship("Favorito", back_populates="usuario")
    reseñas = relationship("Reseña", back_populates="usuario")
    notificaciones = relationship("Notificacion", back_populates="usuario")
    chats_cliente = relationship("Chat", foreign_keys="Chat.cliente_id", back_populates="cliente")
    chats_admin = relationship("Chat", foreign_keys="Chat.admin_id", back_populates="admin")

class Chat(Base):
    __tablename__ = "chats"
    
    id = Column(Integer, primary_key=True, index=True)
    cliente_id = Column(Integer, ForeignKey("usuarios.id"), nullable=False)
    admin_id = Column(Integer, ForeignKey("usuarios.id"), nullable=True)
    asunto = Column(String(200), nullable=True)
    estado = Column(String(20), default="abierto")  # abierto, cerrado, en_proceso
    leido_cliente = Column(Boolean, default=False)
    leido_admin = Column(Boolean, default=False)
    fecha_creacion = Column(DateTime(timezone=True), server_default=func.now())
    fecha_ultima_actividad = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relaciones
    cliente = relationship("Usuario", foreign_keys=[cliente_id], back_populates="chats_cliente")
    admin = relationship("Usuario", foreign_keys=[admin_id], back_populates="chats_admin")
    mensajes = relationship("ChatMensaje", back_populates="chat", cascade="all, delete-orphan")

class ChatMensaje(Base):
    __tablename__ = "chat_mensajes"
    
    id = Column(Integer, primary_key=True, index=True)
    chat_id = Column(Integer, ForeignKey("chats.id"), nullable=False)
    remitente_id = Column(Integer, ForeignKey("usuarios.id"), nullable=False)
    contenido = Column(Text, nullable=False)
    tipo = Column(String(20), default="usuario")  # usuario, admin, bot
    leido = Column(Boolean, default=False)
    fecha_envio = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relaciones
    chat = relationship("Chat", back_populates="mensajes")
    remitente = relationship("Usuario")
