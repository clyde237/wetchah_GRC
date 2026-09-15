from datetime import datetime, timedelta, timezone
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session

from app.api.deps import get_db, get_current_user, require_roles, record_activity
from app.models.policy import PolicyDocument, PolicyVersion, PolicyAcknowledgment
from app.models.user import User
from app.schemas.policy import (
    PolicyCreate, PolicyUpdate, PolicyOut, PolicyDetailOut,
    PolicyVersionCreate, PolicyVersionOut, PolicyAcknowledgmentOut,
)

router = APIRouter()

# Cycle de vie documentaire (POL-02). Une politique ne saute pas d'étape :
# un document ne passe pas de brouillon à publié sans revue ni approbation,
# sinon la trace d'approbation ne vaut rien devant un auditeur externe.
TRANSITIONS = {
    "brouillon": ["en_revue"],
    "en_revue":  ["approuve", "brouillon"],
    "approuve":  ["publie", "en_revue"],
    "publie":    ["archive", "en_revue"],
    "archive":   ["brouillon"],
}

# Rédiger et approuver sont deux actes distincts : le second engage.
ROLES_REDACTION = ["admin", "risk_manager", "controller"]
ROLES_APPROBATION = ["admin", "risk_manager"]


def _with_counts(policy: PolicyDocument, schema=PolicyOut):
    out = schema.model_validate(policy)
    out.version_count = len(policy.versions)
    out.acknowledgment_count = len(policy.acknowledgments)
    return out


def _get_or_404(db: Session, policy_id: int) -> PolicyDocument:
    policy = db.query(PolicyDocument).filter(PolicyDocument.id == policy_id).first()
    if not policy:
        raise HTTPException(status_code=404, detail="Politique introuvable.")
    return policy


