# app/api/pagos.py
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.integrations.webpay import crear_transaccion, confirmar_transaccion

router = APIRouter()

SECRET_KEY = "h3n1234sdfg1234h3n1234sdfg1234h3n1234sdfg1234"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

class TransaccionRequest(BaseModel):
    buy_order: str
    session_id: str
    amount: float
    return_url: str

@router.post("/webpay/iniciar")
def iniciar_pago(data: TransaccionRequest):
    resultado, status = crear_transaccion(data.buy_order, data.session_id, data.amount, data.return_url)
    if status != 200:
        raise HTTPException(status_code=status, detail=resultado)
    return resultado

@router.get("/webpay/confirmar/{token}")
def confirmar_pago(token: str):
    resultado, status = confirmar_transaccion(token)
    if status != 200:
        raise HTTPException(status_code=status, detail=resultado)
    return resultado
@router.get("/webpay/estado/{token}")
def estado_pago(token: str):
    resultado, status = confirmar_transaccion(token)
    if status != 200:
        raise HTTPException(status_code=status, detail=resultado)
    return resultado