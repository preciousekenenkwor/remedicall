from sqlalchemy import Column, Integer, String, Boolean, DateTime
from database.database import Base
import datetime

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    full_name = Column(String, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    is_verified = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

class EmailVerification(Base):
    __tablename__ = "email_verifications"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, nullable=False)
    code = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

class PasswordReset(Base):
    __tablename__ = "password_resets"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, nullable=False)
    code = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
