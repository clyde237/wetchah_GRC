"""
Le jeu initial doit rendre l'application démontrable dès le premier
démarrage : un module dont les écrans s'ouvrent vides passe pour cassé.

Ces tests portent sur ce que le seed doit garantir, pas sur son contenu
exact — le libellé d'un risque peut changer sans casser quoi que ce soit.
"""


def test_les_referentiels_de_conformite_sont_charges(client, admin):
    frameworks = client.get("/api/v1/compliance/frameworks", headers=admin).json()

    codes = {f["code"] for f in frameworks}
    assert {"ISO-27001", "SYSCOHADA-CI"} <= codes


def test_le_registre_des_risques_nest_pas_vide(client, admin):
    risques = client.get("/api/v1/risks/", headers=admin).json()

    assert risques
    assert all(r["residual_score"] == r["residual_impact"] * r["residual_likelihood"] for r in risques)


def test_une_mission_daudit_est_disponible(client, admin):
    """
    Sans mission initiale, l'écran « Rapports de missions » s'ouvre vide sur
    une installation neuve et la génération de PDF paraît hors service.
    """
    missions = client.get("/api/v1/audit/missions", headers=admin).json()

    assert missions, "le seed doit fournir au moins une mission d'audit"


def test_la_mission_du_seed_porte_constats_et_plans_daction(client, admin):
    """
    Le rapport PDF agrège mission → constats → plans d'action : une mission
    sans constat produirait un document vide.
    """
    mission = client.get("/api/v1/audit/missions", headers=admin).json()[0]

    pdf = client.get(f"/api/v1/reports/missions/{mission['id']}/pdf", headers=admin)
    assert pdf.status_code == 200
    assert pdf.content.startswith(b"%PDF")

    plans = client.get("/api/v1/audit/action-plans", headers=admin).json()
    assert plans, "les constats du seed doivent porter des plans d'action"


def test_le_tableau_de_bord_sagrege_sans_erreur(client, admin):
    """Premier écran vu par le contrôleur : il doit être renseigné d'emblée."""
    dashboard = client.get("/api/v1/dashboard/", headers=admin).json()

    assert dashboard["total_risks"] > 0
    assert dashboard["active_controls"] > 0
    assert dashboard["top_risks"]
    assert len(dashboard["heatmap"]) == 25  # matrice 5x5 complète
    # Un plan d'action échu figure dans le jeu initial : le compteur de retard
    # doit le refléter, sinon l'indicateur paraît mort.
    assert dashboard["delayed_action_plans"] > 0


def test_le_flux_pms_est_annonce_indisponible_et_non_simule(client, admin):
    """
    Sans REPORTING_SECRET, le connecteur doit le dire. Il ne doit en aucun
    cas produire des montants plausibles : un chiffre affiché ici est lu
    comme un constat opposable.
    """
    resume = client.get("/api/v1/dashboard/", headers=admin).json()["wetchah_financial_summary"]

    assert resume["available"] is False
    assert resume["reason"] == "not_configured"
    assert resume["error"]
    assert "today_revenue" not in resume
    assert "occupancy_rate" not in resume
