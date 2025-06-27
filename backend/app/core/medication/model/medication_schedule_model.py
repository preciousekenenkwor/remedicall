
from datetime import time
from typing import TYPE_CHECKING, Optional

from sqlalchemy import (
    Boolean,
    ForeignKey,
    Integer,
    String,
    Time,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.config.database.db import BaseModelClass

if TYPE_CHECKING:
    from app.core.medication.model.medication_model import MedicationModel


class MedicationScheduleModel(BaseModelClass):
    __tablename__ = "MEDICATION_SCHEDULE"

    medication_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("MEDICATION.id"), nullable=False
    )
    time_of_day: Mapped[time] = mapped_column(Time, nullable=False)
    day_of_week: Mapped[Optional[int]] = mapped_column(
        Integer, nullable=True
    )  # 0=Monday, 6=Sunday, None=daily
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)

    # Relationships
    schedule__medication: Mapped["MedicationModel"] = relationship(
        back_populates="medication__schedules"
    )
