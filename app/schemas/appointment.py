"""
MHRS SaaS — Randevu Pydantic Şemaları
Gelen verileri doğrular; ORM modeline geçmeden önce tüm kurallar burada kontrol edilir.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.models.appointment import AppointmentStatus


# ---------------------------------------------------------------------------
# İstek (Request) Şemaları
# ---------------------------------------------------------------------------


class SimpleDoctor(BaseModel):
    id: int
    name: str
    title: str
    specialization: str
    class Config:
        from_attributes = True

class SimpleClinic(BaseModel):
    id: int
    name: str
    city: str
    district: str
    class Config:
        from_attributes = True

class AppointmentCreate(BaseModel):
    """Yeni randevu oluşturma isteği için şema."""

    doctor_id: int = Field(..., gt=0, description="Randevu verilecek doktor kimliği")
    clinic_id: Optional[int] = Field(None, gt=0, description="Klinik kimliği (opsiyonel)")
    appointment_datetime: datetime = Field(
        ...,
        description="Randevu tarihi ve saati — timezone-aware ISO 8601 (ör. 2025-06-01T09:15:00Z)",
    )
    complaint: Optional[str] = Field(None, description="Hasta şikayeti")

    # ------------------------------------------------------------------ #
    # Doğrulayıcılar                                                       #
    # ------------------------------------------------------------------ #

    @field_validator("appointment_datetime")
    @classmethod
    def must_be_timezone_aware(cls, v: datetime) -> datetime:
        """Saat dilimi bilgisi zorunludur."""
        if v.tzinfo is None:
            raise ValueError(
                "appointment_datetime timezone-aware olmalıdır. "
                "ISO 8601 formatında Z veya +00:00 ekleyin."
            )
        return v

    @field_validator("appointment_datetime")
    @classmethod
    def must_be_in_future(cls, v: datetime) -> datetime:
        """Randevu geçmiş bir tarihte oluşturulamaz."""
        if v <= datetime.now(timezone.utc):
            raise ValueError("Randevu tarihi gelecekte bir zaman olmalıdır.")
        return v

    @field_validator("appointment_datetime")
    @classmethod
    def must_align_to_15_min_slot(cls, v: datetime) -> datetime:
        """Dakika değeri 0, 15, 30 veya 45 olmalıdır — saniye/mikrosaniye kabul edilmez."""
        if v.minute % 15 != 0:
            raise ValueError(
                "Randevu saati 15 dakikalık katlara uygun olmalıdır "
                "(dakika: 0, 15, 30 veya 45). "
                f"Girilen değer: {v.minute} dakika."
            )
        if v.second != 0 or v.microsecond != 0:
            raise ValueError(
                "appointment_datetime saniye veya mikrosaniye içermemelidir."
            )
        return v


class AppointmentStatusUpdate(BaseModel):
    """Randevu durumu güncelleme isteği için şema."""

    status: AppointmentStatus = Field(..., description="Yeni randevu durumu")


# ---------------------------------------------------------------------------
# Yanıt (Response) Şemaları
# ---------------------------------------------------------------------------


class AppointmentResponse(BaseModel):
    """Tek randevu yanıtı — ORM nesnesinden doğrudan dönüştürülür."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    patient_id: int
    doctor_id: int
    clinic_id: Optional[int]
    appointment_datetime: datetime
    status: AppointmentStatus
    created_at: datetime
    updated_at: datetime
    complaint: Optional[str] = None
    patient_name: Optional[str] = None
    
    # İlişkisel (Joined) verileri dahil et
    doctor: Optional[SimpleDoctor] = None
    clinic: Optional[SimpleClinic] = None

class AppointmentListResponse(BaseModel):
    """Randevu listesi yanıtı."""

    model_config = ConfigDict(from_attributes=True)

    total: int = Field(..., description="Toplam randevu sayısı")
    appointments: list[AppointmentResponse]
