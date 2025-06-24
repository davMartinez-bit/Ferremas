from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
import jwt
from datetime import datetime, timedelta
from typing import Optional

from app.data.database import get_db
from app.data.models.usuarios import Usuario
from config import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
security = HTTPBearer(auto_error=False)  # Cambiar a False para desarrollo

# Configuración JWT
SECRET_KEY = settings.SECRET_KEY
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    """Alias para hash_password para compatibilidad"""
    return hash_password(password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """Crear token JWT"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def verify_token(token: str) -> Optional[dict]:
    """Verificar token JWT"""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None

def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    db: Session = Depends(get_db)
) -> Usuario:
    """Obtener usuario actual desde token JWT - MODIFICADO PARA DESARROLLO"""
    
    print(f"DEBUG: get_current_user llamado")
    print(f"DEBUG: credentials = {credentials}")
    print(f"DEBUG: settings.DEBUG = {settings.DEBUG}")
    print(f"DEBUG: SECRET_KEY = {SECRET_KEY[:10]}..." if SECRET_KEY else "DEBUG: SECRET_KEY = None")
    
    # Si no hay token, lanzar error 401 (no usar usuario por defecto)
    if not credentials:
        print(f"DEBUG: No hay credentials, lanzando error 401")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token requerido"
        )
    
    print(f"DEBUG: Verificando token: {credentials.credentials[:20]}...")
    print(f"DEBUG: Token completo: {credentials.credentials}")
    
    try:
        payload = jwt.decode(credentials.credentials, SECRET_KEY, algorithms=[ALGORITHM])
        print(f"DEBUG: Payload decodificado: {payload}")
        username: str = payload.get("sub")
        print(f"DEBUG: Token decodificado, username: {username}")
        
        if username is None:
            print(f"DEBUG: Token no contiene username")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token inválido"
            )
    except jwt.ExpiredSignatureError:
        print(f"DEBUG: Token expirado")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token expirado"
        )
    except jwt.InvalidTokenError as e:
        print(f"DEBUG: Token inválido: {e}")
        print(f"DEBUG: Tipo de error: {type(e)}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido"
        )
    
    # Buscar usuario en la base de datos por email o username
    user = db.query(Usuario).filter(Usuario.email == username).first()
    if not user:
        # Si no se encuentra por email, intentar por username
        user = db.query(Usuario).filter(Usuario.username == username).first()
    
    print(f"DEBUG: Usuario encontrado en DB: {user.email if user else 'None'}")
    
    if user is None:
        print(f"DEBUG: Usuario no encontrado en DB")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuario no encontrado"
        )
    
    return user
