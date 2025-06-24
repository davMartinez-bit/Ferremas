from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime

from app.data.database import get_db
from app.data.models.usuarios import Usuario
from app.data.models.productos import Favorito, Producto
from app.core.security import get_current_user
from app.api.schemas import FavoritoResponse, FavoritoCreate

router = APIRouter(prefix="/api/favoritos", tags=["Favoritos"])

@router.get("/", response_model=List[FavoritoResponse])
async def listar_favoritos(
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """
    Listar favoritos del usuario
    """
    try:
        favoritos = db.query(Favorito).filter(
            Favorito.usuario_id == current_user.id
        ).all()
        
        # Agregar información del producto a cada favorito
        favoritos_con_producto = []
        for favorito in favoritos:
            producto = db.query(Producto).filter(Producto.id == favorito.producto_id).first()
            if producto:
                favorito_dict = {
                    "id": favorito.id,
                    "usuario_id": favorito.usuario_id,
                    "producto_id": favorito.producto_id,
                    "fecha_agregado": favorito.fecha_agregado,
                    "producto_nombre": producto.nombre,
                    "producto_precio": producto.precio_actual,
                    "producto_imagen": producto.imagen_url if hasattr(producto, 'imagen_url') else None
                }
                favoritos_con_producto.append(favorito_dict)
        
        return favoritos_con_producto
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al listar favoritos: {str(e)}"
        )

@router.post("/toggle/{producto_id}", response_model=dict)
async def toggle_favorito(
    producto_id: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """
    Agrega o elimina un producto de la lista de favoritos.
    """
    try:
        producto = db.query(Producto).filter(Producto.id == producto_id).first()
        if not producto:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Producto no encontrado"
            )

        favorito_existente = db.query(Favorito).filter(
            Favorito.usuario_id == current_user.id,
            Favorito.producto_id == producto_id
        ).first()

        if favorito_existente:
            # Si existe, lo eliminamos
            db.delete(favorito_existente)
            db.commit()
            return {"status": "eliminado", "producto_id": producto_id}
        else:
            # Si no existe, lo creamos
            nuevo_favorito = Favorito(
                usuario_id=current_user.id,
                producto_id=producto_id,
                fecha_agregado=datetime.now()
            )
            db.add(nuevo_favorito)
            db.commit()
            return {"status": "agregado", "producto_id": producto_id}

    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al procesar favorito: {str(e)}"
        )

@router.post("/", response_model=FavoritoResponse)
async def agregar_favorito(
    favorito_data: FavoritoCreate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """
    Agregar producto a favoritos
    """
    try:
        # Verificar que el producto existe
        producto = db.query(Producto).filter(Producto.id == favorito_data.producto_id).first()
        if not producto:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Producto no encontrado"
            )
        
        # Verificar que no esté ya en favoritos
        favorito_existente = db.query(Favorito).filter(
            Favorito.usuario_id == current_user.id,
            Favorito.producto_id == favorito_data.producto_id
        ).first()
        
        if favorito_existente:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="El producto ya está en favoritos"
            )
        
        # Crear nuevo favorito
        nuevo_favorito = Favorito(
            usuario_id=current_user.id,
            producto_id=favorito_data.producto_id,
            fecha_agregado=datetime.now()
        )
        
        db.add(nuevo_favorito)
        db.commit()
        db.refresh(nuevo_favorito)
        
        return {
            "id": nuevo_favorito.id,
            "usuario_id": nuevo_favorito.usuario_id,
            "producto_id": nuevo_favorito.producto_id,
            "fecha_agregado": nuevo_favorito.fecha_agregado,
            "producto_nombre": producto.nombre,
            "producto_precio": producto.precio_actual,
            "producto_imagen": producto.imagen_url if hasattr(producto, 'imagen_url') else None
        }
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al agregar favorito: {str(e)}"
        )

@router.delete("/{producto_id}")
async def eliminar_favorito(
    producto_id: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """
    Eliminar producto de favoritos
    """
    try:
        favorito = db.query(Favorito).filter(
            Favorito.usuario_id == current_user.id,
            Favorito.producto_id == producto_id
        ).first()
        
        if not favorito:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Favorito no encontrado"
            )
        
        db.delete(favorito)
        db.commit()
        
        return {"message": "Favorito eliminado exitosamente"}
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al eliminar favorito: {str(e)}"
        ) 