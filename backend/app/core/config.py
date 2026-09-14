import os
from typing import List, Union
from pydantic_settings import BaseSettings
from pydantic import AnyHttpUrl, validator

class Settings(BaseSettings):
    PROJECT_NAME: str = "Wetchah_GRC"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    
    # Sécurité & JWT
    SECRET_KEY: str = os.getenv("SECRET_KEY", "wetchah_grc_super_secret_jwt_key_development_only_change_in_prod")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 24 heures
    
    # Base de données
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./grc.db")
    
    # Identité Tenant & Écosystème WeTchah
    TENANT_SLUG: str = os.getenv("TENANT_SLUG", "default")
    TENANT_NAME: str = os.getenv("TENANT_NAME", "Établissement")
    ERP_API_URL: str = os.getenv("ERP_API_URL", "http://localhost:8001")
    REPORTING_SECRET: str = os.getenv("REPORTING_SECRET", "")
    
    # CORS
    CORS_ORIGINS: List[str] = ["*"]

    class Config:
        case_sensitive = True
        env_file = ".env"

settings = Settings()
