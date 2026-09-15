"""
Deux défauts relevés en revue de code et corrigés : la traversée de
répertoire du service de fichiers statiques, et l'absence de bornes sur les
notes de risque.

Ils n'ont rien en commun sinon d'être invisibles depuis l'interface : le
premier ne s'atteint qu'en forgeant une URL, le second qu'en appelant l'API
directement.
"""

import pytest


# ── Service des fichiers statiques ─────────────────────────────────────────

@pytest.mark.parametrize("chemin", [
    "../backend/app/core/config.py",
    "../../etc/passwd",
    "..%2F..%2Fetc%2Fpasswd",
    "app/core/security.py",
])
def test_aucune_sortie_du_dossier_statique(client, chemin):
    """
    Le gestionnaire SPA servait tout fichier dont le chemin était construit
    par simple concaténation : « .. » suffisait à sortir du dossier et à lire
    le code ou la base SQLite du conteneur.

    Une tentative ne doit pas se distinguer d'une URL inconnue : dans les deux
    cas, la SPA est renvoyée.
    """
    reponse = client.get(f"/{chemin}")

    assert reponse.status_code == 200
    corps = reponse.content
    assert b"SECRET_KEY" not in corps
    assert b"root:" not in corps
    assert b"def " not in corps          # aucun code Python ne transparaît


def test_la_racine_sert_toujours_la_spa(client):
    reponse = client.get("/")

    assert reponse.status_code == 200
    # Le dossier statique n'existe pas en environnement de test : l'API répond
    # quand même sans erreur serveur, ce qui suffit à valider le routage.
    assert reponse.status_code < 500


# ── Bornes des notes de risque ─────────────────────────────────────────────

def _risque(**kwargs):
    base = {
        "code": "RSK-BORNE-001",
        "title": "Risque de test",
        "description": "Vérification des bornes de notation.",
        "category": "operationnel",
    }
    base.update(kwargs)
    return base


@pytest.mark.parametrize("champ", [
    "gross_impact", "gross_likelihood", "residual_impact", "residual_likelihood",
])
@pytest.mark.parametrize("valeur", [0, 6, 99, -3])
def test_une_note_hors_matrice_est_refusee(client, admin, champ, valeur):
    """
    La heatmap est une grille 5x5. Une note hors bornes produisait un score
    aberrant et faisait disparaître le risque de la matrice — il restait en
    tête du classement sans apparaître dans aucune case.
    """
    reponse = client.post(
        "/api/v1/risks/", headers=admin,
        json=_risque(code=f"RSK-{champ}-{valeur}", **{champ: valeur}),
    )

    assert reponse.status_code == 422, reponse.text


def test_les_bornes_1_et_5_restent_acceptees(client, admin):
    reponse = client.post("/api/v1/risks/", headers=admin, json=_risque(
        code="RSK-BORNE-VALIDE",
        gross_impact=5, gross_likelihood=5,
        residual_impact=1, residual_likelihood=1,
    ))

    assert reponse.status_code == 201, reponse.text
    corps = reponse.json()
    assert corps["gross_score"] == 25
    assert corps["residual_score"] == 1


def test_les_valeurs_par_defaut_sont_preservees(client, admin):
    """Poser des bornes ne devait pas rendre ces champs obligatoires."""
    reponse = client.post("/api/v1/risks/", headers=admin, json=_risque(code="RSK-DEFAUT"))

    assert reponse.status_code == 201, reponse.text
    corps = reponse.json()
    assert (corps["gross_impact"], corps["gross_likelihood"]) == (3, 3)
    assert (corps["residual_impact"], corps["residual_likelihood"]) == (2, 2)


def test_une_mise_a_jour_hors_bornes_est_refusee(client, admin):
    cree = client.post("/api/v1/risks/", headers=admin, json=_risque(code="RSK-MAJ-BORNE"))
    assert cree.status_code == 201

    refus = client.put(
        f"/api/v1/risks/{cree.json()['id']}", headers=admin,
        json={"residual_impact": 7},
    )

    assert refus.status_code == 422, refus.text


def test_tout_risque_du_registre_tient_dans_la_matrice(client, admin):
    """Garde-fou d'ensemble : aucune fiche ne doit tomber hors de la heatmap."""
    risques = client.get("/api/v1/risks/", headers=admin).json()
    cases = {f"{c['impact']}_{c['likelihood']}"
             for c in client.get("/api/v1/risks/heatmap", headers=admin).json()}

    for r in risques:
        assert f"{r['residual_impact']}_{r['residual_likelihood']}" in cases, r["code"]


