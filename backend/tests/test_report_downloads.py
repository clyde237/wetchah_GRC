"""
Boucle « exports » : les rapports doivent rester protégés par le jeton, et
être réellement téléchargeables par un client qui le présente.

Avant la fermeture de cette boucle, l'interface pointait vers ces endpoints
par de simples liens <a href> : le navigateur n'envoyant aucun en-tête
Authorization, tous les téléchargements répondaient 401. Le correctif est
côté client (fetch authentifié puis blob) ; ces tests verrouillent le
contrat côté serveur dont il dépend.
"""

import pytest


@pytest.fixture(scope="module")
def mission(client, admin):
    """
    Mission propre au test plutôt que celle du seed : le contenu du jeu de
    démonstration peut évoluer, ces assertions ne doivent pas en dépendre.
    """
    mission = client.post("/api/v1/audit/missions", headers=admin, json={
        "reference": "AUD-TEST-2026",
        "title": "Audit du cycle caisse",
        "scope": "Réception et restaurant, juillet à septembre.",
        "start_date": "2026-07-01T08:00:00",
        "end_date": "2026-09-30T18:00:00",
    }).json()

    client.post("/api/v1/audit/findings", headers=admin, json={
        "mission_id": mission["id"],
        "code": "CST-01",
        "title": "Comptage de caisse non contradictoire",
        "description": "Le comptage du soir est réalisé par un seul agent.",
        "severity": "majeur",
        "recommendation": "Instaurer un double comptage signé par deux agents.",
    })
    return mission


def test_export_excel_refuse_sans_jeton(client):
    assert client.get("/api/v1/reports/risks/excel").status_code == 401


def test_export_excel_servi_avec_jeton(client, admin):
    reponse = client.get("/api/v1/reports/risks/excel", headers=admin)

    assert reponse.status_code == 200
    assert len(reponse.content) > 1000
    # Le nom vient du serveur : le client n'a pas à le réinventer.
    assert "filename=" in reponse.headers["content-disposition"]


def test_pdf_de_mission_refuse_sans_jeton(client, mission):
    assert client.get(f"/api/v1/reports/missions/{mission['id']}/pdf").status_code == 401


def test_pdf_de_mission_servi_avec_jeton(client, admin, mission):
    reponse = client.get(f"/api/v1/reports/missions/{mission['id']}/pdf", headers=admin)

    assert reponse.status_code == 200
    assert reponse.content.startswith(b"%PDF")
    assert mission["reference"] in reponse.headers["content-disposition"]


def test_mission_inexistante(client, admin):
    assert client.get("/api/v1/reports/missions/99999/pdf", headers=admin).status_code == 404