@router.get("/", response_model=List[PolicyOut])
def list_policies(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return [_with_counts(p) for p in db.query(PolicyDocument).all()]


@router.post("/", response_model=PolicyOut, status_code=status.HTTP_201_CREATED)
def create_policy(
    p_in: PolicyCreate,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(ROLES_REDACTION))
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
    return _with_counts(p)


@router.get("/{policy_id}", response_model=PolicyDetailOut)
def get_policy(
    policy_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Fiche complète : historique des versions et étapes de cycle ouvertes."""
    policy = _get_or_404(db, policy_id)

    detail = _with_counts(policy, PolicyDetailOut)
    detail.versions = [
        PolicyVersionOut.model_validate(v)
        for v in sorted(policy.versions, key=lambda v: v.created_at, reverse=True)
    ]
    detail.acknowledged_by_me = any(a.user_id == current_user.id for a in policy.acknowledgments)
    detail.allowed_transitions = TRANSITIONS.get(policy.status, [])
    return detail


@router.put("/{policy_id}", response_model=PolicyOut)
def update_policy(
    policy_id: int,
    p_in: PolicyUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(ROLES_REDACTION))
):
    """
    Met à jour une politique. Un changement de statut doit suivre le cycle
    défini par TRANSITIONS ; approuver ou publier réclame en outre un rôle
    habilité.
    """
    policy = _get_or_404(db, policy_id)
    changes = p_in.model_dump(exclude_unset=True)

    new_status = changes.pop("status", None)
    if new_status and new_status != policy.status:
        allowed = TRANSITIONS.get(policy.status, [])
        if new_status not in allowed:
            raise HTTPException(
                status_code=400,
                detail=(
                    f"Passage de « {policy.status} » à « {new_status} » non permis. "
                    f"Étapes possibles : {', '.join(allowed) or 'aucune'}."
                ),
            )
        if new_status in ("approuve", "publie") and current_user.role not in ROLES_APPROBATION:
            raise HTTPException(
                status_code=403,
                detail="Approuver ou publier une politique demande un rôle habilité.",
            )

        # Publier fait courir le délai de revue : sans cela next_review_date
        # reste vide et l'échéance n'est jamais suivie.
        if new_status == "publie" and not policy.next_review_date:
            policy.next_review_date = datetime.now(timezone.utc) + timedelta(
                days=policy.review_frequency_days or 365
            )

        policy.status = new_status
        record_activity(
            db, current_user, "STATUS", "POLICY", str(policy.id),
            f"Politique {policy.code} passée en « {new_status} »"
        )

    for field, value in changes.items():
        setattr(policy, field, value)

    db.commit()
    db.refresh(policy)
    return _with_counts(policy)


@router.get("/{policy_id}/versions", response_model=List[PolicyVersionOut])
def list_versions(
    policy_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    policy = _get_or_404(db, policy_id)
    return sorted(policy.versions, key=lambda v: v.created_at, reverse=True)


@router.post("/{policy_id}/versions", response_model=PolicyVersionOut, status_code=status.HTTP_201_CREATED)
def create_version(
    policy_id: int,
    v_in: PolicyVersionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(ROLES_REDACTION))
):
    """
    Fige une nouvelle version : le numéro devient la version courante et le
    résumé des modifications constitue la trace exigée lors d'une revue.

    Une nouvelle version rouvre le cycle — un texte modifié après publication
    n'est plus le texte approuvé, et les accusés de lecture recueillis sur
    l'ancienne version ne valent plus pour la nouvelle.
    """
    policy = _get_or_404(db, policy_id)

    if any(v.version_number == v_in.version_number for v in policy.versions):
        raise HTTPException(
            status_code=400,
            detail=f"La version « {v_in.version_number} » existe déjà pour cette politique.",
        )

    if v_in.approve and current_user.role not in ROLES_APPROBATION:
        raise HTTPException(
            status_code=403,
            detail="Approuver une version demande un rôle habilité.",
        )

    version = PolicyVersion(
        policy_id=policy.id,
        version_number=v_in.version_number,
        change_summary=v_in.change_summary,
    )
    if v_in.approve:
        version.approved_by = current_user.id
        version.approved_at = datetime.now(timezone.utc)

    policy.current_version = v_in.version_number
    policy.status = "approuve" if v_in.approve else "en_revue"

    db.add(version)
    db.commit()
    db.refresh(version)

    record_activity(
        db, current_user, "VERSION", "POLICY", str(policy.id),
        f"Politique {policy.code} — version {v_in.version_number}"
        + (" approuvée" if v_in.approve else " soumise à revue")
    )
    return version


@router.post("/{policy_id}/acknowledge", response_model=PolicyAcknowledgmentOut, status_code=status.HTTP_201_CREATED)
def acknowledge_policy(
    policy_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Accusé de lecture (POL-05). Réservé aux politiques publiées : on
    n'accuse pas réception d'un brouillon susceptible de changer.
    Idempotent — un second appel renvoie l'accusé déjà enregistré plutôt
    que d'en empiler un nouveau.
    """
    policy = _get_or_404(db, policy_id)

    if policy.status != "publie":
        raise HTTPException(
            status_code=400,
            detail="Seule une politique publiée peut faire l'objet d'un accusé de lecture.",
        )

    existing = db.query(PolicyAcknowledgment).filter(
        PolicyAcknowledgment.policy_id == policy.id,
        PolicyAcknowledgment.user_id == current_user.id,
    ).first()
    if existing:
        return PolicyAcknowledgmentOut(
            id=existing.id,
            user_id=existing.user_id,
            user_name=current_user.full_name,
            acknowledged_at=existing.acknowledged_at,
        )

    ack = PolicyAcknowledgment(policy_id=policy.id, user_id=current_user.id)
    db.add(ack)
    db.commit()
    db.refresh(ack)

    record_activity(
        db, current_user, "ACKNOWLEDGE", "POLICY", str(policy.id),
        f"Accusé de lecture de la politique {policy.code} (v{policy.current_version})"
    )
    return PolicyAcknowledgmentOut(
        id=ack.id,
        user_id=ack.user_id,
        user_name=current_user.full_name,
        acknowledged_at=ack.acknowledged_at,
    )


@router.get("/{policy_id}/acknowledgments", response_model=List[PolicyAcknowledgmentOut])
def list_acknowledgments(
    policy_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(ROLES_REDACTION + ["auditor"]))
):
    """Qui a accusé réception — la pièce attendue lors d'un audit de diffusion."""
    policy = _get_or_404(db, policy_id)
    return [
        PolicyAcknowledgmentOut(
            id=a.id,
            user_id=a.user_id,
            user_name=a.user.full_name if a.user else None,
            acknowledged_at=a.acknowledged_at,
        )
        for a in sorted(policy.acknowledgments, key=lambda a: a.acknowledged_at, reverse=True)
    ]
