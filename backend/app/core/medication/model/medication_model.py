# app/core/medication/models/medication_model.py
from datetime import datetime
from typing import TYPE_CHECKING, Optional

from sqlalchemy import (
    Boolean,
    DateTime,
    Enum,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.config.database.db import BaseModelClass
from app.core.user.model.user_model import UserModel

if TYPE_CHECKING:
    from app.core.medication.model.medication_log_model import MedicationLogModel
    from app.core.medication.model.medication_reminder_model import (
        MedicationReminderModel,
    )
    from app.core.medication.model.medication_schedule_model import (
        MedicationScheduleModel,
    )
from app.core.medication.types.types_medication import (
        MedicationFrequency,
        MedicationStatus,
    )


class MedicationModel(BaseModelClass):
    __tablename__ = "MEDICATION"

    user_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("USER.id"), nullable=False
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    generic_name: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    strength: Mapped[str] = mapped_column(
        String(100), nullable=False
    )  # e.g., "500mg", "10ml"
    dosage_form: Mapped[str] = mapped_column(
        String(100), nullable=False
    )  # tablet, capsule, liquid, etc.
    manufacturer: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    prescription_number: Mapped[Optional[str]] = mapped_column(
        String(100), nullable=True
    )
    prescribing_doctor: Mapped[Optional[str]] = mapped_column(
        String(255), nullable=True
    )

    # Dosage Information
    dosage_amount: Mapped[float] = mapped_column(
        Float, nullable=False
    )  # Number of units per dose
    dosage_unit: Mapped[str] = mapped_column(
        String(50), nullable=False
    )  # tablet, ml, drops, etc.
    frequency: Mapped[MedicationFrequency] = mapped_column(
        Enum(MedicationFrequency), nullable=False
    )
    custom_frequency_hours: Mapped[Optional[int]] = mapped_column(
        Integer, nullable=True
    )  # For custom frequency

    # Duration and Dates
    start_date: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    end_date: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    duration_days: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)

    # Status and Settings
    status: Mapped[MedicationStatus] = mapped_column(
        Enum(MedicationStatus), nullable=False, default=MedicationStatus.ACTIVE
    )
    is_critical: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    allow_late_taking: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=True
    )
    late_taking_window_minutes: Mapped[int] = mapped_column(
        Integer, nullable=False, default=30
    )

    # Instructions and Notes
    instructions: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    food_instructions: Mapped[Optional[str]] = mapped_column(
        String(255), nullable=True
    )  # with food, without food, etc.
    side_effects: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Storage Information
    storage_location: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    storage_temperature: Mapped[Optional[str]] = mapped_column(
        String(100), nullable=True
    )

    # Inventory
    quantity_remaining: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    total_quantity: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    refill_reminder_threshold: Mapped[Optional[float]] = mapped_column(
        Float, nullable=True
    )

    # Relationships
    medication__user: Mapped["UserModel"] = relationship(
        back_populates="user__medications"
    )
    medication__reminders: Mapped[list["MedicationReminderModel"]] = relationship(
        back_populates="reminder__medication", cascade="all, delete-orphan"
    )
    medication__logs: Mapped[list["MedicationLogModel"]] = relationship(
        back_populates="log__medication", cascade="all, delete-orphan"
    )
    medication__schedules: Mapped[list["MedicationScheduleModel"]] = relationship(
        back_populates="schedule__medication", cascade="all, delete-orphan"
    )

