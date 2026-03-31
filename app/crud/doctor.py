"""
MHRS SaaS — Doktor CRUD İşlemleri
"""
from typing import List, Optional, Tuple
from sqlalchemy import or_
from sqlalchemy.orm import Session
from app.models.doctor import Doctor
from app.schemas.doctor import DoctorCreate


def create_doctor(db: Session, payload: DoctorCreate) -> Doctor:
    """
    Yeni bir doktor profili oluşturur.
    ES senkronizasyonu ORM event listener (es_events.py) üzerinden otomatik çalışır.
    """
    db_doctor = Doctor(
        name=payload.name,
        specialization=payload.specialization,
        clinic_id=payload.clinic_id,
        title=payload.title,
        languages=payload.languages,
        working_hours=payload.working_hours,
        is_active=True
    )
    db.add(db_doctor)
    db.commit()
    db.refresh(db_doctor)
    return db_doctor


def get_doctors(
    db: Session,
    skip: int = 0,
    limit: int = 20,
    clinic_id: Optional[int] = None,
    specialization: Optional[str] = None,
    search: Optional[str] = None
) -> Tuple[int, List[Doctor]]:
    """
    Doktorları listeler (Arama, filtrelere, sayfalama ve toplam sayıma sahip).
    """
    query = db.query(Doctor).filter(Doctor.is_active == True)
    
    if clinic_id:
        query = query.filter(Doctor.clinic_id == clinic_id)
        
    if specialization:
        query = query.filter(Doctor.specialization.ilike(f"%{specialization}%"))
        
    if search:
        query = query.filter(
            or_(
                Doctor.name.ilike(f"%{search}%"),
                Doctor.specialization.ilike(f"%{search}%")
            )
        )
        
    total_count = query.count()
    doctors = query.order_by(Doctor.id).offset(skip).limit(limit).all()
    
    return total_count, doctors


def get_doctor_by_id(db: Session, doctor_id: int) -> Optional[Doctor]:
    """
    Belirli bir doktoru ID'ye göre getirir.
    """
    return db.query(Doctor).filter(Doctor.id == doctor_id, Doctor.is_active == True).first()
