# ─────────────────────────────────────────────────────────────────────────────
# Wetchah_GRC — Dockerfile Multi-stage (SvelteKit + FastAPI)
#
# Module 4 de l'écosystème WeTchah : Plateforme de Contrôle de gestion,
# Risques et Conformité.
#
# Stage 1 : Build du frontend SvelteKit SPA (Node 22)
# Stage 2 : Runtime applicatif FastAPI asynchrone (Python 3.12-slim)
# ─────────────────────────────────────────────────────────────────────────────

# ── Stage 1 : Build du Frontend ───────────────────────────────────────────────
FROM node:22-alpine AS build-frontend

WORKDIR /app/frontend

COPY frontend/package.json frontend/package-lock.json* ./
RUN npm install

COPY frontend/ ./
RUN npm run build

# ── Stage 2 : Runtime Backend Python ──────────────────────────────────────────
FROM python:3.12-slim AS runtime

WORKDIR /app

# Dépendances système pour SQLite et compilation éventuelle
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    gcc \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

COPY backend/requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copie du backend
COPY backend/app ./app

# Copie des fichiers statiques générés par SvelteKit
COPY --from=build-frontend /app/frontend/build ./static

# Répertoire persistant pour la base de données SQLite
RUN mkdir -p /data

EXPOSE 8000
ENV PORT=8000
ENV HOST=0.0.0.0
ENV DATABASE_URL="sqlite:////data/grc.db"

HEALTHCHECK --interval=30s --timeout=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
