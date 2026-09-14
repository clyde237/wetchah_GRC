from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, ForeignKey, Table
from sqlalchemy.orm import relationship
from app.core.database import Base

class RiskControlLink(Base):
    __tablename__ = "risk_control_links"
    id = Column(Integer, primary_key=True, index=True)
    risk_id = Column(Integer, ForeignKey("risks.id", ondelete="CASCADE"), nullable=False)
    control_id = Column(Integer, ForeignKey("internal_controls.id", ondelete="CASCADE"), nullable=False)
    efficiency = Column(String(50), default="moyen") # fort, moyen, faible

class Risk(Base):
    __tablename__ = "risks"

    id = Column(Integer, primary_key=True, index=True)
    code = Column(String(50), unique=True, index=True, nullable=False) # e.g. RSK-2026-001
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)
    category = Column(String(50), nullable=False, default="operationnel") 
    # operationnel, financier, it_cyber, juridique, strategique
    process_affected = Column(String(100), nullable=True) # Réception, Caisse, Comptabilité, Economat, etc.
    asset_affected = Column(String(100), nullable=True)
    third_party_id = Column(Integer, ForeignKey("third_parties.id", ondelete="SET NULL"), nullable=True)
    owner_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    status = Column(String(50), nullable=False, default="identifie") 
    # identifie, en_evaluation, traite, en_revue, clos
    
    # Évaluation brute (Impact 1-5 x Vraisemblance 1-5)
    gross_impact = Column(Integer, default=3, nullable=False)
    gross_likelihood = Column(Integer, default=3, nullable=False)
    gross_score = Column(Integer, default=9, nullable=False)
    
    # Évaluation résiduelle (après prise en compte des contrôles internes)
    residual_impact = Column(Integer, default=2, nullable=False)
    residual_likelihood = Column(Integer, default=2, nullable=False)
    residual_score = Column(Integer, default=4, nullable=False)
    
    treatment_strategy = Column(String(50), default="reduire") # eviter, reduire, transferer, accepter
    treatment_plan = Column(Text, nullable=True)
    review_frequency_days = Column(Integer, default=90)
    next_review_date = Column(DateTime, nullable=True)
    
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    owner = relationship("User", foreign_keys=[owner_id])
    third_party = relationship("ThirdParty", foreign_keys=[third_party_id])
