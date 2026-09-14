from datetime import datetime, timezone
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session

from app.api.deps import get_db, get_current_user, require_roles, record_activity
from app.models.incident import Incident
from app.models.user import User
from app.schemas.incident import IncidentCreate, IncidentUpdate, IncidentOut

router = APIRouter()

@router.get("/", response_model=List[IncidentOut])
def list_incidents(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return db.query(Incident).order_by(Incident.occurred_at.desc()).all()

@router.post("/", response_model=IncidentOut, status_code=status.HTTP_201_CREATED)
def report_incident(
    inc_in: IncidentCreate,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    inc = Incident(**inc_in.model_dump())
    inc.reporter_id = current_user.id
    db.add(inc)
    db.commit()
    db.refresh(inc)
    record_activity(db, current_user, "CREATE", "INCIDENT", str(inc.id), f"Déclaration incident {inc.reference}")
    return inc

@router.put("/{inc_id}", response_model=IncidentOut)
def update_incident(
    inc_id: int,
    inc_in: IncidentUpdate,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(["admin", "risk_manager", "auditor", "controller"]))
):
    inc = db.query(Incident).filter(Incident.id == inc_id).first()
    if not inc:
        raise HTTPException(status_code=404, detail="Incident introuvable.")

    for field, val in inc_in.model_dump(exclude_unset=True).items():
        setattr(inc, field, val)

    if inc_in.status == "clos" and not inc.resolved_at:
        inc.resolved_at = datetime.now(timezone.utc)
        if not inc.lessons_learned:
            raise HTTPException(status_code=400, detail="Le retour d'expérience (REX / Leçons apprises) est obligatoire pour clôturer un incident (exigence INC-04).")

    db.commit()
    db.refresh(inc)
    record_activity(db, current_user, "UPDATE", "INCIDENT", str(inc.id), f"Mise à jour statut: {inc.status}")
    return inc
