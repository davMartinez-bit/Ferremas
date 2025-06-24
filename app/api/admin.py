from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from typing import List, Dict, Any
from datetime import datetime, timedelta

from app.data.database import get_db
from app.data.models.usuarios import Usuario
from app.data.models.productos import Pedido, PedidoItem, Producto, Categoria, Marca
from app.data.models.webpay import Pago
from app.core.security import get_current_user
from app.api.schemas import AdminStats, PedidoResponse, UsuarioResponse

router = APIRouter(prefix="/api/admin", tags=["Admin"])

def verificar_admin(current_user: Usuario = Depends(get_current_user)):
    """Verificar que el usuario es administrador"""
    rol = getattr(current_user.rol, 'value', current_user.rol)
    print(f"DEBUG: verificar_admin llamado")
    print(f"DEBUG: current_user = {current_user}")
    print(f"DEBUG: current_user.rol = {current_user.rol}")
    print(f"DEBUG: current_user.email = {current_user.email}")
    print(f"DEBUG: current_user.id = {current_user.id}")
    print(f"DEBUG: rol (normalizado) = {rol}")
    
    if rol not in ["admin", "vendedor"]:
        print(f"DEBUG: Rol '{rol}' no está en ['admin', 'vendedor']")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Acceso denegado. Se requieren permisos de administrador"
        )
    
    print(f"DEBUG: Usuario autorizado como admin/vendedor")
    return current_user

@router.get("/stats", response_model=AdminStats)
async def obtener_estadisticas(
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(verificar_admin)
):
    """
    Obtener estadísticas del dashboard administrativo
    """
    try:
        # Estadísticas de pedidos
        total_pedidos = db.query(Pedido).count()
        pedidos_pendientes = db.query(Pedido).filter(Pedido.estado == "pendiente").count()
        pedidos_entregados = db.query(Pedido).filter(Pedido.estado == "entregado").count()
        
        # Ventas del mes actual
        inicio_mes = datetime.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        ventas_mes = db.query(func.sum(Pedido.total)).filter(
            Pedido.fecha_creacion >= inicio_mes,
            Pedido.estado.in_(["confirmado", "enviado", "entregado"])
        ).scalar() or 0
        
        # Usuarios
        total_usuarios = db.query(Usuario).count()
        usuarios_nuevos_mes = db.query(Usuario).filter(
            Usuario.fecha_creacion >= inicio_mes
        ).count()
        
        # Productos
        total_productos = db.query(Producto).count()
        productos_bajo_stock = db.query(Producto).filter(
            Producto.stock <= Producto.stock_minimo
        ).count()
        
        # Pagos
        total_pagos = db.query(Pago).count()
        pagos_exitosos = db.query(Pago).filter(Pago.estado == "approved").count()
        
        return AdminStats(
            total_pedidos=total_pedidos,
            pedidos_pendientes=pedidos_pendientes,
            pedidos_entregados=pedidos_entregados,
            ventas_mes=float(ventas_mes),
            total_usuarios=total_usuarios,
            usuarios_nuevos_mes=usuarios_nuevos_mes,
            total_productos=total_productos,
            productos_bajo_stock=productos_bajo_stock,
            total_pagos=total_pagos,
            pagos_exitosos=pagos_exitosos
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener estadísticas: {str(e)}"
        )

@router.get("/pedidos", response_model=List[PedidoResponse])
async def listar_todos_pedidos(
    skip: int = 0,
    limit: int = 100,
    estado: str = None,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(verificar_admin)
):
    """
    Listar todos los pedidos (solo admin)
    """
    try:
        query = db.query(Pedido)
        
        if estado:
            query = query.filter(Pedido.estado == estado)
        
        pedidos = query.order_by(desc(Pedido.fecha_creacion)).offset(skip).limit(limit).all()
        return pedidos
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al listar pedidos: {str(e)}"
        )

@router.get("/usuarios", response_model=List[UsuarioResponse])
async def listar_todos_usuarios(
    skip: int = 0,
    limit: int = 100,
    rol: str = None,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(verificar_admin)
):
    """
    Listar todos los usuarios (solo admin)
    """
    try:
        query = db.query(Usuario)
        
        if rol:
            query = query.filter(Usuario.rol == rol)
        
        usuarios = query.order_by(desc(Usuario.fecha_creacion)).offset(skip).limit(limit).all()
        return usuarios
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al listar usuarios: {str(e)}"
        )

