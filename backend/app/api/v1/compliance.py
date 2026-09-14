from typing import List
from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session

from app.api.deps import get_db, get_current_user, require_roles, record_activity
from app.models.compliance import Framework, Requirement
from app.models.user import User
from app.schemas.compliance import FrameworkCreate, FrameworkOut, RequirementUpdate, RequirementOut

router = APIRouter()

@router.get("/frameworks", response_model=List[FrameworkOut])
def list_frameworks(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    frameworks = db.query(Framework).all()
    results = []
    for fw in frameworks:
        reqs = fw.requirements
        total = len(reqs)
        conforme = sum(1 for r in reqs if r.compliance_status == "conforme")
        partiel = sum(1 for r in reqs if r.compliance_status == "partiellement_conforme")
        rate = round(((conforme * 1.0 + partiel * 0.5) / total * 100), 1) if total > 0 else 0.0
        
        fw_out = FrameworkOut.from_orm(fw)
        fw_out.compliance_rate = rate
        results.append(fw_out)
    return results

@router.get("/requirements", response_model=List[RequirementOut])
def list_requirements(
    framework_id: int = None,
    status_filter: str = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    query = db.query(Requirement)
    if framework_id:
        query = query.filter(Requirement.framework_id == framework_id)
    if status_filter:
        query = query.filter(Requirement.compliance_status == status_filter)
    return query.all()

@router.put("/requirements/{req_id}", response_model=RequirementOut)
def update_requirement(
    req_id: int,
    req_in: RequirementUpdate,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(["admin", "risk_manager", "auditor", "controller"]))
):
    req = db.query(Requirement).filter(Requirement.id == req_id).first()
    if not req:
        raise HTTPException(status_code=404, detail="Exigence introuvable.")

    update_data = req_in.dict(exclude_unset=True)
    for field, val in update_data.items():
        setattr(req, field, val)

    db.commit()
    db.refresh(req)

    record_activity(
        db=db,
        user=current_user,
        action="UPDATE",
        resource_type="COMPLIANCE",
        resource_id=str(req.id),
        details=f"Mise à jour exigence {req.clause_number} (statut: {req.compliance_status})",
        ip_address=request.client.host if request.client else None
    )
    return req
