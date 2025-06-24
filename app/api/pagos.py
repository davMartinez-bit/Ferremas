# app/api/pagos.py
from fastapi import APIRouter, Depends, HTTPException, status, Request, Response
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session, joinedload
from datetime import datetime, timedelta
import uuid

from app.data.database import get_db
from app.data.models.usuarios import Usuario
from app.data.models.productos import CarritoItem, Pedido, PedidoItem
from app.data.models.webpay import Pago
from app.core.security import get_current_user, create_access_token
from app.integrations import webpay

router = APIRouter(tags=["Pagos"])

@router.post("/crear-transaccion-webpay")
async def crear_transaccion_webpay(
    request: Request,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """
    Crea una transacción en Webpay a partir del carrito del usuario.
    """
    items_carrito = db.query(CarritoItem).options(
        joinedload(CarritoItem.producto)
    ).filter(CarritoItem.usuario_id == current_user.id).all()
    
    if not items_carrito:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="El carrito está vacío")

    # Calcular subtotal (sin IVA)
    subtotal = sum(float(item.producto.precio_actual) * item.cantidad for item in items_carrito)
    
    # Calcular IVA (19%)
    iva = subtotal * 0.19
    
    # Calcular total con IVA incluido
    total = subtotal + iva
    
    print(f"DEBUG: Subtotal: ${subtotal}")
    print(f"DEBUG: IVA (19%): ${iva}")
    print(f"DEBUG: Total con IVA: ${total}")
    
    if total <= 0:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="El monto de la compra debe ser positivo")

    buy_order = f"FERR{datetime.now().strftime('%Y%m%d%H%M%S')}{current_user.id}"
    session_id = f"session-{current_user.id}"
    return_url = str(request.base_url) + f"api/pagos/retorno-webpay"
    
    response, http_status = webpay.crear_transaccion(buy_order, session_id, round(total), return_url)
    
    print(f"DEBUG: Respuesta de Webpay: {response}")
    print(f"DEBUG: Status HTTP: {http_status}")
    
    if http_status != 200 or "token" not in response:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error al iniciar pago con Webpay: {response}")

    # Verificar que la URL contenga el token
    if "url" in response and "token" in response:
        print(f"DEBUG: URL final: {response['url']}")
        print(f"DEBUG: Token: {response['token']}")
        
        # Asegurar que la URL tenga el token
        if "token=" not in response["url"]:
            response["url"] = f"{response['url']}?token={response['token']}"
            print(f"DEBUG: URL corregida: {response['url']}")

    nuevo_pago = Pago(
        token=response["token"],
        orden_id=buy_order,
        monto=float(total),  # Total con IVA incluido
        estado="PENDIENTE",
        usuario_id=current_user.id,
        return_url=return_url
    )
    db.add(nuevo_pago)
    db.commit()

    return {"url": response["url"], "token": response["token"], "total": total, "subtotal": subtotal, "iva": iva}

@router.get("/retorno-webpay", include_in_schema=False)
async def retorno_webpay(
    token_ws: str,
    db: Session = Depends(get_db)
):
    """
    Página de retorno desde Webpay. Confirma la transacción y crea el pedido.
    """
    response, http_status = webpay.confirmar_transaccion(token_ws)
    
    pago = db.query(Pago).filter(Pago.token == token_ws).first()
    if not pago:
        # Redirigir a página de error
        return RedirectResponse(url="/?pago=error&mensaje=pago_no_encontrado")
        
    usuario = db.query(Usuario).filter(Usuario.id == pago.usuario_id).first()
    if not usuario:
        return RedirectResponse(url="/?pago=error&mensaje=usuario_no_encontrado")

    if response.get("status") == "AUTHORIZED" and response.get("response_code") == 0:
        pago.estado = "APROBADO"
        pago.fecha_confirmacion = datetime.utcnow()
        db.flush() 

        nuevo_pedido = Pedido(
            numero_pedido=pago.orden_id,
            usuario_id=pago.usuario_id,
            total=float(pago.monto),  # Total con IVA incluido
            subtotal=float(pago.monto) / 1.19,  # Calcular subtotal a partir del total
            iva=float(pago.monto) - (float(pago.monto) / 1.19),  # Calcular IVA a partir del total
            estado="CONFIRMADO",
            metodo_pago="Webpay",
            email_contacto=usuario.email,
            telefono_contacto="N/A", 
            direccion_envio="N/A"
        )
        db.add(nuevo_pedido)
        db.flush()

        items_carrito = db.query(CarritoItem).options(
            joinedload(CarritoItem.producto)
        ).filter(CarritoItem.usuario_id == pago.usuario_id).all()

        for item in items_carrito:
            pedido_item = PedidoItem(
                pedido_id=nuevo_pedido.id,
                producto_id=item.producto_id,
                cantidad=item.cantidad,
                precio_unitario=item.producto.precio_actual,
                subtotal=item.producto.precio_actual * item.cantidad
            )
            db.add(pedido_item)
            item.producto.stock -= item.cantidad
            db.delete(item)
            
        pago.pedido_id = nuevo_pedido.id
        db.commit()

        # Crear token temporal para mantener la sesión
        temp_token = create_access_token(
            data={"sub": usuario.email, "user_id": usuario.id},
            expires_delta=timedelta(minutes=30)  # Token válido por 30 minutos
        )

        # Redirigir a la página principal con mensaje de éxito y token temporal
        return RedirectResponse(url=f"/?pago=exitoso&pedido_id={nuevo_pedido.id}&temp_token={temp_token}")

    else:
        pago.estado = "RECHAZADO"
        db.commit()
        return RedirectResponse(url="/?pago=rechazado")