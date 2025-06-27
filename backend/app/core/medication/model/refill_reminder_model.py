
from datetime import datetime
from typing import TYPE_CHECKING, Optional

from sqlalchemy import (
    Boolean,
    DateTime,
    ForeignKey,
    Integer,
    String,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.config.database.db import BaseModelClass

if TYPE_CHECKING:
    from app.core.medication.model.medication_model import MedicationModel


class RefillReminderModel(BaseModelClass):
    __tablename__ = "REFILL_REMINDER"

    medication_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("MEDICATION.id"), nullable=False
    )
    reminder_date: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    days_before_empty: Mapped[int] = mapped_column(Integer, nullable=False, default=7)
    is_sent: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    sent_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)

    # Pharmacy Information
    pharmacy_name: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    pharmacy_phone: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    auto_refill_enabled: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=False
    )

    # Relationships
    refill__medication: Mapped["MedicationModel"] = relationship()
