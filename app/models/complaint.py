"""Complaint filing model."""

from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..database import Base


class Complaint(Base):
    __tablename__ = "complaints"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), nullable=False)
    status: Mapped[str] = mapped_column(
        String(30), default="draft"
    )  # draft | submitted | under_review | resolved | closed
    category: Mapped[str] = mapped_column(
        String(100), nullable=False
    )  # discrimination, retaliation, wage_theft, harassment, safety, other
    description: Mapped[str] = mapped_column(Text, nullable=False)
    employer_name: Mapped[str] = mapped_column(String(255), default="")
    incident_date: Mapped[str] = mapped_column(String(20), default="")
    desired_outcome: Mapped[str] = mapped_column(Text, default="")
    supporting_details: Mapped[str] = mapped_column(Text, default="")
    authority_name: Mapped[str] = mapped_column(String(255), default="")
    authority_email: Mapped[str] = mapped_column(String(255), default="")
    authority_portal_url: Mapped[str] = mapped_column(String(512), default="")
    email_sent: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), onupdate=func.now()
    )

    user = relationship("User", back_populates="complaints")
