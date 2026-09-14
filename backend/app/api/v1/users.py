from typing import List
from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session

from app.api.deps import get_db, get_current_user, require_roles, record_activity
from app.core.security import get_password_hash
from app.models.user import User, ActivityLog
from app.schemas.user import UserCreate, UserUpdate, UserOut, ActivityLogOut

router = APIRouter()

@router.get("/", response_model=List[UserOut])
def list_users(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(["admin", "risk_manager", "controller"]))
):
    return db.query(User).all()

@router.post("/", response_model=UserOut, status_code=status.HTTP_201_CREATED)
def create_user(
    user_in: UserCreate,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(["admin"]))
):
    existing = db.query(User).filter(User.email == user_in.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="Un utilisateur avec cet email existe déjà.")
    
    user = User(
        email=user_in.email,
        hashed_password=get_password_hash(user_in.password),
        full_name=user_in.full_name,
        role=user_in.role,
        department=user_in.department,
        phone=user_in.phone,
        is_active=user_in.is_active
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    record_activity(
        db=db,
        user=current_user,
        action="CREATE",
        resource_type="USER",
        resource_id=str(user.id),
        details=f"Création de l'utilisateur {user.email} (rôle: {user.role})",
        ip_address=request.client.host if request.client else None
    )
    return user

@router.get("/logs", response_model=List[ActivityLogOut])
def list_activity_logs(
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(["admin", "risk_manager", "auditor", "controller", "board"]))
):
    return db.query(ActivityLog).order_by(ActivityLog.created_at.desc()).limit(limit).all()
