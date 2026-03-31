"""
MHRS SaaS — Randevu CRUD İşlemleri

İş Kuralları:
    1. Randevu saati 15 dakikalık katlara uygun olmalıdır (şema katmanında da kontrol edilir).
    2. Aynı doktorun aynı slotunda çift randevu (double-booking) oluşturulamaz.
    3. Hasta ve doktor varlığı doğrulanır; bulunamazsa 404 döner.
"""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import List, Optional

from fastapi import HTTPException, status
from sqlalchemy import and_
from sqlalchemy.orm import Session

from app.models.appointment import Appointment, AppointmentStatus
from app.schemas.appointment import AppointmentCreate, AppointmentStatusUpdate

# Randevu süresi — 15 dakika sabittir.
SLOT_DURATION_MINUTES: int = 15


# ---------------------------------------------------------------------------
# Yardımcı
# ---------------------------------------------------------------------------


def _slot_end(dt: datetime) -> datetime:
    """Bir slotun bitiş zamanını hesaplar."""
    return dt + timedelta(minutes=SLOT_DURATION_MINUTES)


def _check_doctor_exists(db: Session, doctor_id: int) -> None:
    """Doktor tablosunda kayıt yoksa 404 fırlatır."""
    # Lazy import — circular dependency'den kaçınmak için
    from app.models.doctor import Doctor  # noqa: PLC0415

    doctor = db.get(Doctor, doctor_id)
    if not doctor:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Doktor bulunamadı (id={doctor_id}).",
        )


def _check_patient_exists(db: Session, patient_id: int) -> None:
    """Kullanıcı/hasta tablosunda kayıt yoksa 404 fırlatır."""
    from app.models.user import User  # noqa: PLC0415

    user = db.get(User, patient_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Hasta bulunamadı (id={patient_id}).",
        )


def _check_double_booking(
    db: Session,
    doctor_id: int,
    appointment_datetime: datetime,
    exclude_appointment_id: Optional[int] = None,
) -> None:
    """
    Aynı doktorun istenen zaman slotunda aktif bir randevusu varsa
    HTTP 409 Conflict hatası fırlatır.

    Bir slot meşgul sayılır eğer:
        mevcut randevu zamanı == istenen slot zamanı
    (Her slot tam olarak 15 dakika olduğundan başlangıç zamanı karşılaştırması yeterlidir.)
    """
    query = db.query(Appointment).filter(
        and_(
            Appointment.doctor_id == doctor_id,
            Appointment.appointment_datetime == appointment_datetime,
            Appointment.status.notin_(
                [AppointmentStatus.CANCELLED]
            ),
        )
    )

    if exclude_appointment_id is not None:
        query = query.filter(Appointment.id != exclude_appointment_id)

    conflict = query.first()
    if conflict:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Bu randevu saati maalesef az önce doldu."
        )


# ---------------------------------------------------------------------------
# CRUD Fonksiyonları
# ---------------------------------------------------------------------------


def create_appointment(
    db: Session,
    payload: AppointmentCreate,
    patient_id: int,
) -> Appointment:
    """
    Yeni randevu oluşturur.

    Kontroller (sırayla):
        1. Hasta mevcut mu?
        2. Doktor mevcut mu?
        3. Randevu saati 15 dakikalık kata uygun mu?  ← Pydantic'te de kontrol edilir.
        4. Double-booking: doktorun o slotunda başka randevu var mı?

    Args:
        db:         SQLAlchemy oturumu.
        payload:    İstemciden gelen doğrulanmış veri (AppointmentCreate).
        patient_id: Oturum açmış hastanın kimliği (JWT'den alınır).

    Returns:
        Kaydedilmiş Appointment ORM nesnesi.

    Raises:
        HTTPException 404: Hasta veya doktor bulunamadı.
        HTTPException 422: 15 dakikalık slota uygun değil.
        HTTPException 409: Double-booking tespit edildi.
    """
    # 1. Hasta varlık kontrolü
    _check_patient_exists(db, patient_id)

    # 2. Doktor varlık kontrolü
    _check_doctor_exists(db, payload.doctor_id)

    # 3. 15 dakikalık slot kontrolü (Pydantic garantiler ama yine de savunma katmanı)
    dt = payload.appointment_datetime
    if dt.minute % 15 != 0 or dt.second != 0 or dt.microsecond != 0:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=(
                "Randevu saati 15 dakikalık katlara uygun olmalıdır "
                "(dakika: 0, 15, 30 veya 45). Saniye veya mikrosaniye olamaz."
            ),
        )

    # 4. Double-booking koruması
    _check_double_booking(db, payload.doctor_id, payload.appointment_datetime)

    # Kayıt oluştur
    appointment = Appointment(
        patient_id=patient_id,
        doctor_id=payload.doctor_id,
        clinic_id=payload.clinic_id,
        appointment_datetime=payload.appointment_datetime,
        complaint=payload.complaint,
        status=AppointmentStatus.PENDING,
    )
    db.add(appointment)
    db.commit()
    db.refresh(appointment)
    return appointment


