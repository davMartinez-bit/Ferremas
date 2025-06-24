from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import AnyUrl, field_validator

class Settings(BaseSettings):
    # Configuración básica de la aplicación
    APP_ENV: str = "development"
    APP_NAME: str = "Ferretería API"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True

    # Configuración CORS
    ALLOWED_ORIGINS: list[str] = ["*"]

    # Configuración de base de datos MySQL
    DB_HOST: str = "localhost"
    DB_PORT: int = 3306
    DB_USER: str = "root"
    DB_PASSWORD: str = "Losurales2163@"
    DB_NAME: str = "ferreteria_db"
    DATABASE_URL: str = ""

    # JWT Secret Key
    SECRET_KEY: str = "tu_super_secret_key_muy_segura_para_jwt_tokens_2025"

    # Configuración Webpay
    WEBPAY_COMMERCE_CODE: str = "597055555532"
    WEBPAY_API_KEY: str = ""
    WEBPAY_ENV: str = "INTEGRACION"
    WEBPAY_SIMULATOR: bool = True

    # Configuración Banco Central
    BANCO_CENTRAL_API_URL: AnyUrl = "https://api.sbif.cl/api-sbifv3/recursos_api"
    BANCO_CENTRAL_API_KEY: str = ""

    # Validaciones
    @field_validator("APP_ENV")
    @classmethod
    def validate_app_env(cls, v: str) -> str:
        if v not in ["development", "testing", "production"]:
            raise ValueError("APP_ENV debe ser development, testing o production")
        return v

    @field_validator("WEBPAY_ENV")
    @classmethod
    def validate_webpay_env(cls, v: str) -> str:
        if v not in ["INTEGRACION", "CERTIFICACION", "PRODUCCION"]:
            raise ValueError("WEBPAY_ENV debe ser INTEGRACION, CERTIFICACION o PRODUCCION")
        return v

    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore",
        case_sensitive=True
    )

settings = Settings()

# Generar la URL de base de datos MySQL con las variables cargadas
if settings.DB_PASSWORD and settings.DB_USER and settings.DB_NAME:
    settings.DATABASE_URL = (
        f"mysql+mysqlconnector://{settings.DB_USER}:{settings.DB_PASSWORD}"
        f"@{settings.DB_HOST}:{settings.DB_PORT}/{settings.DB_NAME}"
    )
else:
    # Fallback a SQLite si no hay configuración de MySQL
    settings.DATABASE_URL = "sqlite:///./ferreteria.db"
