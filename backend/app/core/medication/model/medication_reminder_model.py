from typing import TYPE_CHECKING, Optional

from sqlalchemy import (
    DateTime,
    Enum,
    ForeignKey,
    Integer,
    String,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.config.database.db import BaseModelClass
from app.core.medication.types.types_medication import ReminderStatus
from app.utils.convert_sqlalchemy_dict import datetime

if TYPE_CHECKING:    
    from app.core.medication.model.medication_model import MedicationModel


class MedicationReminderModel(BaseModelClass):
    __tablename__ = "MEDICATION_REMINDER"

    medication_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("MEDICATION.id"), nullable=False
    )
    scheduled_time: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    actual_reminder_time: Mapped[Optional[datetime]] = mapped_column(
        DateTime, nullable=True
    )
    status: Mapped[ReminderStatus] = mapped_column(
        Enum(ReminderStatus), nullable=False, default=ReminderStatus.PENDING
    )

    # Reminder Settings
    reminder_type: Mapped[str] = mapped_column(
        String(50), nullable=False, default="notification"
    )  # notification, email, sms
    snooze_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    max_snooze_count: Mapped[int] = mapped_column(Integer, nullable=False, default=3)
    snooze_interval_minutes: Mapped[int] = mapped_column(
        Integer, nullable=False, default=10
    )

    # Response tracking
    acknowledged_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    taken_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    missed_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)

    # Relationships
    reminder__medication: Mapped["MedicationModel"] = relationship(
        back_populates="medication__reminders"
    )