def get_appointment_by_id(db: Session, appointment_id: int) -> Appointment:
    """
    ID'ye göre tek randevu getirir. Bulunamazsa 404 fırlatır.
    """
    appointment = db.get(Appointment, appointment_id)
    if not appointment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Randevu bulunamadı (id={appointment_id}).",
        )
    return appointment


def get_appointments_by_patient(
    db: Session,
    patient_id: int,
    skip: int = 0,
    limit: int = 20,
    status_filter: Optional[AppointmentStatus] = None,
) -> List[Appointment]:
    """
    Belirli bir hastanın randevularını sayfalı olarak getirir.

    Args:
        db:            SQLAlchemy oturumu.
        patient_id:    Hastanın kimliği.
        skip:          Atlanacak kayıt sayısı (sayfalama).
        limit:         Maksimum dönen kayıt sayısı (max 100).
        status_filter: Opsiyonel durum filtresi.

    Returns:
        Appointment listesi.
    """
    limit = min(limit, 100)  # Güvenlik sınırı

    query = db.query(Appointment).filter(Appointment.patient_id == patient_id)

    if status_filter is not None:
        query = query.filter(Appointment.status == status_filter)

    return (
        query
        .order_by(Appointment.appointment_datetime.asc())
        .offset(skip)
        .limit(limit)
        .all()
    )


def get_appointments_by_doctor(
    db: Session,
    doctor_id: int,
    skip: int = 0,
    limit: int = 20,
    status_filter: Optional[AppointmentStatus] = None,
) -> List[Appointment]:
    """
    Belirli bir doktorun randevularını sayfalı olarak getirir.
    """
    limit = min(limit, 100)

    query = db.query(Appointment).filter(Appointment.doctor_id == doctor_id)

    if status_filter is not None:
        query = query.filter(Appointment.status == status_filter)

    return (
        query
        .order_by(Appointment.appointment_datetime.asc())
        .offset(skip)
        .limit(limit)
        .all()
    )


def update_appointment_status(
    db: Session,
    appointment_id: int,
    payload: AppointmentStatusUpdate,
) -> Appointment:
    """
    Randevu durumunu günceller.

    Raises:
        HTTPException 404: Randevu bulunamadı.
        HTTPException 409: Zaten iptal edilmiş randevu güncellenemez.
    """
    appointment = get_appointment_by_id(db, appointment_id)

    if appointment.status == AppointmentStatus.CANCELLED:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="İptal edilmiş bir randevunun durumu değiştirilemez.",
        )

    appointment.status = payload.status
    appointment.updated_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(appointment)
    return appointment


def update_appointment_status_by_doctor(
    db: Session,
    appointment_id: int,
    doctor_id: int,
    new_status: AppointmentStatus,
) -> Appointment:
    """
    Doktorun kendisine ait randevunun durumunu (tamamlandı/gelmedi) güncellemesini sağlar.
    """
    appointment = get_appointment_by_id(db, appointment_id)

    if appointment.doctor_id != doctor_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Bu randevuyu güncelleme yetkiniz yok.",
        )

    if appointment.status == AppointmentStatus.CANCELLED:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="İptal edilmiş bir randevunun durumu değiştirilemez.",
        )

    appointment.status = new_status
    appointment.updated_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(appointment)
    return appointment


def cancel_appointment(db: Session, appointment_id: int, patient_id: int) -> Appointment:
    """
    Hastanın kendi randevusunu iptal eder.

    Raises:
        HTTPException 403: Randevu bu hastaya ait değil.
        HTTPException 409: Tamamlanmış randevu iptal edilemez.
    """
    appointment = get_appointment_by_id(db, appointment_id)

    if appointment.patient_id != patient_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Bu randevuyu iptal etme yetkiniz yok.",
        )

    if appointment.status == AppointmentStatus.COMPLETED:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Tamamlanmış randevu iptal edilemez.",
        )

    appointment.status = AppointmentStatus.CANCELLED
    appointment.updated_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(appointment)
    return appointment
