from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, scoped_session, declarative_base
import logging
from config import settings

# ✅ Crear el Base global de los modelos
Base = declarative_base()

DATABASE_URL = settings.DATABASE_URL

# Configurar logging para SQLAlchemy
logging.basicConfig()
logging.getLogger('sqlalchemy.engine').setLevel(logging.INFO if __name__ == "__main__" else logging.WARNING)

# Crear el engine con configuraciones mejoradas para MySQL
engine = create_engine(
    DATABASE_URL,
    echo=False,  # Cambiar a True para debug SQL
    pool_pre_ping=True,  # Verificar conexiones antes de usarlas
    pool_recycle=1800,   # Reciclar conexiones cada 30 minutos (más frecuente)
    pool_size=5,         # Reducir el tamaño del pool para evitar sobrecarga
    max_overflow=10,     # Reducir conexiones adicionales
    pool_timeout=30,     # Timeout para obtener conexión del pool
    pool_reset_on_return='rollback',  # Rollback automático al devolver conexión
    connect_args={
        "charset": "utf8mb4",
        "use_unicode": True,
        "autocommit": False,
        "ssl_disabled": True
    }
)

# Configurar el sessionmaker con mejor manejo de errores
SessionLocal = sessionmaker(
    bind=engine,
    autocommit=False,
    autoflush=False,
    expire_on_commit=False
)

# Crear sesión con scope
db_session = scoped_session(SessionLocal)

def get_db():
    """
    Generador de sesiones de base de datos para FastAPI Dependency Injection
    con mejor manejo de errores
    """
    db = db_session()
    try:
        # Verificar que la conexión esté activa
        db.execute(text("SELECT 1"))
        yield db
    except Exception as e:
        print(f"Error en get_db: {e}")
        db.rollback()
        # Invalidar la sesión para forzar una nueva conexión
        db_session.remove()
        raise e
    finally:
        try:
            db.close()
        except Exception as e:
            print(f"Error cerrando sesión: {e}")
            # Forzar limpieza del scope
            db_session.remove()

def test_connection():
    """
    Prueba la conexión a la base de datos
    """
    try:
        db = db_session()
        # Ejecutar una consulta simple para probar la conexión
        result = db.execute(text("SELECT 1"))
        result.fetchone()
        print("✅ Conexión a MySQL establecida correctamente")
        return True
    except Exception as e:
        print(f"❌ Error conectando a MySQL: {e}")
        return False
    finally:
        try:
            db.close()
        except:
            pass
        db_session.remove()

def reset_db_session():
    """
    Resetea la sesión de base de datos
    """
    try:
        db_session.remove()
        print("✅ Sesión de base de datos reseteada")
    except Exception as e:
        print(f"❌ Error reseteando sesión: {e}")

if __name__ == "__main__":
    print("Probando conexión a la base de datos...")
    test_connection()