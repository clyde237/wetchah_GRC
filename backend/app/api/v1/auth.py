from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session

from app.api.deps import get_db, get_current_user, record_activity
from app.core.security import verify_password, create_access_token
from app.models.user import User
from app.schemas.auth import LoginRequest, Token
from app.schemas.user import UserOut

router = APIRouter()

@router.post("/login", response_model=Token)
def login(request: Request, login_data: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == login_data.email).first()
    if not user or not verify_password(login_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Identifiants incorrects (email ou mot de passe invalide)",
            headers={"WWW-Authenticate": "Bearer"},
        )
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Compte désactivé. Veuillez contacter un administrateur."
        )

    access_token = create_access_token(subject=user.id)
    record_activity(
        db=db,
        user=user,
        action="LOGIN",
        resource_type="AUTH",
        resource_id=str(user.id),
        details=f"Connexion réussie ({user.role})",
        ip_address=request.client.host if request.client else None
    )
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": user
    }

@router.get("/me", response_model=UserOut)
def get_me(current_user: User = Depends(get_current_user)):
    return current_user
