import os
import requests

# ✅ Configuración Webpay API REST
API_KEY_ID = os.getenv("WEBPAY_API_KEY_ID", "597055555532")
API_KEY_SECRET = os.getenv("WEBPAY_API_KEY_SECRET", "579B532A7440BB0C9079DED94D31EA1615BACEB56610332264630D42D0A36B1C")
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
    
    print(f"=== DEBUG WEBPAY ===")
    print(f"URL de la API: {BASE_URL}/rswebpaytransaction/api/webpay/v1.2/transactions")
    print(f"Headers: {HEADERS}")
    print(f"Payload: {payload}")
    
    try:
        response = requests.post(
            f"{BASE_URL}/rswebpaytransaction/api/webpay/v1.2/transactions",
            json=payload,
            headers=HEADERS
        )
        
        print(f"Status Code: {response.status_code}")
        print(f"Response Headers: {dict(response.headers)}")
        print(f"Response Text: {response.text}")
        
        result = response.json()
        print(f"Response JSON: {result}")
        
        # Construir la URL correcta con el token
        if "token" in result:
            token = result["token"]
            # La URL correcta debe incluir el token como parámetro
            result["url"] = f"{BASE_URL}/webpayserver/initTransaction?token={token}"
            print(f"URL construida correctamente: {result['url']}")
        
        return result, response.status_code
    except Exception as e:
        print(f"Error en crear_transaccion: {e}")
        return {"error": str(e)}, 500

def confirmar_transaccion(token: str):
    try:
        response = requests.put(
            f"{BASE_URL}/rswebpaytransaction/api/webpay/v1.2/transactions/{token}",
            headers=HEADERS
        )
        return response.json(), response.status_code
    except Exception as e:
        return {"error": f"Error al confirmar transacción: {str(e)}"}, 500
