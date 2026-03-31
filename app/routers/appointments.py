"""
MHRS SaaS — Randevu API Router (Endpoints)
"""
from typing import List

import io
from fastapi import APIRouter, Depends, Query, status, BackgroundTasks
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from app.database import get_db
from app.crud import appointment as crud
from app.schemas.appointment import (
    AppointmentCreate,
    AppointmentResponse,
    AppointmentListResponse,
    AppointmentStatusUpdate
)
from app.logic.pdf_generator import generate_appointment_pdf
from app.utils.email_sender import send_appointment_confirmation, send_appointment_cancellation
from security.auth import get_current_user, require_role
from datetime import date as DateType
from sqlalchemy import cast, Date
from app.models.appointment import Appointment, AppointmentStatus

router = APIRouter(
    prefix="/appointments",
    tags=["Appointments"]
)


@router.get(
    "/booked-slots",
    response_model=List[str],
    summary="Doktorun belirtilen gündeki dolu randevu saatlerini listeler."
)
def get_booked_slots(
    doctor_id: int = Query(...),
    date: DateType = Query(...),
    db: Session = Depends(get_db)
):
    """
    Seçilen doktor ve tarihte 'İptal edilmemiş' tüm randevuları bulup, "HH:MM" formatında dolu saatlerin listesini döner.
    """
    conflicts = db.query(Appointment.appointment_datetime).filter(
        Appointment.doctor_id == doctor_id,
        cast(Appointment.appointment_datetime, Date) == date,
        Appointment.status.notin_([AppointmentStatus.CANCELLED])
    ).all()
    
    return [dt[0].strftime("%H:%M") for dt in conflicts]

@router.post(
    "/",
    response_model=AppointmentResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Yeni randevu oluştur",
    description="Tam 15 dakikalık katlara uygun ve çakışma (double-booking) yapmayan bir randevu oluşturur."
)
def create_new_appointment(
    payload: AppointmentCreate,
    background_tasks: BackgroundTasks,
    patient_id: int = Query(..., description="Randevuyu alan kullanıcının ID'si (ileride JWT entegre edildiğinde Depends ile değiştirilmeli)"),
    db: Session = Depends(get_db),
):
    """
    Kullanıcı (hasta) için yeni bir randevu açar. 
    CRUD fonksiyonu içerisindeki 15 dakika grid kontrolüne ve double-booking korumasına tabi tutulur.
    Onay mailini arka planda (BackgroundTasks) asenkron gönderir.
    """
    appointment = crud.create_appointment(db=db, payload=payload, patient_id=patient_id)
    
    # İlgili dataları Lazy Loading ile çek
    if appointment.patient and appointment.doctor and appointment.clinic:
        background_tasks.add_task(
            send_appointment_confirmation,
            to_email=appointment.patient.email,
            doctor_name=f"{appointment.doctor.title or ''} {appointment.doctor.name}".strip(),
            date=appointment.appointment_datetime.strftime("%d.%m.%Y"),
            time=appointment.appointment_datetime.strftime("%H:%M"),
            clinic_name=appointment.clinic.name
        )
        
    return appointment


