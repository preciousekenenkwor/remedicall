from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class NotificationTemplate:
    id: int
    template_for: str
    email_body: str
    sms_body: str
    whatsapp_body: str
    auto_send_email: bool
    auto_send_whatsapp: bool
    subject: str
    auto_send_sms:bool
    auto_send: bool
    created_at: str
    updated_at: str

