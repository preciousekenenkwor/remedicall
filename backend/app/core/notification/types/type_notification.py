from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class Notification:
    id: str  # Assuming UUID
    type: str
    notifiable_type: str
    notifiable_id: int
    data: str
    read_at: Optional[datetime]
    cc:str
    bcc:str
    created_at: datetime
    updated_at: datetime




from datetime import datetime
from enum import Enum

from pydantic import BaseModel


class NotificationTypeE(str, Enum):
    TEXT = "TEXT"
    MIXED = "MIXED"
    IMAGE = "IMAGE"


class NotificationSchema(BaseModel):
    id: str
    sub_message_type: NotificationTypeE

    USER: str
    message: str
    SENDER: str
    RECEIVER: str
    is_read: bool
    created_at: datetime
    updated_at: datetime
    deleted_at: datetime

    class Config:
        orm_mode = True