# ── Provisioning depuis l'ERP ──────────────────────────────────────────────

def test_le_provisioning_refuse_un_jeton_vide(client, monkeypatch):
    """
    La garde comparait le jeton reçu au secret de service. Avec un secret non
    configuré — les deux chaînes vides —, « Authorization: Bearer » suffisait
    à se créer un compte. On refuse désormais l'opération plutôt que de
    l'ouvrir.
    """
    from app.core import config

    monkeypatch.setattr(config.settings, "REPORTING_SECRET", "", raising=False)

    reponse = client.post(
        "/api/v1/users/provision-from-erp",
        headers={"Authorization": "Bearer "},
        json={"email": "intrus@exemple.test", "password": "x", "full_name": "Intrus"},
    )

    assert reponse.status_code == 503


def test_le_provisioning_refuse_un_mauvais_secret(client, monkeypatch):
    from app.core import config

    monkeypatch.setattr(config.settings, "REPORTING_SECRET", "le-bon-secret", raising=False)

    reponse = client.post(
        "/api/v1/users/provision-from-erp",
        headers={"Authorization": "Bearer mauvais"},
        json={"email": "intrus@exemple.test", "password": "x", "full_name": "Intrus"},
    )

    assert reponse.status_code == 403


def test_le_provisioning_accepte_le_bon_secret(client, monkeypatch):
    from app.core import config

    monkeypatch.setattr(config.settings, "REPORTING_SECRET", "le-bon-secret", raising=False)

    reponse = client.post(
        "/api/v1/users/provision-from-erp",
        headers={"Authorization": "Bearer le-bon-secret"},
        json={
            "email": "controleur@exemple.test",
            "password": "motdepasse",
            "full_name": "Contrôleur de gestion",
            "role": "controller",
        },
    )

    assert reponse.status_code == 201, reponse.text
    assert reponse.json()["role"] == "controller"


# ── Identité affichée dans l'en-tête ───────────────────────────────────────

def test_health_porte_le_nom_de_l_etablissement(client):
    """L'en-tête y lit le nom de l'établissement sur lequel le module tourne."""
    corps = client.get("/health").json()

    assert "tenant_name" in corps
    assert corps["tenant_slug"]


def test_l_etat_de_la_liaison_pms_est_rapporte(client, admin):
    """
    L'en-tête affichait « Liaison PMS Active » en dur. Sans secret de
    reporting, l'état doit dire que la liaison n'est pas établie.
    """
    etat = client.get("/api/v1/dashboard/pms", headers=admin).json()

    assert etat["available"] is False
    assert etat["reason"] == "not_configured"
    assert etat["error"]


def test_un_changement_d_adresse_renomme_au_lieu_de_dupliquer(client, monkeypatch):
    """
    Quand l'ERP change l'adresse d'un contrôleur, il transmet l'ancienne. Sans
    elle, le provisioning créerait un second compte et l'ancienne adresse
    continuerait d'ouvrir le portail.
    """
    from app.core import config

    monkeypatch.setattr(config.settings, "REPORTING_SECRET", "le-bon-secret", raising=False)
    entete = {"Authorization": "Bearer le-bon-secret"}

    client.post("/api/v1/users/provision-from-erp", headers=entete, json={
        "email": "ancienne@exemple.test", "password": "p", "full_name": "Paul Atangana",
    })

    renomme = client.post("/api/v1/users/provision-from-erp", headers=entete, json={
        "email": "nouvelle@exemple.test",
        "previous_email": "ancienne@exemple.test",
        "password": "p2",
        "full_name": "Paul Atangana",
    })

    assert renomme.status_code == 201, renomme.text

    adresses = [u["email"] for u in client.get("/api/v1/users/", headers=_admin_entete(client)).json()]
    assert "nouvelle@exemple.test" in adresses
    assert "ancienne@exemple.test" not in adresses


def _admin_entete(client) -> dict:
    reponse = client.post("/api/v1/auth/login",
                          json={"email": "admin@wetchah.local", "password": "admin1234"})
    return {"Authorization": f"Bearer {reponse.json()['access_token']}"}
