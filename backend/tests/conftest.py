"""
Socle des tests : une base SQLite jetable par session, montée par le lifespan
réel de l'application (création des tables + seed), et des clients déjà
authentifiés pour les rôles dont les tests ont besoin.

Les variables d'environnement sont posées avant tout import de `app` : la
configuration et le moteur SQLAlchemy sont lus au chargement des modules.
"""

import os
import sys
import tempfile
from pathlib import Path

BACKEND_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BACKEND_ROOT))

os.environ.setdefault("SECRET_KEY", "test-" + "0" * 60)
os.environ["DATABASE_URL"] = "sqlite:///" + str(Path(tempfile.mkdtemp()) / "test_grc.db")
# Vide : le connecteur doit répondre « non configuré » plutôt que d'aller
# chercher un PMS qui n'existe pas dans un environnement de test.
os.environ["REPORTING_SECRET"] = ""

# La SPA compilée (backend/static/) n'est pas versionnée : elle est produite
# par le build de l'image. Sans elle, app.main n'enregistre pas du tout la
# route de service des fichiers — et le test de traversée de répertoire
# passait pour un simple 404, sans jamais atteindre le garde-fou qu'il est
# censé vérifier. On pose donc un squelette minimal quand il manque, pour que
# la CI exerce le même chemin de code que la production.
_STATIC = BACKEND_ROOT / "static"
(_STATIC / "_app").mkdir(parents=True, exist_ok=True)
_INDEX = _STATIC / "index.html"
if not _INDEX.exists():
    _INDEX.write_text("<!doctype html><title>SPA de test</title>", encoding="utf-8")

import pytest  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402

from app.main import app  # noqa: E402


@pytest.fixture(scope="session")
def client():
    # Le gestionnaire de contexte déclenche le lifespan : sans lui, aucune
    # table n'est créée et le seed n'est jamais joué.
    with TestClient(app) as test_client:
        yield test_client


def _headers(client, email: str, password: str) -> dict:
    response = client.post("/api/v1/auth/login", json={"email": email, "password": password})
    assert response.status_code == 200, response.text
    return {"Authorization": f"Bearer {response.json()['access_token']}"}


@pytest.fixture(scope="session")
def admin(client) -> dict:
    """Administrateur GRC — rédige, approuve et publie."""
    return _headers(client, "admin@wetchah.local", "admin1234")


@pytest.fixture(scope="session")
def auditor(client) -> dict:
    """Auditeur interne — consulte et dépouille, ne rédige pas."""
    return _headers(client, "auditor@wetchah.local", "auditor1234")
