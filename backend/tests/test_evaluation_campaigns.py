"""
Boucle « évaluations en ligne » : une campagne doit pouvoir recevoir des
réponses de personnes qui n'ont pas de compte GRC, et le contrôleur doit
pouvoir les dépouiller.

Avant la fermeture de cette boucle, `launch_campaign` produisait des jetons
d'accès qu'aucun endpoint ne consommait : les campagnes ne pouvaient
recueillir aucune réponse.
"""

import pytest


@pytest.fixture(scope="module")
def campagne(client, admin):
    """Un questionnaire de contrôle interne et sa campagne, avec un répondant."""
    questionnaire = client.post("/api/v1/evaluations/questionnaires", headers=admin, json={
        "title": "Contrôle interne caisse",
        "description": "Auto-évaluation trimestrielle des points de vente.",
        "target_type": "interne",
        "questions": [
            {"order_num": 1, "section": "Caisse",
             "question_text": "La caisse est-elle comptée chaque soir ?",
             "question_type": "yes_no", "is_risk_trigger": True},
            {"order_num": 2, "section": "Caisse",
             "question_text": "Fréquence des contrôles inopinés ?",
             "question_type": "scale_1_5", "is_risk_trigger": True},
            {"order_num": 3, "section": "Observations",
             "question_text": "Remarques libres",
             "question_type": "text", "is_risk_trigger": False},
        ],
    }).json()

    campagne = client.post("/api/v1/evaluations/campaigns", headers=admin, json={
        "questionnaire_id": questionnaire["id"],
        "title": "Campagne T3 2026",
        "deadline": "2099-12-31T23:59:00",
        "respondents": [{"name": "Chef de réception", "email": "reception@hotel.test"}],
    }).json()

    liens = client.get(f"/api/v1/evaluations/campaigns/{campagne['id']}/links", headers=admin)
    assert liens.status_code == 200, liens.text
    token = liens.json()[0]["path"].split("/respond/")[1]

    return {"id": campagne["id"], "token": token}


def test_le_repondant_ouvre_le_formulaire_sans_compte(client, campagne):
    """Le jeton de l'URL fait seul office d'autorisation."""
    response = client.get(f"/api/v1/evaluations/respond/{campagne['token']}")

    assert response.status_code == 200
    form = response.json()
    assert len(form["questions"]) == 3
    assert form["respondent_name"] == "Chef de réception"
    assert not form["is_completed"]


def test_le_formulaire_cache_les_questions_sensibles(client, campagne):
    """
    Un répondant qui saurait quelles réponses déclenchent une alerte serait
    tenté d'orienter les siennes.
    """
    form = client.get(f"/api/v1/evaluations/respond/{campagne['token']}").json()

    assert all("is_risk_trigger" not in q for q in form["questions"])


def test_un_jeton_inconnu_est_refuse(client):
    assert client.get("/api/v1/evaluations/respond/jeton-invente").status_code == 404


def test_soumission_note_les_reponses_et_signale_les_points_sensibles(client, admin, campagne):
    """
    Barème : « non » vaut 0, l'échelle 5/5 vaut 100, le texte libre n'est pas
    noté. Le score est la moyenne des seules réponses notables — ici 50.
    La question sensible répondue « non » doit remonter au contrôleur.
    """
    form = client.get(f"/api/v1/evaluations/respond/{campagne['token']}").json()
    ids = {q["question_text"][:12]: q["id"] for q in form["questions"]}

    envoi = client.post(f"/api/v1/evaluations/respond/{campagne['token']}", json={"answers": [
        {"question_id": ids["La caisse es"], "value": "non"},
        {"question_id": ids["Fréquence de"], "value": "5"},
        {"question_id": ids["Remarques li"], "value": "RAS"},
    ]})

    assert envoi.status_code == 200, envoi.text
    resultat = envoi.json()
    assert resultat["score"] == 50.0
    assert resultat["answered"] == 3
    assert resultat["scored"] == 2      # le texte libre documente sans mesurer
    assert not resultat["is_late"]

    depouillement = client.get(
        f"/api/v1/evaluations/campaigns/{campagne['id']}/responses", headers=admin
    ).json()[0]
    assert depouillement["is_completed"]
    assert depouillement["score"] == 50.0
    assert depouillement["triggered_count"] == 1


def test_le_detail_designe_la_question_declenchee(client, auditor, campagne):
    """La pièce que le contrôleur verse à son dossier d'audit."""
    reponses = client.get(
        f"/api/v1/evaluations/campaigns/{campagne['id']}/responses", headers=auditor
    ).json()
    detail = client.get(
        f"/api/v1/evaluations/campaigns/{campagne['id']}/responses/{reponses[0]['id']}",
        headers=auditor,
    ).json()

    declenchees = [a for a in detail["answers"] if a["triggered"]]
    assert len(declenchees) == 1
    assert declenchees[0]["question_text"].startswith("La caisse")
    assert declenchees[0]["scored_value"] == 0.0

    # Sensible mais bien notée : aucune alerte.
    bien_notee = next(a for a in detail["answers"] if a["question_text"].startswith("Fréquence"))
    assert bien_notee["is_risk_trigger"] and not bien_notee["triggered"]


def test_une_reponse_transmise_ne_peut_pas_etre_reecrite(client, campagne):
    """Autoriser la reprise reviendrait à laisser réécrire une déclaration versée au dossier."""
    form = client.get(f"/api/v1/evaluations/respond/{campagne['token']}").json()
    assert form["is_completed"]

    rejeu = client.post(f"/api/v1/evaluations/respond/{campagne['token']}", json={
        "answers": [{"question_id": form["questions"][0]["id"], "value": "oui"}]
    })
    assert rejeu.status_code == 409


def test_le_compteur_de_campagne_suit_les_reponses(client, admin, campagne):
    campagnes = client.get("/api/v1/evaluations/campaigns", headers=admin).json()
    courante = next(c for c in campagnes if c["id"] == campagne["id"])

    assert courante["total_responses"] == 1
    assert courante["completed_responses"] == 1
