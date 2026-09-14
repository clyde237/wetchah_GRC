from typing import List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session

from app.api.deps import get_db, get_current_user, require_roles, record_activity
from app.models.risk import Risk
from app.models.user import User
from app.schemas.risk import RiskCreate, RiskUpdate, RiskOut

router = APIRouter()

@router.get("/", response_model=List[RiskOut])
def list_risks(
    category: str = None,
    status_filter: str = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    query = db.query(Risk)
    if category:
        query = query.filter(Risk.category == category)
    if status_filter:
        query = query.filter(Risk.status == status_filter)
    return query.order_by(Risk.residual_score.desc()).all()

@router.get("/heatmap")
def get_risk_heatmap(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    risks = db.query(Risk).all()
    # Grille 5x5 (Impact 1..5 x Vraisemblance 1..5)
    matrix = {}
    for imp in range(1, 6):
        for lik in range(1, 6):
            matrix[f"{imp}_{lik}"] = {"impact": imp, "likelihood": lik, "count": 0, "risks": []}

    for r in risks:
        key = f"{r.residual_impact}_{r.residual_likelihood}"
        if key in matrix:
            matrix[key]["count"] += 1
            matrix[key]["risks"].append({
                "id": r.id,
                "code": r.code,
                "title": r.title,
                "score": r.residual_score
            })

    return list(matrix.values())

@router.post("/", response_model=RiskOut, status_code=status.HTTP_201_CREATED)
def create_risk(
    risk_in: RiskCreate,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(["admin", "risk_manager", "auditor", "controller"]))
):
    existing = db.query(Risk).filter(Risk.code == risk_in.code).first()
    if existing:
        raise HTTPException(status_code=400, detail=f"Le code de risque {risk_in.code} existe déjà.")

    gross_score = risk_in.gross_impact * risk_in.gross_likelihood
    residual_score = risk_in.residual_impact * risk_in.residual_likelihood

    risk = Risk(
        **risk_in.model_dump(),
        gross_score=gross_score,
        residual_score=residual_score
    )
    db.add(risk)
    db.commit()
    db.refresh(risk)

    record_activity(
        db=db,
        user=current_user,
        action="CREATE",
        resource_type="RISK",
        resource_id=str(risk.id),
        details=f"Création de la fiche de risque {risk.code} - {risk.title}",
        ip_address=request.client.host if request.client else None
    )
    return risk

@router.get("/{risk_id}", response_model=RiskOut)
def get_risk(
    risk_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    risk = db.query(Risk).filter(Risk.id == risk_id).first()
    if not risk:
        raise HTTPException(status_code=404, detail="Fiche de risque introuvable.")
    return risk

@router.put("/{risk_id}", response_model=RiskOut)
def update_risk(
    risk_id: int,
    risk_in: RiskUpdate,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(["admin", "risk_manager", "auditor", "controller", "risk_owner"]))
):
    risk = db.query(Risk).filter(Risk.id == risk_id).first()
    if not risk:
        raise HTTPException(status_code=404, detail="Fiche de risque introuvable.")

    update_data = risk_in.dict(exclude_unset=True)
    for field, val in update_data.items():
        setattr(risk, field, val)

    risk.gross_score = risk.gross_impact * risk.gross_likelihood
    risk.residual_score = risk.residual_impact * risk.residual_likelihood

    db.commit()
    db.refresh(risk)

    record_activity(
        db=db,
        user=current_user,
        action="UPDATE",
        resource_type="RISK",
        resource_id=str(risk.id),
        details=f"Mise à jour du risque {risk.code}",
        ip_address=request.client.host if request.client else None
    )
    return risk
