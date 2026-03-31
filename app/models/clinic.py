"""
MHRS SaaS — Clinic ORM Model
Represents a hospital or medical center with geographic data.
"""
from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, Text
from sqlalchemy.orm import relationship
from app.database import Base


class Clinic(Base):
    __tablename__ = "clinics"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String(200), nullable=False, index=True)

    # Location
    city = Column(String(100), nullable=False, index=True)
    district = Column(String(100), nullable=False)
    address = Column(Text, nullable=True)
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)

    # Specialization tag (e.g., "cardiology", "general")
    clinic_type = Column(String(100), nullable=True, index=True)
    phone = Column(String(20), nullable=True)
    website = Column(String(255), nullable=True)

    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    # Relationships
    doctors = relationship("Doctor", back_populates="clinic", lazy="select")

    def __repr__(self) -> str:
        return f"<Clinic id={self.id} name={self.name} city={self.city}>"
    appointments = relationship("Appointment", back_populates="clinic")