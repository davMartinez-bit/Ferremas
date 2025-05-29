from sqlalchemy.orm import Session
from sqlalchemy import desc
from typing import List, Optional, Dict, Any

from app.data.models import Pago

class PagoRepository:
    def __init__(self, db: Session):
        self.db = db
    
    def create(self, pago_data: Dict[str, Any]) -> Pago:
        """Crea un nuevo registro de pago."""
        nuevo_pago = Pago(**pago_data)
        self.db.add(nuevo_pago)
        self.db.flush()
        return nuevo_pago
    
    def get_by_token(self, token: str) -> Optional[Pago]:
        """Obtiene un pago por su token."""
        return self.db.query(Pago).filter(Pago.token == token).first()
    
    def get_by_orden_id(self, orden_id: str) -> Optional[Pago]:
        """Obtiene un pago por su ID de orden."""
        return self.db.query(Pago).filter(Pago.orden_id == orden_id).first()
    
    def update_estado(self, token: str, nuevo_estado: str) -> Optional[Pago]:
        """Actualiza el estado de un pago existente."""
        pago = self.get_by_token(token)
        if not pago:
            return None
            
        pago.estado = nuevo_estado
        self.db.flush()
        return pago
    
    def get_recent_pagos(self, limit: int = 10) -> List[Pago]:
        """Obtiene los pagos más recientes."""
        return self.db.query(Pago).order_by(desc(Pago.fecha_creacion)).limit(limit).all()