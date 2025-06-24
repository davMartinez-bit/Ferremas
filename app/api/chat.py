# app/api/chat.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime

from app.data.database import get_db
from app.data.models.usuarios import Usuario, Chat, ChatMensaje
from app.core.security import get_current_user
from app.api.schemas import (
    ChatCreate, ChatResponse, ChatMensajeCreate, 
    ChatMensajeResponse, ChatListResponse
)

router = APIRouter(prefix="/api/chat", tags=["Chat"])

# =============================================================================
# ENDPOINTS PARA CLIENTES
# =============================================================================

@router.post("/iniciar", response_model=ChatResponse)
async def iniciar_chat(
    chat_data: ChatCreate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """Iniciar un nuevo chat de soporte"""
    rol = getattr(current_user.rol, 'value', current_user.rol)
    if rol != "cliente":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Solo los clientes pueden iniciar chats"
        )
    
    # Verificar si ya tiene un chat abierto
    chat_existente = db.query(Chat).filter(
        Chat.cliente_id == current_user.id,
        Chat.estado == "abierto"
    ).first()
    
    if chat_existente:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Ya tienes un chat abierto. Usa ese chat para continuar."
        )
    
    # Crear nuevo chat
    nuevo_chat = Chat(
        cliente_id=current_user.id,
        asunto=chat_data.asunto,
        estado="abierto"
    )
    db.add(nuevo_chat)
    db.commit()
    db.refresh(nuevo_chat)
    
    # Crear mensaje automático del bot
    mensaje_bot = ChatMensaje(
        chat_id=nuevo_chat.id,
        remitente_id=current_user.id,  # Usar el mismo usuario para el bot
        contenido="¡Hola! Gracias por contactarnos. Un administrador te responderá pronto. Mientras tanto, puedes describir tu consulta y te atenderemos lo antes posible.",
        tipo="bot"
    )
    db.add(mensaje_bot)
    db.commit()
    
    return nuevo_chat

@router.get("/mi-chat", response_model=ChatResponse)
async def obtener_mi_chat(
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """Obtener el chat activo del cliente"""
    rol = getattr(current_user.rol, 'value', current_user.rol)
    if rol != "cliente":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Solo los clientes pueden acceder a este endpoint"
        )
    
    chat = db.query(Chat).filter(
        Chat.cliente_id == current_user.id,
        Chat.estado == "abierto"
    ).first()
    
    if not chat:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No tienes un chat activo"
        )
    
    # Marcar como leído por el cliente
    chat.leido_cliente = True
    db.commit()
    
    return chat

@router.get("/mi-chat/mensajes", response_model=List[ChatMensajeResponse])
async def obtener_mensajes_chat(
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """Obtener mensajes del chat activo del cliente"""
    rol = getattr(current_user.rol, 'value', current_user.rol)
    if rol != "cliente":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Solo los clientes pueden acceder a este endpoint"
        )
    
    chat = db.query(Chat).filter(
        Chat.cliente_id == current_user.id,
        Chat.estado == "abierto"
    ).first()
    
    if not chat:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No tienes un chat activo"
        )
    
    mensajes = db.query(ChatMensaje).filter(
        ChatMensaje.chat_id == chat.id
    ).order_by(ChatMensaje.fecha_envio.asc()).all()
    
    # Marcar mensajes como leídos
    for mensaje in mensajes:
        if mensaje.remitente_id != current_user.id:
            mensaje.leido = True
    
    chat.leido_cliente = True
    db.commit()
    
    return mensajes

@router.post("/enviar-mensaje", response_model=ChatMensajeResponse)
async def enviar_mensaje_cliente(
    mensaje_data: ChatMensajeCreate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """Enviar mensaje en el chat activo del cliente"""
    rol = getattr(current_user.rol, 'value', current_user.rol)
    if rol != "cliente":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Solo los clientes pueden enviar mensajes"
        )
    
    chat = db.query(Chat).filter(
        Chat.cliente_id == current_user.id,
        Chat.estado == "abierto"
    ).first()
    
    if not chat:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No tienes un chat activo"
        )
    
    nuevo_mensaje = ChatMensaje(
        chat_id=chat.id,
        remitente_id=current_user.id,
        contenido=mensaje_data.contenido,
        tipo="usuario"
    )
    db.add(nuevo_mensaje)
    
    # Actualizar fecha de última actividad
    chat.fecha_ultima_actividad = datetime.utcnow()
    chat.leido_admin = False  # Marcar como no leído por admin
    
    db.commit()
    db.refresh(nuevo_mensaje)
    
    return nuevo_mensaje

# =============================================================================
# ENDPOINTS PARA ADMINISTRADORES
# =============================================================================

