from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.data.database import get_db
from app.data.schemas.usuarios import UsuarioCreate, UsuarioOut, UsuarioLogin
from app.data.repositories import usuarios as repo
from app.core import security
from datetime import datetime, timedelta
import jwt

router = APIRouter(tags=["Usuarios"])  # Sin prefijo aquí





@router.post("/", response_model=UsuarioOut)
def crear_usuario(usuario: UsuarioCreate, db: Session = Depends(get_db)):
    if repo.get_by_email(db, usuario.email):
        raise HTTPException(status_code=400, detail="El correo ya está registrado.")
    if not usuario.email or not usuario.email.strip():
        raise HTTPException(status_code=400, detail="El email es requerido.")
    if not usuario.password or not usuario.password.strip():
        raise HTTPException(status_code=400, detail="La contraseña es requerida.")

    # Aquí asignamos rol fijo "cliente" y username por defecto si no viene
    rol_fijo = "cliente"
    username = usuario.username or usuario.email.split('@')[0]

    # Creamos un nuevo UsuarioCreate con los datos ajustados (sin modificar input original)
    from app.data.schemas.usuarios import UsuarioCreate as UsuarioCreateModel
    usuario_modificado = UsuarioCreateModel(
        email=usuario.email,
        username=username,
        password=usuario.password
    )

    try:
        nuevo_usuario = repo.create_usuario(db, usuario_modificado, rol=rol_fijo)
        return nuevo_usuario
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al crear usuario: {str(e)}")

@router.post("/login", response_model=dict)
def login_usuario(data: UsuarioLogin, db: Session = Depends(get_db)):
    user = repo.get_by_email(db, data.email)
    if not user or not security.verify_password(data.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Credenciales inválidas")

    
    

@router.get("/check/{email}", response_model=dict)
def verificar_usuario(email: str, db: Session = Depends(get_db)):
    exists = repo.get_by_email(db, email) is not None
    return {"exists": exists}

@router.post("/login", response_model=dict)
def login_usuario(data: UsuarioLogin, db: Session = Depends(get_db)):
    user = repo.get_by_email(db, data.email)
    if not user or not security.verify_password(data.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Credenciales inválidas")

    # Payload con datos que quieres guardar en el token
    payload = {
        "sub": user.email,
        "exp": datetime.utcnow() + timedelta(minutes=60)  # Token válido por 60 min
    }
    # Generar token JWT (usa la clave secreta que tengas en tu módulo security)
    token = jwt.encode(payload, security.SECRET_KEY, algorithm="HS256")

    return {"access_token": token, "token_type": "bearer"}
