"""
MHRS SaaS — Admin İstatistikleri Router'ı
"""
from datetime import date
from typing import List, Dict, Any
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.database import get_db
from app.models.doctor import Doctor
from app.models.user import User  # Hastalar users tablosunda tutuluyor
from app.models.appointment import Appointment
from app.models.clinic import Clinic
from app.schemas.appointment import AppointmentResponse
from app.schemas.doctor import AdminDoctorCreate
from security.auth import require_role, hash_password
from security.encryption_utils import encrypt_field
from fastapi import HTTPException
import random

# İsterseniz '_admin = Depends(require_role("admin"))' ile 
# tüm bu router'ı yetki kalkanıyla koruma altına alabilirsiniz.
router = APIRouter(
    tags=["Admin & Statistics"],
    dependencies=[Depends(require_role("admin"))]
)

@router.get("/stats/summary", summary="Genel sistem özetini getirir")
def get_system_summary(db: Session = Depends(get_db)):
    """
    Toplam doktor, kayıtlı hasta (kullanıcı) ve alınan randevu sayılarını döndürür.
    """
    # Eger kullanicilar arasi yalnizca 'patient' olanlari saymak istersen .filter(User.role == 'patient') ekleyebilirsin
    total_doctors = db.query(func.count(Doctor.id)).scalar() or 0
    total_patients = db.query(func.count(User.id)).scalar() or 0
    total_appointments = db.query(func.count(Appointment.id)).scalar() or 0
    
    return {
        "total_doctors": total_doctors,
        "total_patients": total_patients,
        "total_appointments": total_appointments
    }


@router.get("/appointments", response_model=List[AppointmentResponse], summary="Sistemdeki tüm randevuları listeler")
def get_all_appointments(db: Session = Depends(get_db)):
    """
    Sistemdeki TİÜM randevuları User (Hasta) ve Doctor (Doktor) tablolarıyla JOIN'leyip isimleriyle listeler.
    """
    results = (
        db.query(Appointment, User.name.label("patient_name"), Doctor.name.label("doctor_name"))
        .join(User, Appointment.patient_id == User.id)
        .join(Doctor, Appointment.doctor_id == Doctor.id)
        .all()
    )
    
    out = []
    for appt, pat_name, doc_name in results:
        appt.patient_name = pat_name
        # Şemada doktor ilişkisi SimpleDoctor bekleyebilir ya da sadece üstte doctor_name dönebiliriz.
        # Biz doğrudan schema ile uyumlu olsun diye objeye atıyoruz
        setattr(appt, "assoc_doctor_name", doc_name)
        # Eger AppointmentResponse'da doğrudan 'doctor_name' isteniyorsa:
        if not appt.doctor:
            from app.schemas.appointment import SimpleDoctor
            appt.doctor = SimpleDoctor(id=appt.doctor_id, name=doc_name, title="", specialization="")
        else:
            appt.doctor.name = doc_name
        out.append(appt)
        
    return out

@router.get("/stats/popular-clinics", summary="En çok randevu alan 3 kliniği getirir")
def get_popular_clinics(db: Session = Depends(get_db)):
    """
    Klinikleri toplam randevu sayısına göre büyükten küçüğe sıralar ve ilk 3'ünü döner.
    """
    results = (
        db.query(Clinic.name, func.count(Appointment.id).label("appointment_count"))
        .join(Appointment, Clinic.id == Appointment.clinic_id)
        .group_by(Clinic.id)
        .order_by(func.count(Appointment.id).desc())
        .limit(3)
        .all()
    )
    
    return [
        {"clinic_name": row.name, "appointment_count": row.appointment_count} 
        for row in results
    ]


@router.get("/stats/today", response_model=List[AppointmentResponse], summary="Sadece bugün için alınmış randevular")
def get_today_appointments(db: Session = Depends(get_db)):
    """
    Randevu tarihi sistemde 'bugün' olan tüm randevuları döndürür.
    """
    today = date.today()
    
    # MariaDB func.date(Datetime) eşleştirmesi ile 
    # bugünkü tam/başlangıç-bitiş saatleriyle uğraşmadan performanslı filtreleme yapıyoruz.
    appointments = db.query(Appointment).filter(
        func.date(Appointment.appointment_datetime) == today
    ).all()
    
    return appointments


@router.post("/doctors", summary="Admin tarafından yeni doktor ekler", status_code=201)
def add_new_doctor(payload: AdminDoctorCreate, db: Session = Depends(get_db)):
    """
    Hem User (giriş için) hem de Doctor (profil için) kaydını eşzamanlı oluşturur.
    """
    # 1. Check if email already exists in Users
    if db.query(User).filter(User.email == payload.email).first():
        raise HTTPException(status_code=400, detail="Bu e-posta adresi zaten sistemde kayıtlı.")
        
    # 2. Create User account for the doctor
    fake_tc = str(random.randint(10000000000, 99999999999))
    new_user = User(
        tc_no_encrypted=encrypt_field(fake_tc).encode('utf-8'),
        name=payload.name,
        email=payload.email,
        hashed_password=hash_password(payload.password),
        role="doctor",
        city=payload.city,
        district=payload.district,
        is_verified=True,  # Yöneticinin eklediği hesap otomatik onaylıdır
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    # 3. Create Doctor Profile
    new_doctor = Doctor(
        name=payload.name,
        specialization=payload.specialization,
        clinic_id=payload.clinic_id,
        is_active=True
    )
    db.add(new_doctor)
    db.commit()
    db.refresh(new_doctor)
    
    return {
        "message": "Doktor başarıyla eklendi", 
        "doctor_id": new_doctor.id, 
        "user_id": new_user.id
    }
