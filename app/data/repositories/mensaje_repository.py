from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any

from app.data.models import Mensaje

class MensajeRepository:
    def __init__(self, db: Session):
        self.db = db
    
    def create(self, mensaje_data: Dict[str, Any]) -> Mensaje:
        """Crea un nuevo mensaje de contacto."""
        nuevo_mensaje = Mensaje(**mensaje_data)
        self.db.add(nuevo_mensaje)
        self.db.flush()
        return nuevo_mensaje
    
    def get_all(self, vendedor_id: Optional[int] = None, only_unread: bool = False) -> List[Mensaje]:
        """Obtiene mensajes, opcionalmente filtrados por vendedor y/o no leídos."""
        query = self.db.query(Mensaje)
        
        if vendedor_id is not None:
            query = query.filter(Mensaje.vendedor_id == vendedor_id)
            
        if only_unread:
            query = query.filter(~Mensaje.leido)
            
        return query.order_by(Mensaje.fecha.desc()).all()
    
    def get_by_id(self, mensaje_id: int) -> Optional[Mensaje]:
        """Obtiene un mensaje por su ID."""
        return self.db.query(Mensaje).filter(Mensaje.id == mensaje_id).first()
    
    def mark_as_read(self, mensaje_id: int) -> bool:
        """Marca un mensaje como leído."""
        mensaje = self.get_by_id(mensaje_id)
        if not mensaje:
            return False
            
        mensaje.leido = True
        self.db.flush()
        return True
    
    def delete(self, mensaje_id: int) -> bool:
        """Elimina un mensaje."""
        mensaje = self.get_by_id(mensaje_id)
        if not mensaje:
            return False
            
        self.db.delete(mensaje)
        self.db.flush()
        return True