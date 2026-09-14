from typing import List
from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session

from app.api.deps import get_db, get_current_user, require_roles, record_activity
from app.models.third_party import ThirdParty
from app.models.user import User
from app.schemas.third_party import ThirdPartyCreate, ThirdPartyUpdate, ThirdPartyOut

router = APIRouter()

@router.get("/", response_model=List[ThirdPartyOut])
def list_third_parties(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return db.query(ThirdParty).all()

@router.post("/", response_model=ThirdPartyOut, status_code=status.HTTP_201_CREATED)
def create_third_party(
    tp_in: ThirdPartyCreate,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(["admin", "risk_manager", "auditor", "controller"]))
):
    tp = ThirdParty(**tp_in.model_dump())
    db.add(tp)
    db.commit()
    db.refresh(tp)
    record_activity(db, current_user, "CREATE", "THIRD_PARTY", str(tp.id), f"Création tiers {tp.name}")
    return tp

@router.put("/{tp_id}", response_model=ThirdPartyOut)
def update_third_party(
    tp_id: int,
    tp_in: ThirdPartyUpdate,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(["admin", "risk_manager", "auditor", "controller"]))
):
    tp = db.query(ThirdParty).filter(ThirdParty.id == tp_id).first()
    if not tp:
        raise HTTPException(status_code=404, detail="Tiers introuvable.")

    for field, val in tp_in.model_dump(exclude_unset=True).items():
        setattr(tp, field, val)

    db.commit()
    db.refresh(tp)
    record_activity(db, current_user, "UPDATE", "THIRD_PARTY", str(tp.id), f"Mise à jour tiers {tp.name}")
    return tp
