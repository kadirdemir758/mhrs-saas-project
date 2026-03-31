"""
MHRS SaaS — Doctor ORM Model
Doctor profiles linked to clinics, synced to Elasticsearch.
"""
from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from app.database import Base


class Doctor(Base):
    __tablename__ = "doctors"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String(150), nullable=False, index=True)
    specialization = Column(String(150), nullable=False, index=True)

    # FK → Clinic
    clinic_id = Column(Integer, ForeignKey("clinics.id"), nullable=False)

    # Professional info
    title = Column(String(50), nullable=True)          # e.g., "Prof. Dr."
    education = Column(Text, nullable=True)
    languages = Column(String(200), nullable=True)     # comma-separated

    # Rating (aggregated from appointments)
    rating = Column(Float, default=0.0)
    total_ratings = Column(Integer, default=0)

    # Working hours (JSON-like string for simplicity)
    working_hours = Column(Text, nullable=True)        # e.g., "Mon-Fri 09:00-17:00"

    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    # Relationships
    clinic = relationship("Clinic", back_populates="doctors")
    appointments = relationship("Appointment", back_populates="doctor", lazy="select")

    def __repr__(self) -> str:
        return f"<Doctor id={self.id} name={self.name} specialization={self.specialization}>"
