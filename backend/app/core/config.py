import os
import secrets
from typing import List
from pydantic_settings import BaseSettings

# Valeurs de SECRET_KEY historiquement livrées dans le dépôt ou dans les
# gabarits d'environnement. Elles sont publiques : un jeton signé avec l'une
# d'elles peut être forgé par n'importe qui. Le service refuse de démarrer
# tant que l'une d'elles est active.
INSECURE_SECRET_KEYS = {
    "wetchah_grc_super_secret_jwt_key_development_only_change_in_prod",
    "change_this_to_a_secure_random_key_in_production",
    "changeme",
    "secret",
}


class Settings(BaseSettings):
    PROJECT_NAME: str = "Wetchah_GRC"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"

    # Sécurité & JWT.
    # Aucune valeur par défaut : la clé signe les jetons d'accès admin de
    # l'établissement. Un défaut en dur signifierait que tous les
    # établissements partagent la même clé — et donc qu'un jeton forgé sur
    # l'un ouvre tous les autres. Elle est injectée par wetchah_erp au
    # provisioning (une clé aléatoire par établissement, figée dans le
    # docker-compose du tenant), ou par le .env en développement.
    SECRET_KEY: str = ""
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 24 heures

    # Base de données
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./grc.db")

    # Identité Tenant & Écosystème WeTchah
    TENANT_SLUG: str = os.getenv("TENANT_SLUG", "default")
    TENANT_NAME: str = os.getenv("TENANT_NAME", "Établissement")
    ERP_API_URL: str = os.getenv("ERP_API_URL", "http://localhost:8001")
    REPORTING_SECRET: str = os.getenv("REPORTING_SECRET", "")

    # CORS : le frontend SvelteKit est servi par ce même service (montage
    # statique dans main.py), donc aucune origine tierce n'a besoin d'accéder
    # à l'API. On n'ouvre que ce qui est explicitement déclaré.
    # Format attendu : CORS_ORIGINS="https://grc.exemple.com,https://autre.exemple.com"
    CORS_ORIGINS: List[str] = []

    class Config:
        case_sensitive = True
        env_file = ".env"


def _load_settings() -> Settings:
    loaded = Settings()

    key = (loaded.SECRET_KEY or "").strip()

    if not key or key in INSECURE_SECRET_KEYS:
        raise RuntimeError(
            "SECRET_KEY absente ou non sécurisée.\n"
            "\n"
            "Cette clé signe les jetons d'authentification du module GRC : sans "
            "valeur propre à l'établissement, n'importe qui peut forger un jeton "
            "administrateur.\n"
            "\n"
            "  • Déploiement conteneurisé : la clé est générée et injectée par "
            "wetchah_erp (variable SECRET_KEY du docker-compose du tenant). "
            "Si elle manque, relancer la mise à jour de l'établissement depuis "
            "l'espace TECH pour régénérer le compose.\n"
            "  • Développement local : ajouter dans backend/.env une clé "
            "aléatoire, par exemple\n"
            "        SECRET_KEY=" + secrets.token_hex(32) + "\n"
        )

    if len(key) < 32:
        raise RuntimeError(
            f"SECRET_KEY trop courte ({len(key)} caractères). "
            "Utiliser au minimum 32 caractères aléatoires "
            f"(ex. : {secrets.token_hex(32)})."
        )

    return loaded


settings = _load_settings()
