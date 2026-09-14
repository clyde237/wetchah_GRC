from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, ForeignKey
from sqlalchemy.orm import relationship
from app.core.database import Base

class PolicyDocument(Base):
    __tablename__ = "policy_documents"

    id = Column(Integer, primary_key=True, index=True)
    code = Column(String(50), unique=True, index=True, nullable=False) # e.g. POL-SEC-01
    title = Column(String(255), nullable=False)
    document_type = Column(String(50), default="politique") # politique, procedure, charte, norme
    current_version = Column(String(20), default="1.0")
    owner_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    status = Column(String(50), default="brouillon") # brouillon, en_revue, approuve, publie, archive
    review_frequency_days = Column(Integer, default=365)
    next_review_date = Column(DateTime, nullable=True)
    content = Column(Text, nullable=True)
    file_url = Column(String(255), nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    owner = relationship("User", foreign_keys=[owner_id])
    versions = relationship("PolicyVersion", back_populates="policy", cascade="all, delete-orphan")
    acknowledgments = relationship("PolicyAcknowledgment", back_populates="policy", cascade="all, delete-orphan")

class PolicyVersion(Base):
    __tablename__ = "policy_versions"

    id = Column(Integer, primary_key=True, index=True)
    policy_id = Column(Integer, ForeignKey("policy_documents.id", ondelete="CASCADE"), nullable=False)
    version_number = Column(String(20), nullable=False)
    change_summary = Column(Text, nullable=False)
    approved_by = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    approved_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    policy = relationship("PolicyDocument", back_populates="versions")

class PolicyAcknowledgment(Base):
    __tablename__ = "policy_acknowledgments"

    id = Column(Integer, primary_key=True, index=True)
    policy_id = Column(Integer, ForeignKey("policy_documents.id", ondelete="CASCADE"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    acknowledged_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    policy = relationship("PolicyDocument", back_populates="acknowledgments")
    user = relationship("User", foreign_keys=[user_id])