@router.get(
    "/me",
    response_model=AppointmentListResponse,
    summary="Giriş yapan hastanın kendi randevularını listeler",
)
def get_my_appointments(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    JWT Token'dan alınan kimliğe göre hastanın geçmiş ve gelecek randevularını (Doktor ve Klinik datasıyla) getirir.
    """
    appointments = crud.get_appointments_by_patient(db=db, patient_id=current_user.id, skip=skip, limit=limit)
    return AppointmentListResponse(
        total=len(appointments),
        appointments=appointments
    )


@router.get(
    "/doctor/{doctor_id}",
    response_model=AppointmentListResponse,
    summary="Doktorun kendi takvimini/randevularını listelemesi",
)
def get_doctor_appointments(
    doctor_id: int,
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
):
    """
    Girilen doctor_id'ye ait randevuları sayfalı şekilde döndürür.
    Doktorların kendi ekranlarında günlük/haftalık takvimlerini çizerken kullanılır.
    """
    appointments = crud.get_appointments_by_doctor(db=db, doctor_id=doctor_id, skip=skip, limit=limit)
    return AppointmentListResponse(
        total=len(appointments),
        appointments=appointments
    )


@router.patch(
    "/{appointment_id}/cancel",
    response_model=AppointmentResponse,
    summary="Kendi randevunu iptal et",
)
def cancel_my_appointment(
    appointment_id: int,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    Belirtilen randevuyu status='cancelled' yapar. Yalnızca JWT sahibi olan kullanıcı kendi randevusunu iptal edebilir.
    İptal mailini arka planda (BackgroundTasks) asenkron gönderir.
    """
    appointment = crud.cancel_appointment(db=db, appointment_id=appointment_id, patient_id=current_user.id)
    
    if appointment.patient and appointment.doctor:
        background_tasks.add_task(
            send_appointment_cancellation,
            to_email=appointment.patient.email,
            doctor_name=f"{appointment.doctor.title or ''} {appointment.doctor.name}".strip(),
            date=appointment.appointment_datetime.strftime("%d.%m.%Y"),
            time=appointment.appointment_datetime.strftime("%H:%M")
        )
        
    return appointment


@router.patch(
    "/{appointment_id}/status",
    response_model=AppointmentResponse,
    summary="Doktorun randevu durumunu güncellemesi",
)
def update_appointment_status(
    appointment_id: int,
    payload: AppointmentStatusUpdate,
    db: Session = Depends(get_db),
    current_user = Depends(require_role("doctor"))
):
    """
    Sadece doktorların erişebileceği, "completed" veya "no_show" olarak durumu güncelleyen endpoint.
    """
    appointment = crud.update_appointment_status_by_doctor(
        db=db,
        appointment_id=appointment_id,
        doctor_id=current_user.id,
        new_status=payload.status
    )
    
    # Attach patient name dynamically for the response schema
    if appointment.patient:
        appointment.patient_name = appointment.patient.name
        
    return appointment


@router.get(
    "/{appointment_id}/download",
    summary="Randevu Belgesini PDF Olarak İndir (Streaming)",
    description="Randevu detaylarını veritabanından çeker ve diskte tutmadan anlık PDF oluşturup indirilebilir FileResponse (StreamingResponse) döndürür."
)
def download_appointment_pdf(
    appointment_id: int,
    db: Session = Depends(get_db)
):
    """
    Belirtilen ID'ye sahip randevuyu bulup (crud üzerinden) bellek içi bir PDF üretir ve tarayıcıya yollar.
    """
    # 1. DB'den Randevu Al (Mevcut CRUD, bulamazsa hata fırlatır)
    appointment = crud.get_appointment_by_id(db, appointment_id)
    
    # 2. Gönderilecek Veri Paketi Oluştur
    # Doctor/Clinic relationship'leri lazily ya da eagerly yüklenmiş olduğu varsayılır. 
    # Fallback'leri katarak hata oluşmasını engelleriz.
    doc_name = appointment.doctor.name if appointment.doctor else "Bilinmiyor"
    clinic_name = appointment.clinic.name if appointment.clinic else "Genel Poliklinik"
    
    # Güvenli isim çekimi (User tablosunda isim kolonu olup olmama ihtimaline karşı)
    pat_name = getattr(appointment.patient, "name", getattr(appointment.patient, "full_name", f"Hasta #{appointment.patient_id}")) if appointment.patient else f"Hasta #{appointment.patient_id}"
    
    # 3. PDF Generator Beklentisine Hazırla
    appt_data = {
        "id": appointment.id,
        "patient_name": pat_name,
        "doctor_name": doc_name,
        "clinic_name": clinic_name,
        "date": appointment.appointment_datetime.strftime("%d.%m.%Y"),
        "time": appointment.appointment_datetime.strftime("%H:%M")
    }
    
    # 4. Memory üzerinde byte verisini al
    pdf_bytes = generate_appointment_pdf(appt_data)
    
    # 5. Tarayıcıya PDF İndirme Başlığıyla Yolla (StreamingResponse FileResponse yerine byte akışında harikadır)
    return StreamingResponse(
        io.BytesIO(pdf_bytes),
        media_type="application/pdf",
        headers={
            "Content-Disposition": f"attachment; filename=randevu_{appointment.id}.pdf"
        }
    )

