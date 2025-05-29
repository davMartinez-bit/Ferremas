from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import os
import requests

router = APIRouter()

# Configuración Webpay
API_KEY_ID = os.getenv("WEBPAY_API_KEY_ID", "597055555532")
API_KEY_SECRET = os.getenv("WEBPAY_API_KEY_SECRET", "597055555532")
BASE_URL = "https://webpay3gint.transbank.cl"

HEADERS = {
    "Tbk-Api-Key-Id": API_KEY_ID,
    "Tbk-Api-Key-Secret": API_KEY_SECRET,
    "Content-Type": "application/json"
}

# Modelo de entrada
class TransaccionRequest(BaseModel):
    buy_order: str
    session_id: str
    amount: float
    return_url: str

@router.post("/crear_transaccion")
def crear_transaccion(data: TransaccionRequest):
    payload = data.dict()
    try:
        response = requests.post(
            f"{BASE_URL}/rswebpaytransaction/api/webpay/v1.2/transactions",
            json=payload,
            headers=HEADERS
        )
        return response.json()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al crear transacción: {str(e)}")

@router.put("/confirmar_transaccion/{token}")
def confirmar_transaccion(token: str):
    try:
        response = requests.put(
            f"{BASE_URL}/rswebpaytransaction/api/webpay/v1.2/transactions/{token}",
            headers=HEADERS
        )
        return response.json()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al confirmar transacción: {str(e)}")

@router.delete("/rechazar_transaccion/{token}")
def rechazar_transaccion(token: str):
    # Simulación de rechazo: en Webpay real no existe endpoint para rechazar
    return {
        "message": f"Transacción con token {token} marcada como rechazada (simulado)",
        "status": "rejected"
    }
@router.get("/estado_transaccion/{token}")
def estado_transaccion(token: str):
    try:
        response = requests.get(
            f"{BASE_URL}/rswebpaytransaction/api/webpay/v1.2/transactions/{token}",
            headers=HEADERS
        )
        return response.json()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al obtener estado de transacción: {str(e)}")   
    