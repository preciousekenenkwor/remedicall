from typing import TYPE_CHECKING

from sqlalchemy import (
    Boolean,
    ForeignKey,
    String,
    Text,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.config.database.db import BaseModelClass

if TYPE_CHECKING:
    from app.core.medication.model.medication_model import MedicationModel


class MedicationInteractionModel(BaseModelClass):
    __tablename__ = "MEDICATION_INTERACTION"

    medication1_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("MEDICATION.id"), nullable=False
    )
    medication2_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("MEDICATION.id"), nullable=False
    )
    interaction_type: Mapped[str] = mapped_column(
        String(100), nullable=False
    )  # major, moderate, minor
    description: Mapped[str] = mapped_column(Text, nullable=False)
    severity: Mapped[str] = mapped_column(
        String(50), nullable=False
    )  # high, medium, low
    is_contraindicated: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=False
    )

    # Relationships
    interaction__medication1: Mapped["MedicationModel"] = relationship(
        foreign_keys=[medication1_id]
    )
    interaction__medication2: Mapped["MedicationModel"] = relationship(
        foreign_keys=[medication2_id]
    )
