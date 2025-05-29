from fastapi import APIRouter
from app.integrations.banco_central import obtener_valor_divisa

router = APIRouter()

@router.get("/{moneda}", tags=["divisas"])
def obtener_valor(moneda: str):
    moneda = moneda.lower()
    resultado = obtener_valor_divisa(moneda)
    return resultado
