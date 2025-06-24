from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session, joinedload
from typing import List, Optional
from datetime import datetime
import traceback

from app.data.database import get_db
from app.data.models.usuarios import Usuario
from app.data.models.productos import CarritoItem, Producto
from app.core.security import get_current_user
from app.api.schemas import CarritoItemCreate, CarritoItemUpdate, CarritoItemResponse

router = APIRouter(prefix="/api/carrito", tags=["Carrito"])

@router.post("/agregar", response_model=CarritoItemResponse)
async def agregar_al_carrito(
    item: CarritoItemCreate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """
    Agregar un producto al carrito del usuario
    """
    try:
        # Verificar que el producto existe
        producto = db.query(Producto).filter(Producto.id == item.producto_id).first()
        if not producto:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Producto no encontrado"
            )
        
        # Verificar stock disponible
        if producto.stock < item.cantidad:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Stock insuficiente. Disponible: {producto.stock}"
            )
        
        # Verificar si el producto ya está en el carrito
        carrito_existente = db.query(CarritoItem).filter(
            CarritoItem.usuario_id == current_user.id,
            CarritoItem.producto_id == item.producto_id
        ).first()
        
        if carrito_existente:
            # Actualizar cantidad
            carrito_existente.cantidad += item.cantidad
            carrito_existente.fecha_actualizacion = datetime.now()
            db.commit()
            db.refresh(carrito_existente)
            return carrito_existente
        else:
            # Crear nuevo item en carrito
            nuevo_item = CarritoItem(
                usuario_id=current_user.id,
                producto_id=item.producto_id,
                cantidad=item.cantidad,
                fecha_agregado=datetime.now(),
                fecha_actualizacion=datetime.now()
            )
            db.add(nuevo_item)
            db.commit()
            db.refresh(nuevo_item)
            return nuevo_item
            
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        print("TRACEBACK DEL ERROR EN AGREGAR AL CARRITO:")
        traceback.print_exc()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al agregar al carrito: {str(e)}"
        )

@router.get("/", response_model=List[CarritoItemResponse])
async def obtener_carrito(
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """
    Obtener el carrito completo del usuario con detalles del producto
    """
    try:
        items = db.query(CarritoItem).options(
            joinedload(CarritoItem.producto)
        ).filter(
            CarritoItem.usuario_id == current_user.id
        ).all()
        return items
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener carrito: {str(e)}"
        )

@router.put("/actualizar/{item_id}", response_model=CarritoItemResponse)
async def actualizar_cantidad(
    item_id: int,
    item_update: CarritoItemUpdate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """
    Actualizar la cantidad de un item en el carrito
    """
    try:
        # Buscar el item en el carrito del usuario
        carrito_item = db.query(CarritoItem).filter(
            CarritoItem.id == item_id,
            CarritoItem.usuario_id == current_user.id
        ).first()
        
        if not carrito_item:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Item no encontrado en el carrito"
            )
        
        # Verificar stock disponible
        producto = db.query(Producto).filter(Producto.id == carrito_item.producto_id).first()
        if producto.stock < item_update.cantidad:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Stock insuficiente. Disponible: {producto.stock}"
            )
        
        # Actualizar cantidad
        carrito_item.cantidad = item_update.cantidad
        carrito_item.fecha_actualizacion = datetime.now()
        db.commit()
        db.refresh(carrito_item)
        return carrito_item
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al actualizar carrito: {str(e)}"
        )

@router.delete("/eliminar/{item_id}")
async def eliminar_del_carrito(
    item_id: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """
    Eliminar un item del carrito
    """
    try:
        carrito_item = db.query(CarritoItem).filter(
            CarritoItem.id == item_id,
            CarritoItem.usuario_id == current_user.id
        ).first()
        
        if not carrito_item:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Item no encontrado en el carrito"
            )
        
        db.delete(carrito_item)
        db.commit()
        
        return {"message": "Item eliminado del carrito exitosamente"}
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al eliminar del carrito: {str(e)}"
        )

@router.delete("/limpiar")
async def limpiar_carrito(
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """
    Limpiar todo el carrito del usuario
    """
    try:
        items = db.query(CarritoItem).filter(
            CarritoItem.usuario_id == current_user.id
        ).all()
        
        for item in items:
            db.delete(item)
        
        db.commit()
        return {"message": "Carrito limpiado exitosamente"}
        
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al limpiar carrito: {str(e)}"
        ) 