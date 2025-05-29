from sqlalchemy.orm import Session
from app.data.models.usuarios import Usuario
from app.data.schemas.usuarios import UsuarioCreate
from app.core.security import hash_password

def get_by_email(db: Session, email: str):
    return db.query(Usuario).filter(Usuario.email == email).first()

def create_usuario(db: Session, usuario_data: UsuarioCreate, rol: str = "cliente"):
    hashed = hash_password(usuario_data.password)
    nuevo = Usuario(
        username=usuario_data.username,
        email=usuario_data.email,
        password_hash=hashed,
        rol=rol
    )
    db.add(nuevo)
    db.commit()
    db.refresh(nuevo)
    return nuevo