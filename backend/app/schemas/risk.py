from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field

# La matrice de risque est une grille 5x5 : une note hors de cet intervalle
# produit un score aberrant et, surtout, fait disparaître le risque de la
# heatmap — la case correspondante n'existe pas. Le risque reste alors en tête
# du classement sans apparaître nulle part.
def note(defaut):
    """Note de 1 à 5, avec sa valeur par défaut d'origine préservée."""
    return Field(defaut, ge=1, le=5)

class RiskBase(BaseModel):
    code: str
    title: str
    description: str
    category: str = "operationnel"
    process_affected: Optional[str] = None
    asset_affected: Optional[str] = None
    third_party_id: Optional[int] = None
    owner_id: Optional[int] = None
    status: str = "identifie"
    gross_impact: int = note(3)
    gross_likelihood: int = note(3)
    residual_impact: int = note(2)
    residual_likelihood: int = note(2)
    treatment_strategy: str = "reduire"
    treatment_plan: Optional[str] = None
    review_frequency_days: int = 90
    next_review_date: Optional[datetime] = None

class RiskCreate(RiskBase):
    pass

class RiskUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    category: Optional[str] = None
    process_affected: Optional[str] = None
    asset_affected: Optional[str] = None
    third_party_id: Optional[int] = None
    owner_id: Optional[int] = None
    status: Optional[str] = None
    gross_impact: Optional[int] = note(None)
    gross_likelihood: Optional[int] = note(None)
    residual_impact: Optional[int] = note(None)
    residual_likelihood: Optional[int] = note(None)
    treatment_strategy: Optional[str] = None
    treatment_plan: Optional[str] = None
    review_frequency_days: Optional[int] = None
    next_review_date: Optional[datetime] = None

class RiskOut(RiskBase):
    id: int
    gross_score: int
    residual_score: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class HeatmapCell(BaseModel):
    impact: int
    likelihood: int
    count: int
    risk_ids: List[int]
