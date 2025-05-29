from fastapi import APIRouter, Depends, Query, HTTPException, status
from sqlalchemy.orm import Session
from typing import Optional, List

from app.data.database import get_db

from app.api.schemas import (
    ProductoCreate, 
    ProductoUpdate, 
    ProductoResponse,
    ProductoBasic,
    HistorialPreciosResponse,
    CategoriaCompleteResponse,
    MarcaCompleteResponse,
    ProductosDestacadosResponse
)

from app.services.productos import ProductoService

router = APIRouter()

# =============================================================================
# ENDPOINTS DE PRODUCTOS
# =============================================================================

@router.get("/productos/{codigo}", response_model=ProductoResponse, summary="Obtener producto por código")
def obtener_producto_por_codigo(
    codigo: str, 
    db: Session = Depends(get_db)
):
    """
    Obtiene los detalles completos de un producto específico por su código.
    
    - **codigo**: Código único del producto
    
    ### Ejemplo de uso:
    ```
    GET /api/productos/MTL-001
    ```
    """
    service = ProductoService(db)
    resultado = service.get_producto_by_codigo(codigo)
    
    if "error" in resultado:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=resultado["error"]
        )
    
    return resultado

@router.get("/productos/", response_model=List[ProductoBasic], summary="Buscar productos con filtros")
def buscar_productos(
    nombre: Optional[str] = Query(None, description="Buscar por nombre (búsqueda parcial)", example="martillo"),
    categoria: Optional[str] = Query(None, description="Filtrar por categoría", example="Herramientas"),
    stock_max: Optional[int] = Query(None, ge=0, description="Productos con stock menor o igual a este valor", example=10),
    db: Session = Depends(get_db)
):
    """
    Busca productos aplicando diferentes filtros.
    
    - **nombre**: Búsqueda parcial por nombre del producto
    - **categoria**: Filtrar productos por categoría
    - **stock_max**: Mostrar productos con stock menor o igual al valor especificado
    
    Al menos uno de los filtros debe ser proporcionado.
    
    ### Ejemplos de uso:
    ```
    GET /api/productos/?nombre=martillo
    GET /api/productos/?categoria=Herramientas
    GET /api/productos/?stock_max=5
    ```
    """
    service = ProductoService(db)
    
    if nombre:
        return service.search_productos_by_name(nombre)
    elif categoria:
        return service.get_productos_by_categoria(categoria)
    elif stock_max is not None:
        return service.get_productos_by_stock(stock_max)
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Debes especificar al menos un filtro (nombre, categoria o stock_max)"
        )

@router.get("/productos/{codigo}/precios", response_model=HistorialPreciosResponse, summary="Historial de precios")
def obtener_historial_precios(
    codigo: str,
    fecha: Optional[str] = Query(None, description="Fecha desde la cual obtener el historial (formato: YYYY-MM-DD)", example="2024-01-01"),
    db: Session = Depends(get_db)
):
    """
    Obtiene el historial de precios de un producto específico.
    
    - **codigo**: Código único del producto
    - **fecha**: Fecha opcional desde la cual obtener el historial (formato: YYYY-MM-DD)
    
    ### Ejemplo de uso:
    ```
    GET /api/productos/MTL-001/precios
    GET /api/productos/MTL-001/precios?fecha=2024-01-01
    ```
    """
    service = ProductoService(db)
    resultado = service.get_historial_precios(codigo, fecha)
    
    if "error" in resultado:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=resultado["error"]
        )
    
    return resultado

@router.post("/productos/", response_model=ProductoResponse, status_code=status.HTTP_201_CREATED, summary="Crear nuevo producto")
def crear_producto(
    producto_data: ProductoCreate, 
    db: Session = Depends(get_db)
):
    """
    Crea un nuevo producto en el sistema.
    
    ### Campos requeridos:
    - **codigo**: Código único del producto
    - **nombre**: Nombre del producto
    - **precio_actual**: Precio actual del producto
    
    ### Campos opcionales:
    - **descripcion**: Descripción del producto
    - **stock**: Cantidad inicial en stock (por defecto: 0)
    - **categoria_id**: ID de la categoría
    - **marca_id**: ID de la marca
    
    ### Ejemplo de payload:
    ```json
    {
        "codigo": "MTL-003",
        "nombre": "Martillo de Goma",
        "descripcion": "Martillo de goma para trabajos delicados",
        "stock": 15,
        "precio_actual": 12990,
        "categoria_id": 1,
        "marca_id": 2
    }
    ```
    """
    service = ProductoService(db)
    resultado = service.create_producto(producto_data.model_dump())
    
    if "error" in resultado:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=resultado["error"]
        )
    
    return resultado

