from typing import List
from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session

from app.api.deps import get_db, get_current_user, require_roles, record_activity
from app.models.policy import PolicyDocument, PolicyVersion
from app.models.user import User
from app.schemas.policy import PolicyCreate, PolicyUpdate, PolicyOut

router = APIRouter()

@router.get("/", response_model=List[PolicyOut])
def list_policies(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return db.query(PolicyDocument).all()

@router.post("/", response_model=PolicyOut, status_code=status.HTTP_201_CREATED)
def create_policy(
    p_in: PolicyCreate,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(["admin", "risk_manager"]))
):
    existing = db.query(PolicyDocument).filter(PolicyDocument.code == p_in.code).first()
    if existing:
        raise HTTPException(status_code=400, detail="Ce code de politique existe déjà.")
    p = PolicyDocument(**p_in.model_dump())
    if not p.owner_id:
        p.owner_id = current_user.id
    db.add(p)
    db.commit()
    db.refresh(p)
    record_activity(db, current_user, "CREATE", "POLICY", str(p.id), f"Création politique {p.code}")
    return p
