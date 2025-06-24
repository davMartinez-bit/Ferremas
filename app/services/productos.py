from sqlalchemy.orm import Session, joinedload
from sqlalchemy import and_, or_, func, desc, asc
from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta
import math

from app.data.models import Producto, Categoria, Marca, PrecioHistorico
from app.api.schemas import (
    ProductoCreate, ProductoUpdate, ProductoResponse, ProductoBasic,
    CategoriaResponse, MarcaResponse, HistorialPreciosResponse,
    ProductoSearch, EstadisticasGenerales, FiltrosProducto,
    CategoriaCompleteResponse, SubcategoriaResponse
)

class ProductoService:
    def __init__(self, db: Session):
        self.db = db

    def get_producto_by_codigo(self, codigo: str) -> Dict[str, Any]:
        """Obtiene un producto por su código"""
        try:
            producto = self.db.query(Producto).options(
                joinedload(Producto.categoria),
                joinedload(Producto.marca),
                joinedload(Producto.precios)
            ).filter(Producto.codigo == codigo).first()

            if not producto:
                return {"error": f"Producto con código '{codigo}' no encontrado"}

            # Calcular información adicional
            dias_desde_creacion = (datetime.utcnow() - producto.fecha_creacion).days
            stock_bajo = producto.stock <= producto.stock_minimo

            response_data = {
                "id": producto.id,
                "codigo": producto.codigo,
                "nombre": producto.nombre,
                "descripcion": producto.descripcion,
                "stock": producto.stock,
                "stock_minimo": producto.stock_minimo,
                "unidad_medida": producto.unidad_medida,
                "activo": producto.activo,
                "destacado": producto.destacado,
                "en_promocion": producto.en_promocion,
                "peso": float(producto.peso) if producto.peso else None,
                "dimensiones": producto.dimensiones,
                "color": producto.color,
                "modelo": producto.modelo,
                "categoria_id": producto.categoria_id,
                "marca_id": producto.marca_id,
                "fecha_creacion": producto.fecha_creacion,
                "fecha_actualizacion": producto.fecha_actualizacion,
                "precio_actual": producto.precio_actual,
                "stock_bajo": stock_bajo,
                "dias_desde_creacion": dias_desde_creacion,
                "categoria": {
                    "id": producto.categoria.id,
                    "nombre": producto.categoria.nombre,
                    "codigo": producto.categoria.codigo,
                    "padre_id": producto.categoria.padre_id
                } if producto.categoria else None,
                "marca": {
                    "id": producto.marca.id,
                    "nombre": producto.marca.nombre,
                    "codigo": producto.marca.codigo
                } if producto.marca else None
            }

            return response_data

        except Exception as e:
            return {"error": f"Error obteniendo producto: {str(e)}"}

    def search_productos_by_name(self, nombre: str, pagina: int = 1, por_pagina: int = 20) -> List[Dict[str, Any]]:
        """Busca productos por nombre (búsqueda parcial)"""
        try:
            query = self.db.query(Producto).options(
                joinedload(Producto.categoria),
                joinedload(Producto.marca)
            ).filter(
                and_(
                    Producto.nombre.contains(nombre),
                    Producto.activo == True
                )
            )

            # Calcular paginación
            total = query.count()
            productos = query.offset((pagina - 1) * por_pagina).limit(por_pagina).all()

            return self._format_productos_basicos(productos)

        except Exception as e:
            return {"error": f"Error buscando productos: {str(e)}"}

    def get_productos_by_categoria(self, categoria_codigo: str, incluir_subcategorias: bool = True) -> List[Dict[str, Any]]:
        """Obtiene productos de una categoría específica"""
        try:
            categoria = self.db.query(Categoria).filter(Categoria.codigo == categoria_codigo).first()
            if not categoria:
                return {"error": f"Categoría '{categoria_codigo}' no encontrada"}

            category_ids = [categoria.id]
            
            if incluir_subcategorias:
                # Obtener todas las subcategorías recursivamente
                subcategorias = self._get_subcategorias_recursivo(categoria.id)
                category_ids.extend(subcategorias)

            productos = self.db.query(Producto).options(
                joinedload(Producto.categoria),
                joinedload(Producto.marca)
            ).filter(
                and_(
                    Producto.categoria_id.in_(category_ids),
                    Producto.activo == True
                )
            ).all()

            return self._format_productos_basicos(productos)

        except Exception as e:
            return {"error": f"Error obteniendo productos por categoría: {str(e)}"}

    def get_productos_by_stock(self, stock_max: int) -> List[Dict[str, Any]]:
        """Obtiene productos con stock menor o igual al especificado"""
        try:
            productos = self.db.query(Producto).options(
                joinedload(Producto.categoria),
                joinedload(Producto.marca)
            ).filter(
                and_(
                    Producto.stock <= stock_max,
                    Producto.activo == True
                )
            ).order_by(asc(Producto.stock)).all()

            return self._format_productos_basicos(productos)

        except Exception as e:
            return {"error": f"Error obteniendo productos por stock: {str(e)}"}

    def get_all_productos(self, pagina: int = 1, por_pagina: int = 50) -> List[Dict[str, Any]]:
        """Obtiene todos los productos activos"""
        try:
            productos = self.db.query(Producto).options(
                joinedload(Producto.categoria),
                joinedload(Producto.marca)
            ).filter(
                Producto.activo == True
            ).order_by(asc(Producto.nombre)).all()

            return self._format_productos_basicos(productos)

        except Exception as e:
            return {"error": f"Error obteniendo todos los productos: {str(e)}"}

    def buscar_productos_avanzado(self, filtros: FiltrosProducto, pagina: int = 1, por_pagina: int = 20) -> Dict[str, Any]:
        """Búsqueda avanzada de productos con múltiples filtros"""
        try:
            query = self.db.query(Producto).options(
                joinedload(Producto.categoria),
                joinedload(Producto.marca),
                joinedload(Producto.precios)
            )

            # Construir filtros dinámicamente
            conditions = []

            if filtros.solo_activos:
                conditions.append(Producto.activo == True)

            if filtros.nombre:
                conditions.append(Producto.nombre.contains(filtros.nombre))

            if filtros.categoria_id:
                # Incluir subcategorías
                categoria_ids = [filtros.categoria_id]
                subcategorias = self._get_subcategorias_recursivo(filtros.categoria_id)
                categoria_ids.extend(subcategorias)
                conditions.append(Producto.categoria_id.in_(categoria_ids))

            if filtros.marca_id:
                conditions.append(Producto.marca_id == filtros.marca_id)

            if filtros.stock_min is not None:
                conditions.append(Producto.stock >= filtros.stock_min)

            if filtros.stock_max is not None:
                conditions.append(Producto.stock <= filtros.stock_max)

            if filtros.solo_destacados:
                conditions.append(Producto.destacado == True)

            if filtros.solo_promociones:
                conditions.append(Producto.en_promocion == True)

            if filtros.stock_bajo:
                conditions.append(Producto.stock <= Producto.stock_minimo)

            # Aplicar filtros
            if conditions:
                query = query.filter(and_(*conditions))

            # Filtros de precio (requieren subconsulta)
            if filtros.precio_min or filtros.precio_max:
                subquery = self.db.query(
                    PrecioHistorico.producto_id,
                    func.max(PrecioHistorico.fecha).label('max_fecha')
                ).group_by(PrecioHistorico.producto_id).subquery()

                precio_query = self.db.query(PrecioHistorico).join(
                    subquery,
                    and_(
                        PrecioHistorico.producto_id == subquery.c.producto_id,
                        PrecioHistorico.fecha == subquery.c.max_fecha
                    )
                )

                if filtros.precio_min:
                    precio_query = precio_query.filter(PrecioHistorico.valor >= filtros.precio_min)
                if filtros.precio_max:
                    precio_query = precio_query.filter(PrecioHistorico.valor <= filtros.precio_max)

                productos_con_precio_filtrado = [p.producto_id for p in precio_query.all()]
                query = query.filter(Producto.id.in_(productos_con_precio_filtrado))

            # Ordenar por relevancia
            query = query.order_by(desc(Producto.destacado), desc(Producto.en_promocion), Producto.nombre)

            # Paginación
            total = query.count()
            total_paginas = math.ceil(total / por_pagina)
            productos = query.offset((pagina - 1) * por_pagina).limit(por_pagina).all()

            return {
                "productos": self._format_productos_basicos(productos),
                "total": total,
                "pagina": pagina,
                "total_paginas": total_paginas,
                "productos_por_pagina": por_pagina
            }

        except Exception as e:
            return {"error": f"Error en búsqueda avanzada: {str(e)}"}

    def get_historial_precios(self, codigo: str, fecha_desde: Optional[str] = None) -> Dict[str, Any]:
        """Obtiene el historial de precios de un producto"""
        try:
            producto = self.db.query(Producto).filter(Producto.codigo == codigo).first()
            if not producto:
                return {"error": f"Producto con código '{codigo}' no encontrado"}

            query = self.db.query(PrecioHistorico).filter(PrecioHistorico.producto_id == producto.id)

            if fecha_desde:
                try:
                    fecha_filtro = datetime.fromisoformat(fecha_desde.replace('Z', '+00:00'))
                    query = query.filter(PrecioHistorico.fecha >= fecha_filtro)
                except ValueError:
                    return {"error": "Formato de fecha inválido. Use formato ISO (YYYY-MM-DD)"}

            precios = query.order_by(desc(PrecioHistorico.fecha)).all()

            if not precios:
                return {
                    "producto_codigo": codigo,
                    "producto_nombre": producto.nombre,
                    "precios": [],
                    "precio_actual": None
                }   
            precio_actual = precios[0].valor if precios else None
            historial = [
                {
                    "valor": float(p.valor),
                    "fecha": p.fecha.isoformat(),
                    "usuario_id": p.usuario_id,
                    "motivo": p.motivo
                } for p in precios
            ]       
            return {
                "producto_codigo": codigo,
                "producto_nombre": producto.nombre,
                "precio_actual": float(precio_actual) if precio_actual else None,
                "precios": historial
            }
        except Exception as e:
            return {"error": f"Error obteniendo historial de precios: {str(e)}"}        
    
    def _format_productos_basicos(self, productos: List[Producto]) -> List[Dict[str, Any]]:
        """Formatea una lista de productos en formato básico para respuestas de API"""
        formatted_products = []
        
        for producto in productos:
            formatted_product = {
                "id": producto.id,
                "codigo": producto.codigo,
                "nombre": producto.nombre,
                "descripcion": producto.descripcion,
                "stock": producto.stock,
                "stock_minimo": producto.stock_minimo,
                "unidad_medida": producto.unidad_medida,
                "activo": producto.activo,
                "destacado": producto.destacado,
                "en_promocion": producto.en_promocion,
                "peso": float(producto.peso) if producto.peso else None,
                "dimensiones": producto.dimensiones,
                "color": producto.color,
                "modelo": producto.modelo,
                "categoria_id": producto.categoria_id,
                "marca_id": producto.marca_id,
                "fecha_creacion": producto.fecha_creacion,
                "fecha_actualizacion": producto.fecha_actualizacion,
                "precio_actual": producto.precio_actual,
                "categoria": {
                    "id": producto.categoria.id,
                    "nombre": producto.categoria.nombre,
                    "descripcion": producto.categoria.descripcion
                } if producto.categoria else None,
                "marca": {
                    "id": producto.marca.id,
                    "nombre": producto.marca.nombre,
                    "codigo": producto.marca.codigo
                } if producto.marca else None
            }
            formatted_products.append(formatted_product)
        
        return formatted_products
    
    def _get_subcategorias_recursivo(self, categoria_id: int) -> List[int]:
        """Obtiene todas las subcategorías de una categoría de forma recursiva"""
        subcategorias = []
        hijos = self.db.query(Categoria).filter(Categoria.padre_id == categoria_id).all()
        
        for hijo in hijos:
            subcategorias.append(hijo.id)
            subcategorias.extend(self._get_subcategorias_recursivo(hijo.id))
        
        return subcategorias        

    def get_categorias(self) -> List[Dict[str, Any]]:
        """Devuelve todas las categorías en formato jerárquico"""
        try:
            # Obtener todas las categorías
            categorias = self.db.query(Categoria).all()
            
            if not categorias:
                return []
            
            categorias_dict = {c.id: c for c in categorias}

            # Construir árbol de subcategorías
            def build_subcategorias(parent_id):
                subcats = [c for c in categorias if c.padre_id == parent_id]
                return [
                    SubcategoriaResponse(
                        id=sc.id,
                        nombre=sc.nombre,
                        descripcion=sc.descripcion,
                        subcategorias=build_subcategorias(sc.id)
                    ) for sc in subcats
                ]

            # Categorías raíz (sin padre)
            categorias_raiz = [c for c in categorias if c.padre_id is None]
            
            resultado = []
            for cat in categorias_raiz:
                resultado.append(
                    CategoriaCompleteResponse(
                        id=cat.id,
                        nombre=cat.nombre,
                        descripcion=cat.descripcion,
                        subcategorias=build_subcategorias(cat.id)
                    )
                )
            
            return resultado
            
        except Exception as e:
            return []  # Devolver lista vacía en lugar de diccionario con error

    def get_marcas(self) -> List[Dict[str, Any]]:
        """Devuelve todas las marcas disponibles"""
        try:
            marcas = self.db.query(Marca).all()
            return [
                {
                    "id": m.id,
                    "nombre": m.nombre,
                    "codigo": m.codigo
                } for m in marcas
            ]
        except Exception as e:
            return {"error": f"Error obteniendo marcas: {str(e)}"}

    def get_productos_destacados(self) -> List[Dict[str, Any]]:
        """Devuelve productos destacados (dummy/simple para evitar error 500)"""
        try:
            productos = self.db.query(Producto).filter(Producto.destacado == True).all()
            return self._format_productos_basicos(productos)
        except Exception as e:
            return {"error": f"Error obteniendo productos destacados: {str(e)}"}

    def get_productos_en_promocion(self) -> List[Dict[str, Any]]:
        """Devuelve productos en promoción (dummy/simple para evitar error 500)"""
        try:
            productos = self.db.query(Producto).filter(Producto.en_promocion == True).all()
            return self._format_productos_basicos(productos)
        except Exception as e:
            return {"error": f"Error obteniendo productos en promoción: {str(e)}"}

    def get_productos_lanzamiento(self, dias: int = 30) -> List[Dict[str, Any]]:
        """Devuelve productos lanzados recientemente (dummy/simple para evitar error 500)"""
        try:
            desde = datetime.utcnow() - timedelta(days=dias)
            productos = self.db.query(Producto).filter(Producto.fecha_creacion >= desde).all()
            return self._format_productos_basicos(productos)
        except Exception as e:
            return {"error": f"Error obteniendo productos de lanzamiento: {str(e)}"}

    def create_producto(self, data: dict) -> dict:
        """Crea un nuevo producto en la base de datos"""
        try:
            # Validar que el código no exista
            if self.db.query(Producto).filter(Producto.codigo == data["codigo"]).first():
                return {"error": f"Ya existe un producto con el código '{data['codigo']}'"}
            
            # Extraer el precio del data
            precio_inicial = data.pop("precio_actual", 0)
            
            producto = Producto(
                codigo=data["codigo"],
                nombre=data["nombre"],
                descripcion=data.get("descripcion", ""),
                stock=data.get("stock", 0),
                stock_minimo=data.get("stock_minimo", 0),
                categoria_id=data.get("categoria_id"),
                marca_id=data.get("marca_id"),
                unidad_medida=data.get("unidad_medida", "unidad"),
                destacado=data.get("destacado", False),
                en_promocion=data.get("en_promocion", False),
                peso=data.get("peso"),
                fecha_creacion=datetime.utcnow(),
                fecha_actualizacion=datetime.utcnow(),
                activo=True
            )
            self.db.add(producto)
            self.db.commit()
            self.db.refresh(producto)
            
            # Crear el precio histórico inicial
            if precio_inicial > 0:
                precio_historico = PrecioHistorico(
                    producto_id=producto.id,
                    valor=precio_inicial,
                    fecha=datetime.utcnow(),
                    motivo="Precio inicial"
                )
                self.db.add(precio_historico)
                self.db.commit()
            
            return self.get_producto_by_codigo(producto.codigo)
        except Exception as e:
            self.db.rollback()
            return {"error": f"Error creando producto: {str(e)}"}

    def update_producto(self, codigo: str, data: dict) -> dict:
        """Actualiza un producto existente"""
        try:
            producto = self.db.query(Producto).filter(Producto.codigo == codigo).first()
            if not producto:
                return {"error": f"Producto con código '{codigo}' no encontrado"}
            
            # Manejar actualización de precio por separado
            nuevo_precio = data.pop("precio_actual", None)
            
            # Actualizar campos del producto
            for key, value in data.items():
                if hasattr(producto, key):
                    setattr(producto, key, value)
            
            producto.fecha_actualizacion = datetime.utcnow()
            self.db.commit()
            
            # Si hay nuevo precio, crear registro en historial
            if nuevo_precio is not None:
                precio_historico = PrecioHistorico(
                    producto_id=producto.id,
                    valor=nuevo_precio,
                    fecha=datetime.utcnow(),
                    motivo="Actualización de precio"
                )
                self.db.add(precio_historico)
                self.db.commit()
            
            self.db.refresh(producto)
            return self.get_producto_by_codigo(producto.codigo)
        except Exception as e:
            self.db.rollback()
            return {"error": f"Error actualizando producto: {str(e)}"}

    def delete_producto(self, codigo: str) -> dict:
        """Elimina un producto por su código"""
        try:
            producto = self.db.query(Producto).filter(Producto.codigo == codigo).first()
            if not producto:
                return {"error": f"Producto con código '{codigo}' no encontrado"}
            self.db.delete(producto)
            self.db.commit()
            return {"message": f"Producto '{codigo}' eliminado correctamente"}
        except Exception as e:
            self.db.rollback()
            return {"error": f"Error eliminando producto: {str(e)}"}        