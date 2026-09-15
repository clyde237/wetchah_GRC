"""
Boucle « cycle de vie documentaire » : une politique doit pouvoir parcourir
brouillon → revue → approbation → publication, porter ses versions et
recueillir des accusés de lecture.

Avant la fermeture de cette boucle, le module n'exposait que « lister » et
« créer » : les tables de versions et d'accusés existaient sans qu'aucun
endpoint ne puisse les alimenter.
"""

import pytest


@pytest.fixture(scope="module")
def politique(client, admin):
    reponse = client.post("/api/v1/policies/", headers=admin, json={
        "code": "POL-TEST-01",
        "title": "Politique de caisse",
        "document_type": "politique",
        "content": "Contenu initial.",
        "review_frequency_days": 180,
    })
    assert reponse.status_code == 201, reponse.text
    return reponse.json()


def test_une_politique_nait_en_brouillon(politique):
    assert politique["status"] == "brouillon"
    assert politique["version_count"] == 0
    assert politique["acknowledgment_count"] == 0


def test_le_cycle_ne_se_saute_pas(client, admin, politique):
    """
    Passer directement de brouillon à publié priverait l'approbation de toute
    valeur devant un auditeur externe.
    """
    saut = client.put(f"/api/v1/policies/{politique['id']}", headers=admin,
                      json={"status": "publie"})

    assert saut.status_code == 400
    assert "non permis" in saut.json()["detail"]


def test_parcours_complet_jusqua_la_publication(client, admin, politique):
    pid = politique["id"]

    assert client.put(f"/api/v1/policies/{pid}", headers=admin,
                      json={"status": "en_revue"}).status_code == 200
    assert client.put(f"/api/v1/policies/{pid}", headers=admin,
                      json={"status": "approuve"}).status_code == 200
    publiee = client.put(f"/api/v1/policies/{pid}", headers=admin, json={"status": "publie"})

    assert publiee.status_code == 200
    assert publiee.json()["status"] == "publie"

    detail = client.get(f"/api/v1/policies/{pid}", headers=admin).json()
    # Publier fait courir le délai de revue, sinon l'échéance n'est jamais suivie.
    assert detail["next_review_date"] is not None
    assert set(detail["allowed_transitions"]) == {"archive", "en_revue"}


def test_accuse_de_lecture_reserve_aux_textes_publies(client, admin, auditor):
    """On n'accuse pas réception d'un brouillon susceptible de changer."""
    brouillon = client.post("/api/v1/policies/", headers=admin, json={
        "code": "POL-TEST-02", "title": "Procédure d'inventaire",
    }).json()

    refus = client.post(f"/api/v1/policies/{brouillon['id']}/acknowledge", headers=auditor)

    assert refus.status_code == 400


def test_accuse_de_lecture_idempotent(client, admin, auditor, politique):
    """Un second appel ne doit pas empiler un doublon."""
    pid = politique["id"]

    premier = client.post(f"/api/v1/policies/{pid}/acknowledge", headers=auditor)
    second = client.post(f"/api/v1/policies/{pid}/acknowledge", headers=auditor)

    assert premier.status_code == 201
    assert second.json()["id"] == premier.json()["id"]

    accuses = client.get(f"/api/v1/policies/{pid}/acknowledgments", headers=admin).json()
    assert len(accuses) == 1
    assert accuses[0]["user_name"]  # la pièce attendue lors d'un audit de diffusion


def test_nouvelle_version_rouvre_le_cycle(client, admin, politique):
    """
    Un texte modifié après publication n'est plus le texte approuvé : les
    accusés recueillis sur l'ancienne version ne valent plus pour la nouvelle.
    """
    pid = politique["id"]

    version = client.post(f"/api/v1/policies/{pid}/versions", headers=admin, json={
        "version_number": "2.0",
        "change_summary": "Ajout du double comptage.",
        "approve": True,
    })

    assert version.status_code == 201
    assert version.json()["approved_at"] is not None

    apres = client.get(f"/api/v1/policies/{pid}", headers=admin).json()
    assert apres["current_version"] == "2.0"
    assert apres["status"] == "approuve"      # n'est plus « publié »
    assert apres["version_count"] == 1


def test_un_numero_de_version_deja_pris_est_refuse(client, admin, politique):
    doublon = client.post(f"/api/v1/policies/{politique['id']}/versions", headers=admin,
                          json={"version_number": "2.0", "change_summary": "doublon"})

    assert doublon.status_code == 400


def test_un_auditeur_ne_redige_pas_les_politiques(client, auditor, politique):
    """Rédiger et contrôler sont deux rôles distincts."""
    tentative = client.post(f"/api/v1/policies/{politique['id']}/versions", headers=auditor,
                            json={"version_number": "3.0", "change_summary": "x"})

    assert tentative.status_code == 403


def test_les_actes_sont_traces_au_journal(client, admin):
    """Un cycle documentaire sans piste d'audit ne vaut rien."""
    actions = {ligne["action"] for ligne in client.get("/api/v1/users/logs", headers=admin).json()}

    assert {"STATUS", "VERSION", "ACKNOWLEDGE"} <= actions
