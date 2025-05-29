from sqlalchemy.orm import Session
from sqlalchemy import desc, func
from typing import List, Optional, Dict, Any

from app.data.models import Producto, PrecioHistorico, Categoria, Marca

class ProductoRepository:
    def __init__(self, db: Session):
        self.db = db
    
    def get_by_codigo(self, codigo: str) -> Optional[Producto]:
        """Obtiene un producto por su código único."""
        return self.db.query(Producto).filter(Producto.codigo == codigo, Producto.activo).first()
    
    def search_by_name(self, name_partial: str) -> List[Producto]:
        """Busca productos que contengan el texto parcial en su nombre."""
        return self.db.query(Producto).filter(
            Producto.nombre.ilike(f"%{name_partial}%"),
            Producto.activo
        ).all()
    
    def get_by_categoria(self, categoria_nombre: str) -> List[Producto]:
        """Obtiene productos por nombre de categoría."""
        return self.db.query(Producto).join(Categoria).filter(
            func.lower(Categoria.nombre) == func.lower(categoria_nombre),
            Producto.activo
        ).all()
    
    def get_by_stock_criteria(self, max_stock: Optional[int] = None) -> List[Producto]:
        """Obtiene productos con criterio de stock."""
        query = self.db.query(Producto).filter(Producto.activo)
        
        if max_stock is not None:
            query = query.filter(Producto.stock <= max_stock)
            
        return query.order_by(Producto.stock).all()
    
    def get_precio_by_fecha(self, producto_id: int, fecha: Optional[str] = None) -> List[PrecioHistorico]:
        """Obtiene el historial de precios de un producto, opcionalmente filtrado por fecha."""
        query = self.db.query(PrecioHistorico).filter(PrecioHistorico.producto_id == producto_id)
        
        if fecha:
            query = query.filter(func.date(PrecioHistorico.fecha) == fecha)
            
        return query.order_by(desc(PrecioHistorico.fecha)).all()
    
    def get_producto_detalle(self, codigo: str) -> Dict[str, Any]:
        """Obtiene un diccionario con los detalles completos del producto."""
        producto = self.get_by_codigo(codigo)
        if not producto:
            return None
        
        precios_historicos = self.get_precio_by_fecha(producto.id)
        precios_formateados = [
            {
                "Fecha": precio.fecha.isoformat(),
                "Valor": precio.valor
            } for precio in precios_historicos
        ]
        
        return {
            "Código del producto": producto.codigo,
            "Marca": producto.marca.nombre if producto.marca else None,
            "Código de Marca": producto.marca.codigo if producto.marca else None,
            "Nombre": producto.nombre,
            "Descripción": producto.descripcion,
            "Stock": producto.stock,
            "Categoría": producto.categoria.nombre if producto.categoria else None,
            "Precio": precios_formateados
        }
    
    def create(self, producto_data: Dict[str, Any]) -> Producto:
        """Crea un nuevo producto con su precio inicial."""
        # Obtener o crear marca si es necesario
        marca = None
        if "marca_id" in producto_data:
            marca_id = producto_data.pop("marca_id")
            marca = self.db.query(Marca).get(marca_id)
        elif "marca_nombre" in producto_data and "marca_codigo" in producto_data:
            marca_nombre = producto_data.pop("marca_nombre")
            marca_codigo = producto_data.pop("marca_codigo")
            
            marca = self.db.query(Marca).filter(Marca.codigo == marca_codigo).first()
            if not marca:
                marca = Marca(nombre=marca_nombre, codigo=marca_codigo)
                self.db.add(marca)
                self.db.flush()
        
        # Obtener o crear categoría si es necesario
        categoria = None
        if "categoria_id" in producto_data:
            categoria_id = producto_data.pop("categoria_id")
            categoria = self.db.query(Categoria).get(categoria_id)
        elif "categoria_nombre" in producto_data:
            categoria_nombre = producto_data.pop("categoria_nombre")
            
            categoria = self.db.query(Categoria).filter(
                func.lower(Categoria.nombre) == func.lower(categoria_nombre)
            ).first()
            
            if not categoria:
                categoria = Categoria(nombre=categoria_nombre)
                self.db.add(categoria)
                self.db.flush()
                
        # Extraer precio inicial si existe
        precio_inicial = None
        if "precio" in producto_data:
            precio_inicial = producto_data.pop("precio")
        
        # Crear producto
        nuevo_producto = Producto(
            **producto_data,
            marca_id=marca.id if marca else None,
            categoria_id=categoria.id if categoria else None
        )
        
        self.db.add(nuevo_producto)
        self.db.flush()
        
        # Agregar precio inicial si existe
        if precio_inicial is not None:
            precio = PrecioHistorico(
                producto_id=nuevo_producto.id,
                valor=precio_inicial
            )
            self.db.add(precio)
            self.db.flush()
        
        return nuevo_producto
    
    def update(self, codigo: str, producto_data: Dict[str, Any]) -> Optional[Producto]:
        """Actualiza un producto existente."""
        producto = self.get_by_codigo(codigo)
        if not producto:
            return None
            
        # Extraer precio si existe
        nuevo_precio = None
        if "precio" in producto_data:
            nuevo_precio = producto_data.pop("precio")
            
        # Actualizar propiedades del producto
        for key, value in producto_data.items():
            if hasattr(producto, key):
                setattr(producto, key, value)
                
        # Agregar nuevo precio al historial si existe
        if nuevo_precio is not None:
            precio = PrecioHistorico(
                producto_id=producto.id,
                valor=nuevo_precio
            )
            self.db.add(precio)
            
        self.db.flush()
        return producto
    
    def delete(self, codigo: str) -> bool:
        """Elimina lógicamente un producto (lo marca como inactivo)."""
        producto = self.get_by_codigo(codigo)
        if not producto:
            return False
            
        producto.activo = False
        self.db.flush()
        return True