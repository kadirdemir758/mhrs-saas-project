"""
MHRS SaaS — User ORM Model
Stores patient/admin account data. TC number is stored encrypted.
"""
import random
from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Enum, LargeBinary
from sqlalchemy.orm import relationship
from app.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)

    # Identity — TC No encrypted at rest via encryption_utils.py
    tc_no_encrypted = Column(LargeBinary, unique=True, nullable=False)
    name = Column(String(100), nullable=False)
    email = Column(String(150), unique=True, index=True, nullable=False)
    phone = Column(String(20), nullable=True)

    # Location
    city = Column(String(100), nullable=True)
    district = Column(String(100), nullable=True)

    # Auth
    hashed_password = Column(String(255), nullable=False)
    role = Column(Enum("patient", "doctor", "admin", name="user_role"), default="patient")

    # Email verification
    is_verified = Column(Boolean, default=False)
    verification_code = Column(String(6), nullable=True)
    verification_expires_at = Column(DateTime(timezone=True), nullable=True)

    # Password Reset
    reset_code = Column(String(6), nullable=True)

    # Metadata
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    # Relationships
    appointments = relationship("Appointment", back_populates="patient", lazy="select")

    @staticmethod
    def generate_verification_code() -> str:
        """Returns a random 6-digit string code."""
        return str(random.randint(100000, 999999))

    def __repr__(self) -> str:
        return f"<User id={self.id} email={self.email} role={self.role}>"
