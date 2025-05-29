from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional, List, Dict
from pydantic import BaseModel, Field



from app.data.database import get_db
from app.services.productos import ProductoService  # Asegúrate de que la ruta sea correcta

router = APIRouter()

# -----------------------------
# Pydantic Schemas (validador)
# -----------------------------
class ProductoCreate(BaseModel):
    codigo: str = Field(..., example="PROD-001")
    nombre: str
    descripcion: Optional[str] = ""
    stock: int = 0
    categoria_id: Optional[int]
    marca_id: Optional[int]
    unidad_medida: Optional[str] = "unidad"
    destacado: Optional[bool] = False
    en_promocion: Optional[bool] = False
    peso: Optional[float] = None
    precio_actual: float = Field(..., gt=0, example=9900.0)


class ProductoUpdate(BaseModel):
    nombre: Optional[str]
    descripcion: Optional[str]
    stock: Optional[int]
    categoria_id: Optional[int]
    marca_id: Optional[int]
    unidad_medida: Optional[str]
    destacado: Optional[bool]
    en_promocion: Optional[bool]
    peso: Optional[float]
    precio_actual: Optional[float]


# -----------------------------
# Endpoints
# -----------------------------

@router.get("/productos/", summary="Listar productos por nombre", tags=["productos"])
def buscar_productos(nombre: Optional[str] = Query(None), db: Session = Depends(get_db)):
    service = ProductoService(db)
    if nombre:
        return service.search_productos_by_name(nombre)
    return service.get_productos_destacados()


@router.get("/productos/categoria/", summary="Buscar productos por categoría", tags=["productos"])
def productos_por_categoria(categoria: str, db: Session = Depends(get_db)):
    service = ProductoService(db)
    return service.get_productos_by_categoria(categoria)


@router.get("/productos/stock/", summary="Buscar productos con bajo stock", tags=["productos"])
def productos_por_stock(stock_max: int = 10, db: Session = Depends(get_db)):
    service = ProductoService(db)
    return service.get_productos_by_stock(stock_max)


@router.get("/productos/{codigo}", summary="Obtener detalle de producto", tags=["productos"])
def obtener_producto(codigo: str, db: Session = Depends(get_db)):
    service = ProductoService(db)
    result = service.get_producto_by_codigo(codigo)
    if "error" in result:
        raise HTTPException(status_code=404, detail=result["error"])
    return result


@router.get("/productos/{codigo}/historial", summary="Historial de precios", tags=["productos"])
def historial_precios(codigo: str, desde: Optional[str] = None, db: Session = Depends(get_db)):
    service = ProductoService(db)
    return service.get_historial_precios(codigo, desde)


@router.post("/productos/", summary="Crear nuevo producto", tags=["productos"])
def crear_producto(data: ProductoCreate, db: Session = Depends(get_db)):
    service = ProductoService(db)
    result = service.create_producto(data.dict())
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    return result


@router.put("/productos/{codigo}", summary="Actualizar producto", tags=["productos"])
def actualizar_producto(codigo: str, data: ProductoUpdate, db: Session = Depends(get_db)):
    service = ProductoService(db)
    result = service.update_producto(codigo, data.dict(exclude_unset=True))
    if "error" in result:
        raise HTTPException(status_code=404, detail=result["error"])
    return result


@router.delete("/productos/{codigo}", summary="Eliminar producto", tags=["productos"])
def eliminar_producto(codigo: str, db: Session = Depends(get_db)):
    service = ProductoService(db)
    result = service.delete_producto(codigo)
    if "error" in result:
        raise HTTPException(status_code=404, detail=result["error"])
    return result


@router.get("/categorias/", summary="Listar categorías jerárquicas", tags=["categorías"])
def listar_categorias(db: Session = Depends(get_db)):
    service = ProductoService(db)
    return service.get_categorias()


@router.get("/marcas/", summary="Listar marcas disponibles", tags=["marcas"])
def listar_marcas(db: Session = Depends(get_db)):
    service = ProductoService(db)
    return service.get_marcas()
     