@router.get("/reportes/ventas")
async def obtener_reportes_ventas(
    fecha_inicio: str = None,
    fecha_fin: str = None,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(verificar_admin)
):
    """
    Obtener reportes de ventas
    """
    try:
        # Si no se especifican fechas, usar el mes actual
        if not fecha_inicio:
            fecha_inicio = datetime.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        else:
            fecha_inicio = datetime.fromisoformat(fecha_inicio)
            
        if not fecha_fin:
            fecha_fin = datetime.now()
        else:
            fecha_fin = datetime.fromisoformat(fecha_fin)
        
        # Ventas por día
        ventas_por_dia = db.query(
            func.date(Pedido.fecha_creacion).label('fecha'),
            func.count(Pedido.id).label('cantidad'),
            func.sum(Pedido.total).label('total')
        ).filter(
            Pedido.fecha_creacion >= fecha_inicio,
            Pedido.fecha_creacion <= fecha_fin,
            Pedido.estado.in_(["confirmado", "enviado", "entregado"])
        ).group_by(func.date(Pedido.fecha_creacion)).all()
        
        # Productos más vendidos
        productos_vendidos = db.query(
            Producto.nombre,
            func.sum(PedidoItem.cantidad).label('cantidad_vendida'),
            func.sum(PedidoItem.subtotal).label('total_vendido')
        ).join(PedidoItem, Producto.id == PedidoItem.producto_id)\
         .join(Pedido, PedidoItem.pedido_id == Pedido.id)\
         .filter(
            Pedido.fecha_creacion >= fecha_inicio,
            Pedido.fecha_creacion <= fecha_fin,
            Pedido.estado.in_(["confirmado", "enviado", "entregado"])
        ).group_by(Producto.id, Producto.nombre)\
         .order_by(desc(func.sum(PedidoItem.cantidad)))\
         .limit(10).all()
        
        return {
            "periodo": {
                "fecha_inicio": fecha_inicio.isoformat(),
                "fecha_fin": fecha_fin.isoformat()
            },
            "ventas_por_dia": [
                {
                    "fecha": str(v.fecha),
                    "cantidad": v.cantidad,
                    "total": float(v.total) if v.total else 0
                }
                for v in ventas_por_dia
            ],
            "productos_mas_vendidos": [
                {
                    "nombre": p.nombre,
                    "cantidad_vendida": p.cantidad_vendida,
                    "total_vendido": float(p.total_vendido) if p.total_vendido else 0
                }
                for p in productos_vendidos
            ]
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener reportes: {str(e)}"
        )

@router.get("/inventario")
async def obtener_estado_inventario(
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(verificar_admin)
):
    """
    Obtener estado del inventario
    """
    try:
        # Productos con bajo stock
        productos_bajo_stock = db.query(Producto).filter(
            Producto.stock <= Producto.stock_minimo
        ).all()
        
        # Productos agotados
        productos_agotados = db.query(Producto).filter(Producto.stock == 0).all()
        
        # Stock por categoría
        stock_por_categoria = db.query(
            Categoria.nombre,
            func.count(Producto.id).label('total_productos'),
            func.sum(Producto.stock).label('stock_total')
        ).join(Producto, Categoria.id == Producto.categoria_id)\
         .group_by(Categoria.id, Categoria.nombre).all()
        
        # Stock por marca
        stock_por_marca = db.query(
            Marca.nombre,
            func.count(Producto.id).label('total_productos'),
            func.sum(Producto.stock).label('stock_total')
        ).join(Producto, Marca.id == Producto.marca_id)\
         .group_by(Marca.id, Marca.nombre).all()
        
        return {
            "productos_bajo_stock": [
                {
                    "id": p.id,
                    "nombre": p.nombre,
                    "stock_actual": p.stock,
                    "stock_minimo": p.stock_minimo
                }
                for p in productos_bajo_stock
            ],
            "productos_agotados": [
                {
                    "id": p.id,
                    "nombre": p.nombre,
                    "stock_actual": p.stock
                }
                for p in productos_agotados
            ],
            "stock_por_categoria": [
                {
                    "categoria": c.nombre,
                    "total_productos": c.total_productos,
                    "stock_total": c.stock_total or 0
                }
                for c in stock_por_categoria
            ],
            "stock_por_marca": [
                {
                    "marca": m.nombre,
                    "total_productos": m.total_productos,
                    "stock_total": m.stock_total or 0
                }
                for m in stock_por_marca
            ]
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener inventario: {str(e)}"
        )

@router.put("/pedidos/{pedido_id}/estado")
async def actualizar_estado_pedido_admin(
    pedido_id: int,
    estado: str,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(verificar_admin)
):
    """
    Actualizar estado de un pedido (admin)
    """
    try:
        pedido = db.query(Pedido).filter(Pedido.id == pedido_id).first()
        
        if not pedido:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Pedido no encontrado"
            )
        
        estados_validos = ["pendiente", "confirmado", "en_proceso", "enviado", "entregado", "cancelado"]
        if estado not in estados_validos:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Estado inválido. Estados válidos: {estados_validos}"
            )
        
        pedido.estado = estado
        pedido.fecha_actualizacion = datetime.now()
        
        db.commit()
        db.refresh(pedido)
        
        return {"message": f"Estado del pedido actualizado a: {estado}"}
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al actualizar estado: {str(e)}"
        ) 