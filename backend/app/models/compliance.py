from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, ForeignKey
from sqlalchemy.orm import relationship
from app.core.database import Base

class Framework(Base):
    __tablename__ = "frameworks"

    id = Column(Integer, primary_key=True, index=True)
    code = Column(String(50), unique=True, index=True, nullable=False) # e.g. ISO-27001, RGPD, SYSCOHADA-CI
    name = Column(String(255), nullable=False)
    version = Column(String(50), default="2022")
    category = Column(String(100), default="Sécurité & Organisation")
    description = Column(Text, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    requirements = relationship("Requirement", back_populates="framework", cascade="all, delete-orphan")

class Requirement(Base):
    __tablename__ = "requirements"

    id = Column(Integer, primary_key=True, index=True)
    framework_id = Column(Integer, ForeignKey("frameworks.id", ondelete="CASCADE"), nullable=False)
    clause_number = Column(String(50), nullable=False) # e.g. A.5.1, Art. 32, C.12
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)
    compliance_status = Column(String(50), default="partiellement_conforme", nullable=False)
    # conforme, partiellement_conforme, non_conforme, non_applicable
    gap_description = Column(Text, nullable=True)
    remediation_plan = Column(Text, nullable=True)
    target_date = Column(DateTime, nullable=True)
    responsible_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    evidence_notes = Column(Text, nullable=True)
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    framework = relationship("Framework", back_populates="requirements")
    responsible = relationship("User", foreign_keys=[responsible_id])
