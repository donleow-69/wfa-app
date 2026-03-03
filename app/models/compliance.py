"""Employer compliance checklist model."""

from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..database import Base


class ComplianceChecklist(Base):
    __tablename__ = "compliance_checklists"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), nullable=False)
    company_name: Mapped[str] = mapped_column(String(255), default="")
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), onupdate=func.now()
    )

    user = relationship("User", back_populates="checklists")
    items = relationship("ComplianceItem", back_populates="checklist", cascade="all, delete-orphan")


class ComplianceItem(Base):
    __tablename__ = "compliance_items"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    checklist_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("compliance_checklists.id"), nullable=False
    )
    requirement: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str] = mapped_column(Text, default="")
    category: Mapped[str] = mapped_column(String(100), default="general")
    completed: Mapped[bool] = mapped_column(Boolean, default=False)
    due_date: Mapped[str] = mapped_column(String(20), default="")
    notes: Mapped[str] = mapped_column(Text, default="")

    checklist = relationship("ComplianceChecklist", back_populates="items")
