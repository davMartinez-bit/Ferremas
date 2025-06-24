# app/integrations/banco_central.py
import bcchapi
from datetime import datetime
import pandas as pd
from typing import Literal

from pathlib import Path

# Ruta al archivo de credenciales
CREDENTIALS_FILE = Path(__file__).parent.parent.parent / "banco_central_credentials.txt"

# Instanciar el cliente Siete
siete = bcchapi.Siete(file=str(CREDENTIALS_FILE))

# Códigos comunes de divisas: EUR = Euro, USD = Dólar, etc.
CURRENCY_CODES = {
    "usd": "F073.TCO.PRE.Z.D",  # Tipo de cambio observado dólar
    "eur": "F072.CLP.EUR.N.O.D",  # Euro observado en pesos CLP
}


def obtener_valor_divisa(moneda: Literal["usd", "eur"], fecha: str = None) -> dict:
    if moneda not in CURRENCY_CODES:
        return {"error": "Moneda no soportada"}

    codigo = CURRENCY_CODES[moneda]
    if fecha is None:
        fecha = datetime.now().strftime("%Y-%m-%d")

    try:
        # Usar el método cuadro para obtener datos
        df = siete.cuadro(codigo, desde=fecha, hasta=fecha)
        if df.empty:
            return {"error": f"No hay datos disponibles para {moneda} en {fecha}"}
        
        # El valor está en la primera fila, columna 'valor' o similar
        valor = df.iloc[0].iloc[-1]  # Última columna (valor)
        return {
            "moneda": moneda.upper(),
            "fecha": fecha,
            "valor_clp": float(valor)
        }
    except Exception as e:
        return {"error": str(e)}

def obtener_todas_las_divisas(fecha: str = None) -> list:
    if fecha is None:
        fecha = datetime.now().strftime("%Y-%m-%d")

    resultados = []
    for moneda, codigo in CURRENCY_CODES.items():
        try:
            # Usar el método cuadro para obtener datos
            df = siete.cuadro(codigo, desde=fecha, hasta=fecha)
            if df.empty:
                resultados.append({
                    "moneda": moneda.upper(),
                    "codigo": codigo,
                    "fecha": fecha,
                    "error": f"No hay datos disponibles para {moneda} en {fecha}"
                })
            else:
                valor = df.iloc[0].iloc[-1]  # Última columna (valor)
                resultados.append({
                    "moneda": moneda.upper(),
                    "codigo": codigo,
                    "fecha": fecha,
                    "valor_clp": float(valor)
                })
        except Exception as e:
            resultados.append({
                "moneda": moneda.upper(),
                "codigo": codigo,
                "fecha": fecha,
                "error": str(e)
            })
    return resultados
