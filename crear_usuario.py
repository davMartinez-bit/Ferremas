# crear_usuario.py
from datetime import datetime, timezone
from app.data.database import SessionLocal
from app.data.models.usuarios import Usuario, RolEnum
from app.core.security import hash_password  # Asegúrate que esta función existe

# Crea sesión de base de datos
db = SessionLocal()

nuevo_usuario = Usuario(
    username="admin2",
    email="adminn@example.com",
    password_hash=hash_password("admin123"),
    rol=RolEnum.admin,
    activo=True,
    nombre="Admin",
    apellidos="Principal",
    fecha_creacion=datetime.now(timezone.utc),
    fecha_actualizacion=datetime.now(timezone.utc),
)

db.add(nuevo_usuario)
db.commit()
db.refresh(nuevo_usuario)

print(f"✅ Usuario creado con ID: {nuevo_usuario.id}, email: {nuevo_usuario.email}")
db.close()
