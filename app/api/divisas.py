from fastapi import APIRouter, Query
from app.integrations.banco_central import obtener_valor_divisa, obtener_todas_las_divisas
from typing import Optional

router = APIRouter()

@router.get("/{moneda}", tags=["divisas"])
def obtener_valor(moneda: str):
    moneda = moneda.lower()
    resultado = obtener_valor_divisa(moneda)
    return resultado

@router.get("/", tags=["divisas"])
def obtener_todas_divisas():
    """Obtiene todas las divisas disponibles con sus valores actuales"""
    return obtener_todas_las_divisas()

@router.get("/convertir/{moneda}", tags=["divisas"])
def convertir_divisa(
    moneda: str,
    monto: float = Query(..., description="Monto a convertir"),
    fecha: Optional[str] = Query(None, description="Fecha para la conversión (YYYY-MM-DD)")
):
    """Convierte un monto de CLP a la moneda especificada"""
    moneda = moneda.lower()
    resultado = obtener_valor_divisa(moneda, fecha)
    
    if "error" in resultado:
        return resultado
    
    valor_en_clp = resultado["valor_clp"]
    valor_convertido = monto / valor_en_clp
    
    return {
        "moneda_origen": "CLP",
        "moneda_destino": moneda.upper(),
        "monto_original": monto,
        "tasa_cambio": valor_en_clp,
        "monto_convertido": round(valor_convertido, 2),
        "fecha": resultado["fecha"]
    }