@router.put("/productos/{codigo}", response_model=ProductoResponse, summary="Actualizar producto")
def actualizar_producto(
    codigo: str, 
    producto_data: ProductoUpdate, 
    db: Session = Depends(get_db)
):
    """
    Actualiza un producto existente.
    
    - **codigo**: Código del producto a actualizar
    - Solo se actualizarán los campos proporcionados
    - Si se actualiza el precio, se registrará en el historial
    
    ### Ejemplo de payload:
    ```json
    {
        "nombre": "Martillo de Carpintero 16oz Premium",
        "precio_actual": 17990,
        "stock": 30
    }
    ```
    """
    service = ProductoService(db)
    
    # Filtrar solo los campos que no son None
    update_data = {k: v for k, v in producto_data.model_dump().items() if v is not None}
    
    if not update_data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Debe proporcionar al menos un campo para actualizar"
        )
    
    resultado = service.update_producto(codigo, update_data)
    
    if "error" in resultado:
        if "no encontrado" in resultado["error"].lower():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=resultado["error"]
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=resultado["error"]
            )
    
    return resultado

@router.delete("/productos/{codigo}", summary="Eliminar producto")
def eliminar_producto(
    codigo: str, 
    db: Session = Depends(get_db)
):
    """
    Elimina lógicamente un producto (lo marca como inactivo).
    
    - **codigo**: Código del producto a eliminar
    
    El producto no se elimina físicamente de la base de datos, 
    sino que se marca como inactivo para mantener la integridad referencial.
    """
    service = ProductoService(db)
    resultado = service.delete_producto(codigo)
    
    if "error" in resultado:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=resultado["error"]
        )
    
    return resultado

# =============================================================================
# ENDPOINTS DE PRODUCTOS DESTACADOS
# =============================================================================

@router.get("/productos-destacados/", response_model=ProductosDestacadosResponse, summary="Obtener productos destacados")
def obtener_productos_destacados(db: Session = Depends(get_db)):
    """
    Obtiene productos destacados incluyendo promociones y lanzamientos recientes.
    
    ### Retorna:
    - **promociones**: Productos con cambios de precio recientes
    - **lanzamientos**: Productos creados recientemente
    """
    service = ProductoService(db)
    return service.get_productos_destacados()

@router.get("/promociones/", response_model=List[ProductoBasic], summary="Productos en promoción")
def obtener_promociones(db: Session = Depends(get_db)):
    """
    Obtiene todos los productos actualmente en promoción.
    
    Se consideran en promoción los productos que han tenido 
    cambios de precio en los últimos 15 días.
    """
    service = ProductoService(db)
    return service.get_productos_en_promocion()

@router.get("/lanzamientos/", response_model=List[ProductoBasic], summary="Productos lanzados recientemente")
def obtener_lanzamientos(
    dias: Optional[int] = Query(30, ge=1, le=365, description="Días hacia atrás para considerar como reciente"),
    db: Session = Depends(get_db)
):
    """
    Obtiene productos lanzados en los últimos días especificados.
    
    - **dias**: Número de días hacia atrás (por defecto: 30, máximo: 365)
    
    ### Ejemplo de uso:
    ```
    GET /api/lanzamientos/
    GET /api/lanzamientos/?dias=7
    ```
    """
    service = ProductoService(db)
    return service.get_productos_lanzamiento(dias)

# =============================================================================
# ENDPOINTS DE CATEGORÍAS Y MARCAS
# =============================================================================

@router.get("/categorias/", response_model=List[CategoriaCompleteResponse], summary="Listar todas las categorías")
def listar_categorias(db: Session = Depends(get_db)):
    """
    Obtiene todas las categorías disponibles organizadas jerárquicamente.
    
    ### Estructura jerárquica incluye:
    - **Herramientas**
      - Herramientas Manuales (Martillos, Destornilladores, Llaves)
      - Herramientas Eléctricas (Taladros, Sierras, Lijadoras)
    - **Materiales de Construcción**
      - Materiales Básicos (Cemento, Arena, Ladrillos)
      - Acabados (Pinturas, Barnices, Cerámicos)
    - **Equipos de Seguridad** (Cascos, Guantes, Lentes)
    - **Accesorios Varios** (Tornillos, Fijaciones, Equipos de Medición)
    """
    service = ProductoService(db)
    return service.get_categorias()

@router.get("/marcas/", response_model=List[MarcaCompleteResponse], summary="Listar todas las marcas")
def listar_marcas(db: Session = Depends(get_db)):
    """
    Obtiene todas las marcas disponibles con información adicional.
    
    ### Información incluida:
    - ID y nombre de la marca
    - Código de la marca
    - Total de productos por marca
    
    ### Marcas disponibles incluyen:
    Bosch, DeWalt, Stanley, Makita, Black & Decker, Hilti, entre otras.
    """
    service = ProductoService(db)
    return service.get_marcas()