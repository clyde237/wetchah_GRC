# Wetchah_GRC — Plateforme de Contrôle de Gestion, Risques & Conformité

Quatrième module officiel de l'écosystème **WeTchah** (aux côtés de `wetchah_app`, `wetchah_erp` et `wetchah_site`), développé conformément au Cahier des Charges (CDC v1.0, Clyde Fanche, Douala).

---

## 1. Architecture Technique
- **Frontend** : SvelteKit + Tailwind CSS + Lucide Icons (Single Page Application servie directement par le backend FastAPI).
- **Backend** : FastAPI (Python 3.12, asynchrone, Pydantic v2, documentation Swagger OpenAPI sous `/docs`).
- **Base de données** : SQLite WAL persistant dans `/data/grc.db` (avec support direct SQLAlchemy pour migration PostgreSQL si souhaité).
- **Moteur d'Audit & Reporting** : Générateur ReportLab PDF (rapports d'audit professionnels) et openpyxl (export cartographie Excel).
- **Intégration PMS** : Consommation directe des flux financiers, de caisse et d'anomalies de `wetchah_app` via l'API sécurisée (`REPORTING_SECRET`).

---

## 2. Les 9 Modules Fonctionnels du Cahier des Charges

| Module | Code CDC | Fonctionnalités Clés |
|---|---|---|
| **Gestion des Risques** | `RIS-01` à `RIS-08` | Fiche de risque, score inhérent et résiduel ($P \times I$), matrice interactive 5x5 Heatmap, plans d'atténuation. |
| **Conformité Réglementaire** | `CONF-01` à `CONF-06` | Référentiels **ISO/IEC 27001:2022** et **SYSCOHADA**, calcul de conformité global, suivi des écarts. |
| **Audit & Contrôle Interne** | `AUD-01` à `AUD-07` | Référentiel des contrôles, tests périodiques, missions d'audit de terrain, constats et plans d'action (CAPA). |
| **Gouvernance Documentaire** | `POL-01` à `POL-05` | Politiques et procédures, cycle de vie (brouillon, revue, approbation, publication, archivage), versioning. |
| **Gestion des Incidents** | `INC-01` à `INC-05` | Déclaration, criticité, assignation, traitement et **condition obligatoire de REX** (leçons apprises) avant clôture. |
| **Évaluations en Ligne** | `EVAL-01` à `EVAL-05` | Questionnaires de contrôle interne, campagnes périodiques et notation automatique de maturité. |
| **Gestion des Tiers** | `TIERS-01` à `TIERS-04` | Cartographie des fournisseurs/sous-traitants, criticité opérationnelle, dépendance et clauses de conformité. |
| **Reporting & Tableaux de Bord** | `REP-01` à `REP-04` | Dashboard consolidé, export Excel (`.xlsx`), génération de rapports PDF d'audit ReportLab. |
| **Administration & Sécurité** | `ADM-01` à `ADM-05` | RBAC à 6 rôles (`admin`, `controller`, `auditor`, `risk_manager`, `executive`, `risk_owner`), journal d'audit des activités. |

---

## 3. Identifiants Pré-configurés (Seed)

| Rôle | Adresse Email | Mot de Passe par Défaut |
|---|---|---|
| **Administrateur GRC** | `admin@wetchah.local` | `admin1234` |
| **Contrôleur de Gestion** | `controller@wetchah.local` | `controller1234` |
| **Auditeur Interne** | `auditor@wetchah.local` | `auditor1234` |

> *Note : Les contrôleurs de gestion d'un établissement client sont créés directement depuis l'interface `wetchah_erp`.*

---

## 4. Démarrage et Déploiement

### Option A : Déploiement Automatique via `wetchah_erp` (Recommandé)
Dans `wetchah_erp` :
1. Activez le module **Contrôle de Gestion & GRC** sur la fiche de l'établissement.
2. Le provisioning Docker génère et démarre automatiquement le conteneur `meka-erp-{$slug}-grc` sur le port `grc_port = app_port + 2000`.
3. Cliquez sur **« Créer le contrôleur GRC »** pour générer les identifiants d'accès du contrôleur de l'établissement.

### Option B : Standalone Docker
```bash
docker compose up -d --build
```
L'application est disponible sur `http://localhost:8000` (Frontend SPA et API Swagger sur `/docs`).

### Option C : Développement Local

#### Backend
```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```
Swagger UI disponible sur : `http://localhost:8000/docs`

#### Frontend
```bash
cd frontend
npm install
npm run dev
```
Interface de développement disponible sur : `http://localhost:5173`
Pour générer les fichiers statiques de production :
```bash
npm run build
cp -r build/* ../backend/static/
```
