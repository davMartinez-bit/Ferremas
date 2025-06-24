from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
from decimal import Decimal

from app.data.database import get_db
from app.data.models.usuarios import Usuario
from app.data.models.productos import CarritoItem, Pedido, PedidoItem, Producto
from app.core.security import get_current_user
from app.api.schemas import PedidoCreate, PedidoUpdate, PedidoResponse, PedidoItemResponse

router = APIRouter(prefix="/api/pedidos", tags=["Pedidos"])

@router.post("/crear", response_model=PedidoResponse)
async def crear_pedido(
    pedido_data: PedidoCreate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """
    Crear un nuevo pedido desde el carrito
    """
    try:
        # Obtener items del carrito del usuario
        carrito_items = db.query(CarritoItem).filter(
            CarritoItem.usuario_id == current_user.id
        ).all()
        
        if not carrito_items:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="El carrito está vacío"
            )
        
        # Calcular total del pedido
        total = Decimal('0.0')
        items_pedido = []
        
        for item in carrito_items:
            producto = db.query(Producto).filter(Producto.id == item.producto_id).first()
            if not producto:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Producto {item.producto_id} no encontrado"
                )
            
            # Verificar stock
            if producto.stock < item.cantidad:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Stock insuficiente para {producto.nombre}. Disponible: {producto.stock}"
                )
            
            # Obtener precio actual del producto
            precio_actual = db.query(Producto).filter(Producto.id == item.producto_id).first()
            if precio_actual:
                subtotal = Decimal(str(precio_actual.precio)) * item.cantidad
                total += subtotal
                
                # Preparar item del pedido
                items_pedido.append({
                    'producto_id': item.producto_id,
                    'cantidad': item.cantidad,
                    'precio_unitario': precio_actual.precio,
                    'subtotal': subtotal
                })
        
        # Crear el pedido
        nuevo_pedido = Pedido(
            usuario_id=current_user.id,
            total=total,
            estado="pendiente",
            direccion_entrega=pedido_data.direccion_entrega,
            telefono_contacto=pedido_data.telefono_contacto,
            notas=pedido_data.notas,
            fecha_creacion=datetime.now(),
            fecha_actualizacion=datetime.now()
        )
        
        db.add(nuevo_pedido)
        db.flush()  # Para obtener el ID del pedido
        
        # Crear items del pedido
        for item_data in items_pedido:
            pedido_item = PedidoItem(
                pedido_id=nuevo_pedido.id,
                producto_id=item_data['producto_id'],
                cantidad=item_data['cantidad'],
                precio_unitario=item_data['precio_unitario'],
                subtotal=item_data['subtotal']
            )
            db.add(pedido_item)
            
            # Actualizar stock del producto
            producto = db.query(Producto).filter(Producto.id == item_data['producto_id']).first()
            producto.stock -= item_data['cantidad']
        
        # Limpiar carrito
        for item in carrito_items:
            db.delete(item)
        
        db.commit()
        db.refresh(nuevo_pedido)
        
        return nuevo_pedido
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al crear pedido: {str(e)}"
        )

@router.get("/", response_model=List[PedidoResponse])
async def listar_pedidos(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """
    Listar pedidos del usuario
    """
    try:
        pedidos = db.query(Pedido).filter(
            Pedido.usuario_id == current_user.id
        ).offset(skip).limit(limit).all()
        
        return pedidos
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al listar pedidos: {str(e)}"
        )

@router.get("/{pedido_id}", response_model=PedidoResponse)
async def obtener_pedido(
    pedido_id: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """
    Obtener detalle de un pedido específico
    """
    try:
        pedido = db.query(Pedido).filter(
            Pedido.id == pedido_id,
            Pedido.usuario_id == current_user.id
        ).first()
        
        if not pedido:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Pedido no encontrado"
            )
        
        return pedido
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener pedido: {str(e)}"
        )

@router.put("/{pedido_id}/estado", response_model=PedidoResponse)
async def actualizar_estado_pedido(
    pedido_id: int,
    estado_update: PedidoUpdate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """
    Actualizar estado de un pedido
    """
    try:
        pedido = db.query(Pedido).filter(
            Pedido.id == pedido_id,
            Pedido.usuario_id == current_user.id
        ).first()
        
        if not pedido:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Pedido no encontrado"
            )
        
        # Validar estado
        estados_validos = ["pendiente", "confirmado", "en_proceso", "enviado", "entregado", "cancelado"]
        if estado_update.estado not in estados_validos:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Estado inválido. Estados válidos: {estados_validos}"
            )
        
        pedido.estado = estado_update.estado
        pedido.fecha_actualizacion = datetime.now()
        
        db.commit()
        db.refresh(pedido)
        
        return pedido
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al actualizar estado: {str(e)}"
        )

@router.get("/{pedido_id}/items", response_model=List[PedidoItemResponse])
async def obtener_items_pedido(
    pedido_id: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """
    Obtener items de un pedido específico
    """
    try:
        # Verificar que el pedido pertenece al usuario
        pedido = db.query(Pedido).filter(
            Pedido.id == pedido_id,
            Pedido.usuario_id == current_user.id
        ).first()
        
        if not pedido:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Pedido no encontrado"
            )
        
        items = db.query(PedidoItem).filter(
            PedidoItem.pedido_id == pedido_id
        ).all()
        
        return items
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener items del pedido: {str(e)}"
        )

@router.get("/numero/{numero_pedido}", response_model=PedidoResponse)
async def obtener_pedido_por_numero(
    numero_pedido: str,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """
    Obtener pedido por número de pedido (para rastreo)
    """
    try:
        pedido = db.query(Pedido).filter(
            Pedido.numero_pedido == numero_pedido,
            Pedido.usuario_id == current_user.id
        ).first()
        
        if not pedido:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Pedido no encontrado"
            )
        
        return pedido
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener pedido: {str(e)}"
        )

@router.get("/{pedido_id}/detalles")
async def obtener_detalles_pedido(
    pedido_id: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """
    Obtener detalles completos de un pedido incluyendo sus items
    """
    try:
        # Obtener el pedido con sus items
        pedido = db.query(Pedido).filter(
            Pedido.id == pedido_id,
            Pedido.usuario_id == current_user.id
        ).first()
        
        if not pedido:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Pedido no encontrado"
            )
        
        # Obtener los items del pedido con información del producto
        items = db.query(PedidoItem).join(Producto).filter(
            PedidoItem.pedido_id == pedido_id
        ).all()
        
        # Formatear la respuesta
        detalles_pedido = {
            "pedido": {
                "id": pedido.id,
                "numero_pedido": pedido.numero_pedido,
                "total": float(pedido.total),
                "subtotal": float(pedido.subtotal),
                "iva": float(pedido.iva),
                "estado": pedido.estado,
                "metodo_pago": pedido.metodo_pago,
                "direccion_envio": pedido.direccion_envio,
                "telefono_contacto": pedido.telefono_contacto,
                "email_contacto": pedido.email_contacto,
                "notas": pedido.notas,
                "fecha_creacion": pedido.fecha_creacion,
            },
            "items": [
                {
                    "id": item.id,
                    "producto_id": item.producto_id,
                    "producto_nombre": item.producto.nombre,
                    "producto_descripcion": item.producto.descripcion,
                    "cantidad": item.cantidad,
                    "precio_unitario": float(item.precio_unitario),
                    "subtotal": float(item.subtotal)
                }
                for item in items
            ]
        }
        
        return detalles_pedido
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener detalles del pedido: {str(e)}"
        ) 