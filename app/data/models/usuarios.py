from sqlalchemy import Column, Integer, String, Boolean, DateTime, Enum
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
    fecha_creacion = Column(DateTime, default=datetime.utcnow)
    fecha_actualizacion = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
