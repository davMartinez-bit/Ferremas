from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel
from datetime import datetime, timedelta
import jwt

from app.data.database import get_db
from app.data.models.usuarios import Usuario
from app.core.security import verify_password
from config import settings

router = APIRouter()

class LoginData(BaseModel):
    username: str
    password: str

class LoginResponse(BaseModel):
    access_token: str
    token_type: str
    user: dict

SECRET_KEY = settings.SECRET_KEY
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 1440  # 1 día

def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=15))
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

@router.post("/login", response_model=LoginResponse)
async def login(data: LoginData, db: Session = Depends(get_db)):
    # Buscar usuario por email
    usuario = db.query(Usuario).filter(Usuario.email == data.username).first()
    
    if not usuario or not verify_password(data.password, usuario.password_hash):
        raise HTTPException(status_code=400, detail="Usuario o contraseña incorrectos")
    
    if not usuario.activo:
        raise HTTPException(status_code=400, detail="Usuario inactivo")
    
    # Crear token
    access_token = create_access_token(
        data={"sub": usuario.email, "user_id": usuario.id},
        expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    
    # Devolver información del usuario (sin password)
    user_data = {
        "id": usuario.id,
        "email": usuario.email,
        "nombre": usuario.nombre,
        "rol": usuario.rol,
        "activo": usuario.activo
    }
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": user_data
    }
