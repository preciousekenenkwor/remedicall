

from sqlalchemy import Boolean, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.config.database.db import BaseModelClass
from app.core.auth.models.model_token import TokenModel
from app.core.medication.model.medication_model import MedicationModel
from app.core.notification.models.model_notification import NotificationModel


class UserModel(BaseModelClass):
    __tablename__ = "USER"
    first_name: Mapped[str] = mapped_column(String(255), nullable=False)
    last_name: Mapped[str] = mapped_column(String(255), nullable=False)
    email: Mapped[str] = mapped_column(String(255), nullable=False, unique=True)
    password: Mapped[str] = mapped_column(String(255), nullable=False)
    user_type: Mapped[str] = mapped_column(String(255), nullable=False)
    email_verified: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    is_blocked: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)


    user__token: Mapped["TokenModel"] = relationship(back_populates="token__user")
    user__notification: Mapped["NotificationModel"] = relationship(back_populates="notification__user")
    user__medications: Mapped[list["MedicationModel"]] = relationship(
        back_populates="medication__user", cascade="all, delete-orphan"
    )
