from datetime import datetime
from typing import TYPE_CHECKING, Optional

from sqlalchemy import Boolean, DateTime, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.config.database.db import BaseModelClass

if TYPE_CHECKING:
    from app.core.user.model.user_model import UserModel

# from modules.auth.model.model import UserModel




# The `NotificationModel` class is a subclass of the `Base` class and inherits from the `Base` class.
# This class likely represents a notification model that inherits from a base class and includes
# timestamp functionality.
class NotificationModel(BaseModelClass):

    __tablename__: str = "NOTIFICATION"

    title: Mapped[str] = mapped_column(String(255), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    notification_type: Mapped[str] = mapped_column(String(50), nullable=False)
    is_read: Mapped[bool] = mapped_column(Boolean, default=False)
    read_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    


    #foreign key
    user_id: Mapped[str] = mapped_column(ForeignKey("USER.id"))

    #relationship
    notification__user: Mapped["UserModel"] = relationship("UserModel", back_populates="user__notification"  )

