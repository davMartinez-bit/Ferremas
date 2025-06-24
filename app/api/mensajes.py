from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime

from app.data.database import get_db
from app.data.models.usuarios import Usuario
from app.data.models.webpay import Mensaje
from app.core.security import get_current_user
from app.api.schemas import MensajeCreate, MensajeUpdate, MensajeResponse

router = APIRouter(prefix="/api/mensajes", tags=["Mensajes"])

@router.post("/enviar", response_model=MensajeResponse)
async def enviar_mensaje(
    mensaje_data: MensajeCreate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """
    Enviar un nuevo mensaje
    """
    try:
        nuevo_mensaje = Mensaje(
            cliente_nombre=mensaje_data.cliente_nombre,
            cliente_email=mensaje_data.cliente_email,
            cliente_telefono=mensaje_data.cliente_telefono,
            vendedor_id=mensaje_data.vendedor_id,
            asunto=mensaje_data.asunto,
            contenido=mensaje_data.contenido,
            fecha=datetime.now(),
            leido=False,
            respondido=False,
            pedido_id=mensaje_data.pedido_id,
            producto_id=mensaje_data.producto_id
        )
        
        db.add(nuevo_mensaje)
        db.commit()
        db.refresh(nuevo_mensaje)
        
        return nuevo_mensaje
        
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al enviar mensaje: {str(e)}"
        )

@router.get("/", response_model=List[MensajeResponse])
async def obtener_mensajes(
    skip: int = 0,
    limit: int = 100,
    leido: Optional[bool] = None,
    respondido: Optional[bool] = None,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """
    Obtener mensajes con filtros opcionales
    """
    try:
        query = db.query(Mensaje)
        
        # Filtrar por usuario (cliente o vendedor)
        if current_user.rol == "cliente":
            query = query.filter(Mensaje.cliente_email == current_user.email)
        elif current_user.rol == "vendedor":
            query = query.filter(Mensaje.vendedor_id == current_user.id)
        
        # Aplicar filtros adicionales
        if leido is not None:
            query = query.filter(Mensaje.leido == leido)
        
        if respondido is not None:
            query = query.filter(Mensaje.respondido == respondido)
        
        mensajes = query.offset(skip).limit(limit).all()
        return mensajes
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener mensajes: {str(e)}"
        )

@router.get("/{mensaje_id}", response_model=MensajeResponse)
async def obtener_mensaje(
    mensaje_id: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """
    Obtener un mensaje específico
    """
    try:
        mensaje = db.query(Mensaje).filter(Mensaje.id == mensaje_id).first()
        
        if not mensaje:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Mensaje no encontrado"
            )
        
        # Verificar permisos
        if current_user.rol == "cliente" and mensaje.cliente_email != current_user.email:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="No tienes permisos para ver este mensaje"
            )
        
        return mensaje
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener mensaje: {str(e)}"
        )

@router.put("/{mensaje_id}/leer", response_model=MensajeResponse)
async def marcar_como_leido(
    mensaje_id: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """
    Marcar un mensaje como leído
    """
    try:
        mensaje = db.query(Mensaje).filter(Mensaje.id == mensaje_id).first()
        
        if not mensaje:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Mensaje no encontrado"
            )
        
        # Verificar permisos
        if current_user.rol == "cliente" and mensaje.cliente_email != current_user.email:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="No tienes permisos para modificar este mensaje"
            )
        
        mensaje.leido = True
        db.commit()
        db.refresh(mensaje)
        
        return mensaje
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al marcar mensaje como leído: {str(e)}"
        )

@router.put("/{mensaje_id}/responder", response_model=MensajeResponse)
async def responder_mensaje(
    mensaje_id: int,
    respuesta: MensajeUpdate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """
    Responder a un mensaje (solo vendedores)
    """
    try:
        if current_user.rol != "vendedor":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Solo los vendedores pueden responder mensajes"
            )
        
        mensaje = db.query(Mensaje).filter(Mensaje.id == mensaje_id).first()
        
        if not mensaje:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Mensaje no encontrado"
            )
        
        # Actualizar mensaje original
        mensaje.respondido = True
        mensaje.leido = True
        
        # Crear mensaje de respuesta
        respuesta_mensaje = Mensaje(
            cliente_nombre=current_user.nombre,
            cliente_email=current_user.email,
            cliente_telefono=current_user.telefono,
            vendedor_id=None,  # No es vendedor, es respuesta
            asunto=f"Re: {mensaje.asunto}",
            contenido=respuesta.contenido,
            fecha=datetime.now(),
            leido=False,
            respondido=False,
            pedido_id=mensaje.pedido_id,
            producto_id=mensaje.producto_id
        )
        
        db.add(respuesta_mensaje)
        db.commit()
        db.refresh(mensaje)
        
        return mensaje
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al responder mensaje: {str(e)}"
        )

@router.get("/no-leidos/count")
async def contar_mensajes_no_leidos(
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """
    Contar mensajes no leídos
    """
    try:
        query = db.query(Mensaje).filter(Mensaje.leido == False)
        
        if current_user.rol == "cliente":
            query = query.filter(Mensaje.cliente_email == current_user.email)
        elif current_user.rol == "vendedor":
            query = query.filter(Mensaje.vendedor_id == current_user.id)
        
        count = query.count()
        return {"count": count}
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al contar mensajes: {str(e)}"
        ) 