@router.get("/admin/chats", response_model=ChatListResponse)
async def listar_chats_admin(
    estado: str = None,
    skip: int = 0,
    limit: int = 50,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """Listar todos los chats (solo admin)"""
    rol = getattr(current_user.rol, 'value', current_user.rol)
    if rol not in ["admin", "empleado"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Solo administradores pueden acceder a este endpoint"
        )
    
    query = db.query(Chat)
    
    if estado:
        query = query.filter(Chat.estado == estado)
    
    total = query.count()
    chats = query.order_by(Chat.fecha_ultima_actividad.desc()).offset(skip).limit(limit).all()
    
    # Contar chats no leídos
    no_leidos = db.query(Chat).filter(Chat.leido_admin == False).count()
    
    return {
        "chats": chats,
        "total": total,
        "no_leidos": no_leidos
    }

@router.get("/admin/chats/{chat_id}", response_model=ChatResponse)
async def obtener_chat_admin(
    chat_id: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """Obtener un chat específico (admin)"""
    rol = getattr(current_user.rol, 'value', current_user.rol)
    if rol not in ["admin", "empleado"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Solo administradores pueden acceder a este endpoint"
        )
    
    chat = db.query(Chat).filter(Chat.id == chat_id).first()
    
    if not chat:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Chat no encontrado"
        )
    
    # Marcar como leído por admin
    chat.leido_admin = True
    db.commit()
    
    return chat

@router.get("/admin/chats/{chat_id}/mensajes", response_model=List[ChatMensajeResponse])
async def obtener_mensajes_chat_admin(
    chat_id: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """Obtener mensajes de un chat específico (admin)"""
    rol = getattr(current_user.rol, 'value', current_user.rol)
    if rol not in ["admin", "empleado"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Solo administradores pueden acceder a este endpoint"
        )
    
    chat = db.query(Chat).filter(Chat.id == chat_id).first()
    
    if not chat:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Chat no encontrado"
        )
    
    mensajes = db.query(ChatMensaje).filter(
        ChatMensaje.chat_id == chat_id
    ).order_by(ChatMensaje.fecha_envio.asc()).all()
    
    # Marcar mensajes como leídos
    for mensaje in mensajes:
        if mensaje.remitente_id != current_user.id:
            mensaje.leido = True
    
    chat.leido_admin = True
    db.commit()
    
    return mensajes

@router.post("/admin/chats/{chat_id}/responder", response_model=ChatMensajeResponse)
async def responder_chat_admin(
    chat_id: int,
    mensaje_data: ChatMensajeCreate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """Responder a un chat (admin)"""
    rol = getattr(current_user.rol, 'value', current_user.rol)
    if rol not in ["admin", "empleado"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Solo administradores pueden responder chats"
        )
    
    chat = db.query(Chat).filter(Chat.id == chat_id).first()
    
    if not chat:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Chat no encontrado"
        )
    
    # Asignar admin al chat si no está asignado
    if not chat.admin_id:
        chat.admin_id = current_user.id
        chat.estado = "en_proceso"
    
    nuevo_mensaje = ChatMensaje(
        chat_id=chat_id,
        remitente_id=current_user.id,
        contenido=mensaje_data.contenido,
        tipo="admin"
    )
    db.add(nuevo_mensaje)
    
    # Actualizar fecha de última actividad
    chat.fecha_ultima_actividad = datetime.utcnow()
    chat.leido_cliente = False  # Marcar como no leído por cliente
    
    db.commit()
    db.refresh(nuevo_mensaje)
    
    return nuevo_mensaje

@router.put("/admin/chats/{chat_id}/estado")
async def cambiar_estado_chat(
    chat_id: int,
    estado: str,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """Cambiar estado de un chat (admin)"""
    rol = getattr(current_user.rol, 'value', current_user.rol)
    if rol not in ["admin", "empleado"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Solo administradores pueden cambiar el estado"
        )
    
    if estado not in ["abierto", "en_proceso", "cerrado"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Estado inválido"
        )
    
    chat = db.query(Chat).filter(Chat.id == chat_id).first()
    
    if not chat:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Chat no encontrado"
        )
    
    chat.estado = estado
    chat.fecha_ultima_actividad = datetime.utcnow()
    db.commit()
    
    return {"mensaje": f"Estado del chat cambiado a {estado}"}

@router.put("/admin/chats/{chat_id}/marcar-leido")
async def marcar_chat_leido(
    chat_id: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """Marcar chat como leído (admin)"""
    rol = getattr(current_user.rol, 'value', current_user.rol)
    if rol not in ["admin", "empleado"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Solo administradores pueden marcar chats como leídos"
        )
    
    chat = db.query(Chat).filter(Chat.id == chat_id).first()
    
    if not chat:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Chat no encontrado"
        )
    
    chat.leido_admin = True
    db.commit()
    
    return {"mensaje": "Chat marcado como leído"} 