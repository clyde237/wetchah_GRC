import os
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from app.core.config import settings
from app.core.database import engine, Base, SessionLocal
from app.services.seed_service import seed_database

# Routers
from app.api.v1 import (
    auth, users, risks, compliance, audit,
    policies, incidents, evaluations, third_parties,
    dashboard, reports
)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Création automatique des tables et initialisation du seed si nécessaire
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        seed_database(db)
    finally:
        db.close()
    yield

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="Plateforme de Contrôle de Gestion, Risques et Conformité pour l'écosystème WeTchah.",
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# Configuration CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Inclusion des Routers API v1
app.include_router(auth.router, prefix=f"{settings.API_V1_STR}/auth", tags=["Authentification"])
app.include_router(users.router, prefix=f"{settings.API_V1_STR}/users", tags=["Utilisateurs & RBAC (ADM)"])
app.include_router(risks.router, prefix=f"{settings.API_V1_STR}/risks", tags=["Gestion des Risques (RIS)"])
app.include_router(compliance.router, prefix=f"{settings.API_V1_STR}/compliance", tags=["Conformité & Référentiels (CONF)"])
app.include_router(audit.router, prefix=f"{settings.API_V1_STR}/audit", tags=["Contrôles Internes & Audit (AUD)"])
app.include_router(policies.router, prefix=f"{settings.API_V1_STR}/policies", tags=["Politiques & Documentation (POL)"])
app.include_router(incidents.router, prefix=f"{settings.API_V1_STR}/incidents", tags=["Gestion des Incidents (INC)"])
app.include_router(evaluations.router, prefix=f"{settings.API_V1_STR}/evaluations", tags=["Évaluations en Ligne (EVAL)"])
app.include_router(third_parties.router, prefix=f"{settings.API_V1_STR}/third-parties", tags=["Gestion des Tiers (TIERS)"])
app.include_router(dashboard.router, prefix=f"{settings.API_V1_STR}/dashboard", tags=["Tableaux de Bord & Reporting (REP)"])
app.include_router(reports.router, prefix=f"{settings.API_V1_STR}/reports", tags=["Génération de Rapports"])

# Statut / Health check
@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "service": settings.PROJECT_NAME,
        "tenant_slug": settings.TENANT_SLUG,
        "version": settings.VERSION
    }

# Montage du Frontend statique SvelteKit SPA si le dossier existe
static_dir = os.path.join(os.path.dirname(__file__), "..", "static")
if os.path.exists(static_dir):
    app.mount("/_app", StaticFiles(directory=os.path.join(static_dir, "_app")), name="_app")
    
    @app.get("/{full_path:path}")
    async def serve_spa(full_path: str):
        file_path = os.path.join(static_dir, full_path)
        if os.path.isfile(file_path):
            return FileResponse(file_path)
        # Fallback SPA pour SvelteKit router
        return FileResponse(os.path.join(static_dir, "index.html"))
