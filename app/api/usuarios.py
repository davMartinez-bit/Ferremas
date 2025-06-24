from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.data.database import get_db
from app.data.schemas.usuarios import UsuarioCreate, UsuarioOut, UsuarioLogin
from app.data.repositories import usuarios as repo
from app.core.security import get_current_user, verify_password, get_password_hash, SECRET_KEY
from app.data.models.usuarios import Usuario
from app.api.schemas import PerfilUpdate, PasswordUpdate, UsuarioResponse
from datetime import datetime, timedelta
import jwt

router = APIRouter(tags=["Usuarios"])

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
    if not user or not verify_password(data.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Credenciales inválidas")

    # Payload con datos que quieres guardar en el token
    payload = {
        "sub": user.email,
        "exp": datetime.utcnow() + timedelta(minutes=60)  # Token válido por 60 min
    }
    # Generar token JWT (usa la clave secreta que tengas en tu módulo security)
    token = jwt.encode(payload, SECRET_KEY, algorithm="HS256")

    return {"access_token": token, "token_type": "bearer", "role": user.rol}

@router.get("/check/{email}", response_model=dict)
def verificar_usuario(email: str, db: Session = Depends(get_db)):
    exists = repo.get_by_email(db, email) is not None
    return {"exists": exists}

# =============================================================================
# 🆕 ENDPOINTS PARA GESTIÓN DE PERFIL
# =============================================================================

@router.get("/me", response_model=UsuarioResponse)
async def obtener_perfil_me(
    current_user: Usuario = Depends(get_current_user)
):
    """
    Obtener perfil del usuario autenticado (endpoint /me para compatibilidad)
    """
    return current_user

@router.put("/me", response_model=UsuarioResponse)
async def actualizar_perfil_me(
    perfil_data: PerfilUpdate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """
    Actualizar perfil del usuario autenticado (endpoint /me para compatibilidad)
    """
    try:
        # Actualizar campos del usuario
        if perfil_data.nombre is not None:
            current_user.nombre = perfil_data.nombre
        
        # if perfil_data.telefono is not None:
        #     current_user.telefono = perfil_data.telefono
        
        # if perfil_data.direccion is not None:
        #     current_user.direccion = perfil_data.direccion
        
        current_user.fecha_actualizacion = datetime.now()
        
        db.commit()
        db.refresh(current_user)
        
        return current_user
        
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Error al actualizar perfil: {str(e)}"
        )

@router.post("/cambiar-password")
async def cambiar_password_me(
    password_data: PasswordUpdate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """
    Cambiar contraseña del usuario autenticado (endpoint /cambiar-password para compatibilidad)
    """
    try:
        # Verificar contraseña actual
        if not verify_password(password_data.password_actual, current_user.password_hash):
            raise HTTPException(
                status_code=400,
                detail="La contraseña actual es incorrecta"
            )
        
        # Verificar que la nueva contraseña sea diferente
        if verify_password(password_data.password_nuevo, current_user.password_hash):
            raise HTTPException(
                status_code=400,
                detail="La nueva contraseña debe ser diferente a la actual"
            )
        
        # Hashear y actualizar nueva contraseña
        new_password_hash = get_password_hash(password_data.password_nuevo)
        current_user.password_hash = new_password_hash
        current_user.fecha_actualizacion = datetime.now()
        
        db.commit()
        
        return {"message": "Contraseña actualizada exitosamente"}
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Error al cambiar contraseña: {str(e)}"
        )

@router.put("/perfil", response_model=UsuarioResponse)
async def actualizar_perfil(
    perfil_data: PerfilUpdate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """
    Actualizar perfil del usuario autenticado
    """
    try:
        # Actualizar campos del usuario
        if perfil_data.nombre is not None:
            current_user.nombre = perfil_data.nombre
        
        # if perfil_data.telefono is not None:
        #     current_user.telefono = perfil_data.telefono
        
        current_user.fecha_actualizacion = datetime.now()
        
        db.commit()
        db.refresh(current_user)
        
        return current_user
        
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Error al actualizar perfil: {str(e)}"
        )

@router.put("/password")
async def cambiar_password(
    password_data: PasswordUpdate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """
    Cambiar contraseña del usuario autenticado
    """
    try:
        # Verificar contraseña actual
        if not verify_password(password_data.password_actual, current_user.password_hash):
            raise HTTPException(
                status_code=400,
                detail="La contraseña actual es incorrecta"
            )
        
        # Verificar que la nueva contraseña sea diferente
        if verify_password(password_data.password_nuevo, current_user.password_hash):
            raise HTTPException(
                status_code=400,
                detail="La nueva contraseña debe ser diferente a la actual"
            )
        
        # Hashear y actualizar nueva contraseña
        new_password_hash = get_password_hash(password_data.password_nuevo)
        current_user.password_hash = new_password_hash
        current_user.fecha_actualizacion = datetime.now()
        
        db.commit()
        
        return {"message": "Contraseña actualizada exitosamente"}
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Error al cambiar contraseña: {str(e)}"
        )

@router.get("/perfil", response_model=UsuarioResponse)
async def obtener_perfil(
    current_user: Usuario = Depends(get_current_user)
):
    """
    Obtener perfil del usuario autenticado
    """
    return current_user
