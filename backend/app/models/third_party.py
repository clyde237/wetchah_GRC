from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, Float
from app.core.database import Base

class ThirdParty(Base):
    __tablename__ = "third_parties"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    category = Column(String(100), default="fournisseur") # fournisseur, prestataire_it, maintenance, blanchisserie, gardiennage
    criticality = Column(String(50), default="moyen") # faible, moyen, eleve, critique
    contact_name = Column(String(100), nullable=True)
    contact_email = Column(String(100), nullable=True)
    contact_phone = Column(String(50), nullable=True)
    contract_reference = Column(String(100), nullable=True)
    contract_expiry = Column(DateTime, nullable=True)
    risk_score = Column(Float, default=0.0) # Score calculé d'exposition au risque
    status = Column(String(50), default="actif") # actif, en_evaluation, bloque, archive
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
