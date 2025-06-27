from typing import TYPE_CHECKING, Optional

from sqlalchemy import (
    Boolean,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.config.database.db import BaseModelClass
from app.utils.convert_sqlalchemy_dict import datetime

if TYPE_CHECKING:
    from app.core.medication.model.medication_model import MedicationModel

class MedicationLogModel(BaseModelClass):
    __tablename__ = "MEDICATION_LOG"

    medication_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("MEDICATION.id"), nullable=False
    )
    scheduled_time: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    actual_time: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    status: Mapped[str] = mapped_column(
        String(50), nullable=False
    )  # taken, missed, skipped, late

    # Dosage Information
    dosage_taken: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    dosage_unit: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)

    # Additional Information
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    side_effects_experienced: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    effectiveness_rating: Mapped[Optional[int]] = mapped_column(
        Integer, nullable=True
    )  # 1-5 scale

    # Location and Context
    location_taken: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    with_food: Mapped[Optional[bool]] = mapped_column(Boolean, nullable=True)

    # Relationships
    log__medication: Mapped["MedicationModel"] = relationship(
        back_populates="medication__logs"
    )
