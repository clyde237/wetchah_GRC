from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from app.api.deps import get_db, get_current_user
from app.models.audit import AuditMission, AuditFinding, ActionPlan
from app.models.risk import Risk
from app.models.user import User
from app.services.report_service import GrcReportService

router = APIRouter()

@router.get("/missions/{mission_id}/pdf")
def download_audit_mission_pdf(
    mission_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    mission = db.query(AuditMission).filter(AuditMission.id == mission_id).first()
    if not mission:
        raise HTTPException(status_code=404, detail="Mission d'audit introuvable.")

    findings = mission.findings
    action_plans = []
    for f in findings:
        action_plans.extend(f.action_plans)

    pdf_stream = GrcReportService.generate_audit_mission_pdf(mission, findings, action_plans)
    filename = f"RAPPORT_AUDIT_{mission.reference}.pdf"
    
    return StreamingResponse(
        pdf_stream,
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )

@router.get("/risks/excel")
def download_risks_excel(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    risks = db.query(Risk).all()
    excel_stream = GrcReportService.generate_risks_excel(risks)
    filename = "REGISTRE_RISQUES_WETCHAH_GRC.xlsx"

    return StreamingResponse(
        excel_stream,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )
