from datetime import datetime, timezone
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session

from app.api.deps import get_db, get_current_user, require_roles, record_activity
from app.models.audit import InternalControl, ControlTest, AuditMission, AuditFinding, ActionPlan
from app.models.user import User
from app.schemas.audit import (
    ControlCreate, ControlOut, ControlTestCreate, ControlTestOut,
    AuditMissionCreate, AuditMissionOut, FindingCreate, FindingOut,
    ActionPlanCreate, ActionPlanUpdate, ActionPlanOut
)

router = APIRouter()

# --- Contrôles Internes ---
@router.get("/controls", response_model=List[ControlOut])
def list_controls(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return db.query(InternalControl).all()

@router.post("/controls", response_model=ControlOut, status_code=status.HTTP_201_CREATED)
def create_control(
    ctrl_in: ControlCreate,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(["admin", "risk_manager", "auditor", "controller"]))
):
    ctrl = InternalControl(**ctrl_in.model_dump())
    db.add(ctrl)
    db.commit()
    db.refresh(ctrl)
    record_activity(db, current_user, "CREATE", "CONTROL", str(ctrl.id), f"Création contrôle {ctrl.code}")
    return ctrl

@router.post("/controls/test", response_model=ControlTestOut)
def record_control_test(
    test_in: ControlTestCreate,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(["admin", "auditor", "controller"]))
):
    ctrl = db.query(InternalControl).filter(InternalControl.id == test_in.control_id).first()
    if not ctrl:
        raise HTTPException(status_code=404, detail="Contrôle introuvable.")

    test = ControlTest(
        control_id=test_in.control_id,
        tester_id=current_user.id,
        result=test_in.result,
        observations=test_in.observations,
        evidence_file=test_in.evidence_file,
        test_date=datetime.now(timezone.utc)
    )
    ctrl.last_test_date = datetime.now(timezone.utc)
    ctrl.last_test_result = test_in.result

    db.add(test)
    db.commit()
    db.refresh(test)
    record_activity(db, current_user, "TEST", "CONTROL", str(ctrl.id), f"Test de contrôle {ctrl.code} : {test.result}")
    return test

# --- Missions d'Audit ---
@router.get("/missions", response_model=List[AuditMissionOut])
def list_missions(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return db.query(AuditMission).all()

@router.post("/missions", response_model=AuditMissionOut, status_code=status.HTTP_201_CREATED)
def create_mission(
    m_in: AuditMissionCreate,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(["admin", "auditor", "controller"]))
):
    m = AuditMission(**m_in.model_dump())
    if not m.lead_auditor_id:
        m.lead_auditor_id = current_user.id
    db.add(m)
    db.commit()
    db.refresh(m)
    record_activity(db, current_user, "CREATE", "AUDIT_MISSION", str(m.id), f"Création mission {m.reference}")
    return m

@router.post("/findings", response_model=FindingOut)
def create_finding(
    f_in: FindingCreate,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(["admin", "auditor", "controller"]))
):
    f = AuditFinding(**f_in.model_dump())
    db.add(f)
    db.commit()
    db.refresh(f)
    record_activity(db, current_user, "CREATE", "AUDIT_FINDING", str(f.id), f"Constat {f.code} : {f.title}")
    return f

# --- Plans d'Action (CAPA) ---
@router.get("/action-plans", response_model=List[ActionPlanOut])
def list_action_plans(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return db.query(ActionPlan).order_by(ActionPlan.due_date.asc()).all()

@router.post("/action-plans", response_model=ActionPlanOut, status_code=status.HTTP_201_CREATED)
def create_action_plan(
    p_in: ActionPlanCreate,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(["admin", "risk_manager", "auditor", "controller"]))
):
    p = ActionPlan(**p_in.model_dump())
    db.add(p)
    db.commit()
    db.refresh(p)
    record_activity(db, current_user, "CREATE", "ACTION_PLAN", str(p.id), f"Plan d'action {p.title}")
    return p

@router.put("/action-plans/{plan_id}", response_model=ActionPlanOut)
def update_action_plan(
    plan_id: int,
    p_in: ActionPlanUpdate,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    plan = db.query(ActionPlan).filter(ActionPlan.id == plan_id).first()
    if not plan:
        raise HTTPException(status_code=404, detail="Plan d'action introuvable.")

    for field, val in p_in.dict(exclude_unset=True).items():
        setattr(plan, field, val)

    if p_in.status in ["realise", "valide"] and not plan.completion_date:
        plan.completion_date = datetime.now(timezone.utc)

    db.commit()
    db.refresh(plan)
    record_activity(db, current_user, "UPDATE", "ACTION_PLAN", str(plan.id), f"Mise à jour statut: {plan.status}")
    return plan
