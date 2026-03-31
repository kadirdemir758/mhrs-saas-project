"""
MHRS SaaS — Randevu ORM Modeli
Hastaları doktorlara bağlayan randevu kayıtları.
"""

import enum
from datetime import datetime, timezone

from sqlalchemy import Column, DateTime, Enum, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from app.database import Base


class AppointmentStatus(str, enum.Enum):
    """Randevu durum döngüsü."""

    PENDING = "pending"        # Onay bekliyor
    CONFIRMED = "confirmed"    # Onaylandı
    COMPLETED = "completed"    # Tamamlandı
    CANCELLED = "cancelled"    # İptal edildi
    NO_SHOW = "no_show"        # Hasta gelmedi


class Appointment(Base):
    __tablename__ = "appointments"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)

    # Yabancı Anahtarlar
    patient_id = Column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="Randevu alan hasta (users tablosu)",
    )
    doctor_id = Column(
        Integer,
        ForeignKey("doctors.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
        comment="Randevu verilen doktor",
    )
    clinic_id = Column(
        Integer,
        ForeignKey("clinics.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
        comment="Randevunun gerçekleşeceği klinik",
    )

    # Zaman Bilgisi
    appointment_datetime = Column(
        DateTime(timezone=True),
        nullable=False,
        index=True,
        comment="Randevu tarihi ve saati (UTC)",
    )

    complaint = Column(
        String(500),
        nullable=True,
        comment="Hasta şikayeti",
    )

    # Durum
    status = Column(
        Enum(AppointmentStatus, name="appointment_status_enum"),
        nullable=False,
        default=AppointmentStatus.PENDING,
        index=True,
        comment="Randevu durumu",
    )

    # Denetim Alanları
    created_at = Column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )
    updated_at = Column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    # İlişkiler
    patient = relationship("User", back_populates="appointments")
    doctor = relationship("Doctor", back_populates="appointments")
    clinic = relationship("Clinic", back_populates="appointments")

    def __repr__(self) -> str:
        return (
            f"<Appointment id={self.id} "
            f"patient_id={self.patient_id} "
            f"doctor_id={self.doctor_id} "
            f"at={self.appointment_datetime} "
            f"status={self.status}>"
        )
