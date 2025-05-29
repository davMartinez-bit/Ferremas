from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session, declarative_base  # ✅
import logging
from config import settings

# ✅ Crear el Base global de los modelos
Base = declarative_base()


DATABASE_URL = settings.DATABASE_URL

# Configurar logging para SQLAlchemy
logging.basicConfig()
logging.getLogger('sqlalchemy.engine').setLevel(logging.INFO if __name__ == "__main__" else logging.WARNING)

# Crear el engine con configuraciones específicas para MySQL
engine = create_engine(
    DATABASE_URL,
    echo=False,  # Cambiar a True para debug SQL
    pool_pre_ping=True,  # Verificar conexiones antes de usarlas
    pool_recycle=3600,   # Reciclar conexiones cada hora
    pool_size=10,        # Tamaño del pool de conexiones
    max_overflow=20,     # Conexiones adicionales permitidas
    connect_args={
        "charset": "utf8mb4",
        "use_unicode": True,
        "autocommit": False
    }
)

# Configurar el sessionmaker
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
    """
    db = db_session()
    try:
        yield db
    except Exception as e:
        db.rollback()
        raise e
    finally:
        db.close()

def test_connection():
    """
    Prueba la conexión a la base de datos
    """
    try:
        db = db_session()
        # Ejecutar una consulta simple para probar la conexión
        result = db.execute("SELECT 1")
        result.fetchone()
        print("✅ Conexión a MySQL establecida correctamente")
        return True
    except Exception as e:
        print(f"❌ Error conectando a MySQL: {e}")
        return False
    finally:
        db.close()

if __name__ == "__main__":
    print("Probando conexión a la base de datos...")
    test_connection()