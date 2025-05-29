import os
import requests

# ✅ Configuración Webpay API REST
API_KEY_ID = os.getenv("WEBPAY_API_KEY_ID", "597055555532")
API_KEY_SECRET = os.getenv("WEBPAY_API_KEY_SECRET", "597055555532")
BASE_URL = "https://webpay3gint.transbank.cl"

HEADERS = {
    "Tbk-Api-Key-Id": API_KEY_ID,
    "Tbk-Api-Key-Secret": API_KEY_SECRET,
    "Content-Type": "application/json"
}

def crear_transaccion(buy_order: str, session_id: str, amount: float, return_url: str):
    payload = {
        "buy_order": buy_order,
        "session_id": session_id,
        "amount": amount,
        "return_url": return_url
    }
    try:
        response = requests.post(
            f"{BASE_URL}/rswebpaytransaction/api/webpay/v1.2/transactions",
            json=payload,
            headers=HEADERS
        )
        return response.json(), response.status_code
    except Exception as e:
        return {"error": f"Error en la conexión con Webpay: {str(e)}"}, 500

def confirmar_transaccion(token: str):
    try:
        response = requests.put(
            f"{BASE_URL}/rswebpaytransaction/api/webpay/v1.2/transactions/{token}",
            headers=HEADERS
        )
        return response.json(), response.status_code
    except Exception as e:
        return {"error": f"Error al confirmar transacción: {str(e)}"}, 500
