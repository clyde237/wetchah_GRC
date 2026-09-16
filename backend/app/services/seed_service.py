from datetime import datetime, timezone, timedelta
from sqlalchemy.orm import Session
from app.core.security import get_password_hash
from app.models.user import User
from app.models.risk import Risk
from app.models.compliance import Framework, Requirement
from app.models.audit import InternalControl, AuditMission, AuditFinding, ActionPlan
from app.models.policy import PolicyDocument, PolicyVersion
from app.models.incident import Incident
from app.models.evaluation import Questionnaire, Question
from app.models.third_party import ThirdParty

def seed_database(db: Session):
    # 1. Utilisateurs initiaux (Admin, Contrôleur, Auditeur, Responsable GRC)
    if not db.query(User).filter(User.email == "admin@wetchah.local").first():
        admin = User(
            email="admin@wetchah.local",
            hashed_password=get_password_hash("admin1234"),
            full_name="Administrateur GRC",
            role="admin",
            department="Direction Générale",
            is_active=True
        )
        db.add(admin)

    if not db.query(User).filter(User.email == "controller@wetchah.local").first():
        controller = User(
            email="controller@wetchah.local",
            hashed_password=get_password_hash("controller1234"),
            full_name="Contrôleur de Gestion Principal",
            role="controller",
            department="Contrôle de Gestion & Finance",
            is_active=True
        )
        db.add(controller)

    if not db.query(User).filter(User.email == "auditor@wetchah.local").first():
        auditor = User(
            email="auditor@wetchah.local",
            hashed_password=get_password_hash("auditor1234"),
            full_name="Auditeur Interne Senior",
            role="auditor",
            department="Audit Interne",
            is_active=True
        )
        db.add(auditor)

    db.commit()

    # 2. Référentiels de conformité (ISO 27001, RGPD, SYSCOHADA)
    if not db.query(Framework).filter(Framework.code == "ISO-27001").first():
        iso = Framework(
            code="ISO-27001",
            name="ISO/IEC 27001:2022 — Sécurité de l'Information",
            version="2022",
            category="Sécurité IT & Cybersécurité",
            description="Exigences pour la mise en place d'un SMSI (Système de Management de la Sécurité de l'Information)."
        )
        db.add(iso)
        db.flush()

        reqs = [
            ("A.5.1", "Politiques de sécurité de l'information", "Les politiques doivent être définies, approuvées par la direction et publiées.", "conforme"),
            ("A.8.1", "Inventaire des actifs", "Tous les actifs matériels, logiciels et données doivent être recensés et dotés d'un propriétaire.", "partiellement_conforme"),
            ("A.9.2", "Gestion des accès utilisateurs", "Processus formel d'enregistrement, de modification et de révocation des droits d'accès.", "conforme"),
            ("A.12.1", "Procédures et responsabilités d'exploitation", "Documentation des procédures opérationnelles et sauvegardes régulières.", "partiellement_conforme"),
            ("A.16.1", "Gestion des incidents de sécurité", "Procédure formalisée de signalement et de traitement des événements de sécurité.", "non_conforme"),
        ]
        for clause, title, desc, status in reqs:
            db.add(Requirement(
                framework_id=iso.id,
                clause_number=clause,
                title=title,
                description=desc,
                compliance_status=status
            ))

    if not db.query(Framework).filter(Framework.code == "SYSCOHADA-CI").first():
        sysco = Framework(
            code="SYSCOHADA-CI",
            name="SYSCOHADA Révisé — Contrôle Interne & Procédures Comptables",
            version="2018",
            category="Financier & Comptabilité",
            description="Standards de contrôle interne comptable pour les organisations sous référentiel OHADA."
        )
        db.add(sysco)
        db.flush()

        sysco_reqs = [
            ("CI.01", "Séparation des fonctions incompatibles", "Séparation stricte entre les fonctions de décision, de détention des fonds (caisse) et d'enregistrement comptable.", "conforme"),
            ("CI.02", "Clôture journalière & arrêtés de caisse", "Rapprochement quotidien entre le solde théorique système et les espèces physiques en caisse.", "partiellement_conforme"),
            ("CI.03", "Lettrage des tiers et balance âgée", "Contrôle mensuel des créances clients et dettes fournisseurs avec pointage régulier.", "partiellement_conforme"),
            ("CI.04", "Inventaire physique des stocks", "Procédure périodique de comptage des stocks économat et boutique avec régularisation des écarts.", "conforme"),
        ]
        for clause, title, desc, status in sysco_reqs:
            db.add(Requirement(
                framework_id=sysco.id,
                clause_number=clause,
                title=title,
                description=desc,
                compliance_status=status
            ))

    # 3. Tiers & Fournisseurs (Module 7)
    if not db.query(ThirdParty).first():
        db.add(ThirdParty(
            name="MTN Mobile Money Cameroon",
            category="prestataire_financier",
            criticality="critique",
            contact_name="Support Entreprises MTN",
            contact_email="business@mtn.cm",
            contract_reference="CTR-MTN-2025",
            contract_expiry=datetime.now(timezone.utc) + timedelta(days=365),
            risk_score=2.1,
            status="actif"
        ))
        db.add(ThirdParty(
            name="Société Camerounaise de Blanchisserie (SCB)",
            category="blanchisserie",
            criticality="eleve",
            contact_name="M. Ebondji",
            contact_phone="+237 699 00 11 22",
            contract_reference="CTR-BLANCH-2026",
            contract_expiry=datetime.now(timezone.utc) + timedelta(days=180),
            risk_score=3.4,
            status="actif"
        ))

    # 4. Risques Métier (Module 1)
    if not db.query(Risk).first():
        admin_user = db.query(User).filter(User.role == "admin").first()
        r1 = Risk(
            code="RSK-FIN-001",
            title="Écarts de caisse récurrents en réception et restaurant",
            description="Différences inexpliquées constatées lors des clôtures journalières de caisse entre le comptage physique et le montant théorique PMS.",
            category="financier",
            process_affected="Encaissement & Clôture de caisse",
            gross_impact=4,
            gross_likelihood=4,
            gross_score=16,
            residual_impact=2,
            residual_likelihood=2,
            residual_score=4,
            treatment_strategy="reduire",
            treatment_plan="Mise en place de comptages inopinés hebdomadaires et verrouillage strict des sessions.",
            status="traite",
            owner_id=admin_user.id if admin_user else None
        )
        r2 = Risk(
            code="RSK-OPS-002",
            title="Pertes de stock et coulages à l'économat central",
            description="Écarts entre le stock théorique de matières premières et l'inventaire physique périodique.",
            category="operationnel",
            process_affected="Économat & Approvisionnements",
            gross_impact=3,
            gross_likelihood=4,
            gross_score=12,
            residual_impact=2,
            residual_likelihood=3,
            residual_score=6,
            treatment_strategy="reduire",
            treatment_plan="Double signature des bons de sortie et fiches techniques par type de plat/service.",
            status="en_evaluation",
            owner_id=admin_user.id if admin_user else None
        )
        r3 = Risk(
            code="RSK-CYB-003",
            title="Indisponibilité du serveur PMS ou perte de données locale",
            description="Coupure de courant prolongée ou crash de machine hôte sans reprise immédiate des sauvegardes.",
            category="it_cyber",
            process_affected="Système d'information hôtelier",
            gross_impact=5,
            gross_likelihood=3,
            gross_score=15,
            residual_impact=2,
            residual_likelihood=2,
            residual_score=4,
            treatment_strategy="reduire",
            treatment_plan="Onduleurs online redondants et script de sauvegarde journalière externalisée chiffrée.",
            status="traite",
            owner_id=admin_user.id if admin_user else None
        )
        db.add_all([r1, r2, r3])

    # 5. Contrôles internes (Module 3)
    if not db.query(InternalControl).first():
        ctrl1 = InternalControl(
            code="CTRL-CAISSE-01",
            title="Contrôle inopiné des tiroirs-caisses",
            description="Vérification physique inopinée des espèces en caisse face au solde théorique direct PMS.",
            control_type="financier",
            frequency="hebdomadaire",
            method="manuel",
            status="actif",
            last_test_date=datetime.now(timezone.utc) - timedelta(days=2),
            last_test_result="conforme"
        )
        ctrl2 = InternalControl(
            code="CTRL-SYS-02",
            title="Revue mensuelle des comptes utilisateurs PMS",
            description="Audit des utilisateurs actifs, révocation immédiate des comptes des employés ayant quitté l'hôtel.",
            control_type="informatique",
            frequency="mensuel",
            method="semi_automatise",
            status="actif",
            last_test_date=datetime.now(timezone.utc) - timedelta(days=15),
            last_test_result="conforme"
        )
        db.add_all([ctrl1, ctrl2])

    # 6. Documentation & Politiques (Module 4)
    if not db.query(PolicyDocument).first():
        p1 = PolicyDocument(
            code="POL-GESTION-01",
            title="Procédure générale d'ouverture et de clôture des caisses",
            document_type="procedure",
            current_version="1.1",
            status="publie",
            content="Toute session de caisse doit comporter un fond initial consigné, un contrôle d'identité à chaque décaissement, et un arrêt physique contradictoire en fin de service."
        )
        db.add(p1)

    # 7. Incidents (Module 5)
    if not db.query(Incident).first():
        inc1 = Incident(
            reference="INC-2026-001",
            title="Écart négatif inexpliqué lors du Night Audit du 10/09",
            description="Écart de 12 500 FCFA constaté entre le rapport d'encaissement restaurant et le tiroir physique.",
            incident_type="ecart_caisse",
            severity="significatif",
            status="en_traitement",
            impact_summary="Perte directe de 12 500 FCFA.",
            lessons_learned="Exiger la validation managériale systématique pour tout paiement fractionné en fin de service."
        )
        db.add(inc1)

    # 8. Questionnaire d'évaluation (Module 6)
    if not db.query(Questionnaire).first():
        q1 = Questionnaire(
            title="Auto-évaluation semestrielle du contrôle interne en hébergement",
            description="Questionnaire à destination des chefs de réception et gouvernantes.",
            target_type="interne"
        )
        db.add(q1)
        db.flush()
        db.add_all([
            Question(questionnaire_id=q1.id, order_num=1, section="Caisse & Tarifs", question_text="Les gratuités et remises accordées font-elles l'objet d'une autorisation écrite du manager ?", question_type="yes_no", is_risk_trigger=True),
            Question(questionnaire_id=q1.id, order_num=2, section="Housekeeping", question_text="L'état de propreté des chambres est-il inspecté avant toute remise en disponibilité ?", question_type="yes_no", is_risk_trigger=True),
            Question(questionnaire_id=q1.id, order_num=3, section="Sécurité", question_text="Les clés passe-partout sont-elles remises sous émargement chaque matin ?", question_type="yes_no", is_risk_trigger=True)
        ])

    # 9. Mission d'audit, constats et plan d'action (Module 3)
    #
    # Sans mission initiale, l'écran « Rapports de missions » d'une
    # installation neuve reste vide : la fonction paraît cassée alors qu'elle
    # attend seulement une matière. La mission ci-dessous illustre en outre la
    # chaîne complète mission → constat → plan d'action, dont dépend la
    # génération du rapport PDF.
    if not db.query(AuditMission).first():
        # Les contrôles viennent d'être ajoutés à la session : on force leur
        # écriture pour pouvoir rattacher les constats à leur identifiant.
        db.flush()

        auditeur = db.query(User).filter(User.email == "auditor@wetchah.local").first()
        controleur = db.query(User).filter(User.email == "controller@wetchah.local").first()
        ctrl_caisse = db.query(InternalControl).filter(InternalControl.code == "CTRL-CAISSE-01").first()
        ctrl_sys = db.query(InternalControl).filter(InternalControl.code == "CTRL-SYS-02").first()

        mission = AuditMission(
            reference="AUD-2026-Q3",
            title="Audit du cycle caisse et des accès applicatifs",
            scope="Réception, restaurant et boutique — période du 1er juillet au 30 septembre 2026. "
                  "Revue des sessions de caisse, des écarts constatés et des habilitations PMS.",
            lead_auditor_id=auditeur.id if auditeur else None,
            start_date=datetime.now(timezone.utc) - timedelta(days=45),
            end_date=datetime.now(timezone.utc) - timedelta(days=5),
            status="terminee",
            summary_notes="Le dispositif de caisse est en place et globalement appliqué. "
                          "Deux faiblesses persistent : l'absence de comptage contradictoire "
                          "en fin de service et le maintien de comptes d'anciens employés."
        )
        db.add(mission)
        db.flush()

        constat1 = AuditFinding(
            mission_id=mission.id,
            code="CONST-01",
            title="Comptage de caisse non contradictoire",
            description="Sur les 12 clôtures examinées, 9 ont été réalisées par un agent seul, "
                        "sans contre-comptage ni visa d'un second intervenant.",
            severity="eleve",
            control_id=ctrl_caisse.id if ctrl_caisse else None,
            recommendation="Instaurer un double comptage systématique en fin de service, "
                           "matérialisé par la signature des deux agents sur le bordereau de clôture."
        )
        constat2 = AuditFinding(
            mission_id=mission.id,
            code="CONST-02",
            title="Comptes applicatifs d'employés sortis toujours actifs",
            description="Trois comptes PMS appartenant à des employés ayant quitté l'établissement "
                        "depuis plus de deux mois étaient encore actifs à la date de l'audit.",
            severity="critique",
            control_id=ctrl_sys.id if ctrl_sys else None,
            recommendation="Rattacher la révocation des accès à la procédure de sortie du personnel "
                           "et contrôler mensuellement l'écart entre effectif réel et comptes actifs."
        )
        db.add_all([constat1, constat2])
        db.flush()

        db.add_all([
            ActionPlan(
                finding_id=constat1.id,
                title="Déployer le bordereau de clôture contradictoire",
                description="Rédiger le bordereau, former les chefs de service et rendre la double "
                            "signature obligatoire avant remise des fonds.",
                assignee_id=controleur.id if controleur else None,
                due_date=datetime.now(timezone.utc) + timedelta(days=30),
                status="en_cours"
            ),
            ActionPlan(
                finding_id=constat2.id,
                title="Revue et purge des comptes applicatifs",
                description="Recenser les comptes actifs, les confronter à l'effectif réel, "
                            "désactiver les comptes orphelins et consigner l'opération.",
                assignee_id=controleur.id if controleur else None,
                due_date=datetime.now(timezone.utc) - timedelta(days=3),
                status="en_cours"   # échue : alimente le compteur d'actions en retard
            ),
        ])

    db.commit()
