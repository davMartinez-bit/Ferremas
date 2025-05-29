from typing import Dict, Any, Optional
from sqlalchemy.orm import Session

from app.integrations.banco_central import BancoCentralIntegration

class DivisaService:
    def __init__(self, db: Session):
        self.db = db
        self.bc_api = BancoCentralIntegration()

    def obtener_tasa_cambio(self, moneda: str) -> Dict[str, Any]:
        """Obtiene la tasa de cambio actual desde el Banco Central."""
        try:
            tasa = self.bc_api.obtener_tasa(moneda)
            if tasa is None:
                return {"error": f"No se encontró tasa para la moneda '{moneda}'"}
            return {
                "moneda": moneda.upper(),
                "tasa": tasa
            }
        except Exception as e:
            return {"error": str(e)}

    def convertir_a_clp(self, moneda: str, monto: float) -> Dict[str, Any]:
        """Convierte un monto en otra divisa a pesos chilenos."""
        try:
            tasa = self.bc_api.obtener_tasa(moneda)
            if tasa is None:
                return {"error": f"No se pudo obtener tasa de cambio para '{moneda}'"}
            valor_en_clp = monto * tasa
            return {
                "moneda_origen": moneda.upper(),
                "monto_original": monto,
                "tasa_cambio": tasa,
                "monto_en_clp": round(valor_en_clp, 2)
            }
        except Exception as e:
            return {"error": str(e)}
