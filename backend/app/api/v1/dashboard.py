from datetime import datetime, timezone
from typing import Dict, Any
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_db, get_current_user
from app.models.risk import Risk
from app.models.compliance import Requirement
from app.models.audit import InternalControl, AuditFinding, ActionPlan
from app.models.incident import Incident
from app.models.user import User
from app.schemas.dashboard import DashboardMetrics, TopRiskItem
from app.services.wetchah_app_connector import wetchah_connector

router = APIRouter()

@router.get("/", response_model=DashboardMetrics)
async def get_dashboard_metrics(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Risques
    risks = db.query(Risk).all()
    total_risks = len(risks)
    critical_risks = sum(1 for r in risks if r.residual_score >= 12)
    top_risks = [
        TopRiskItem(
            id=r.id,
            code=r.code,
            title=r.title,
            category=r.category,
            gross_score=r.gross_score,
            residual_score=r.residual_score,
            status=r.status
        )
        for r in sorted(risks, key=lambda x: x.residual_score, reverse=True)[:5]
    ]

    risks_by_cat = {}
    for r in risks:
        risks_by_cat[r.category] = risks_by_cat.get(r.category, 0) + 1

    # Heatmap
    matrix = {}
    for imp in range(1, 6):
        for lik in range(1, 6):
            matrix[f"{imp}_{lik}"] = {"impact": imp, "likelihood": lik, "count": 0}
    for r in risks:
        k = f"{r.residual_impact}_{r.residual_likelihood}"
        if k in matrix:
            matrix[k]["count"] += 1
    heatmap_data = list(matrix.values())

    # Conformité
    reqs = db.query(Requirement).all()
    total_reqs = len(reqs)
    conforme = sum(1 for req in reqs if req.compliance_status == "conforme")
    partiel = sum(1 for req in reqs if req.compliance_status == "partiellement_conforme")
    overall_compliance = round(((conforme + partiel * 0.5) / total_reqs * 100), 1) if total_reqs > 0 else 0.0

    # Contrôles & Audit
    controls = db.query(InternalControl).all()
    active_controls = sum(1 for c in controls if c.status == "actif")
    failed_controls = sum(1 for c in controls if c.last_test_result == "non_conforme")

    open_findings = db.query(AuditFinding).count()

    # Incidents
    open_incidents = db.query(Incident).filter(Incident.status.in_(["declare", "qualifie", "en_traitement"])).count()

    # Plans d'action
    now = datetime.now(timezone.utc)
    action_plans = db.query(ActionPlan).all()
    active_action_plans = sum(1 for p in action_plans if p.status in ["non_debute", "en_cours"])
    delayed_action_plans = sum(
        1 for p in action_plans 
        if p.status in ["non_debute", "en_cours"] and p.due_date and p.due_date.replace(tzinfo=timezone.utc) < now
    )

    # Données financières consommées en direct depuis wetchah_app via API
    financial_data = await wetchah_connector.get_financial_summary()

    return DashboardMetrics(
        total_risks=total_risks,
        critical_risks=critical_risks,
        overall_compliance_rate=overall_compliance,
        active_controls=active_controls,
        failed_controls=failed_controls,
        open_audit_findings=open_findings,
        open_incidents=open_incidents,
        active_action_plans=active_action_plans,
        delayed_action_plans=delayed_action_plans,
        top_risks=top_risks,
        risks_by_category=risks_by_cat,
        heatmap=heatmap_data,
        wetchah_financial_summary=financial_data
    )
