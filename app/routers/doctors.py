"""
MHRS SaaS — Doctors & Clinics Router
"""
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.clinic import Clinic
from app.crud import doctor as crud
from app.schemas.doctor import (
    DoctorResponse, 
    DoctorSearchResponse, 
    DoctorCreate, 
    DoctorListResponse,
    ClinicOut, 
    ClinicCreate
)
from app.schemas.appointment import AppointmentListResponse
from app.search.es_client import get_es_client
from app.config import get_settings
from security.auth import require_role, get_current_user

settings = get_settings()
router = APIRouter(prefix="/doctors", tags=["Doctors & Clinics"])


# ── GET DOCTORS LIST (RELATIONAL DB) ─────────────────────────────────────────
@router.get("/", response_model=DoctorListResponse, summary="List doctors (Paginated with search)")
def list_doctors(
    skip: int = Query(0, ge=0),
    limit: int = Query(12, ge=1, le=100),
    search: Optional[str] = Query(None),
    clinic_id: Optional[int] = Query(None),
    specialization: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    Elasticsearch kullanmadan, doğrudan MariaDB üzerinden dinamik (ilike) doktor listeleme ve sayfalama.
    """
    total, doctors = crud.get_doctors(
        db, 
        skip=skip, 
        limit=limit, 
        clinic_id=clinic_id, 
        specialization=specialization,
        search=search
    )
    return DoctorListResponse(
        total=total,
        doctors=doctors
    )


# ── CREATE DOCTOR (ADMIN ONLY) ───────────────────────────────────────────────
@router.post("/", response_model=DoctorResponse, status_code=status.HTTP_201_CREATED, summary="Create a new doctor (admin only)")
def create_new_doctor(
    payload: DoctorCreate,
    db: Session = Depends(get_db),
    _admin = Depends(require_role("admin")),
):
    """
    Yeni doktor kaydı oluşturur.
    Admin yetkisi gerektirir.
    ES event sync ORM listener üzerinden arka planda gerçekleşir.
    """
    return crud.create_doctor(db=db, payload=payload)


# ── SEARCH DOCTORS (ELASTICSEARCH) ──────────────────────────────────────────
@router.get("/search", response_model=DoctorSearchResponse, summary="Search doctors via Elasticsearch")
def search_doctors(
    q: Optional[str] = Query(None),
    city: Optional[str] = Query(None),
    specialization: Optional[str] = Query(None),
    min_rating: Optional[float] = Query(None, ge=0.0, le=5.0),
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
):
    """
    Gelişmiş Elasticsearch tabanlı arama.
    """
    from_ = (page - 1) * size
    try:
        es = get_es_client()
        # ES Arama mantığı buraya gelecek
        pass 
    except Exception:
        pass
    
    # ES'e ulaşılamazsa veya ayarlı değilse DB Fallback...
    return DoctorSearchResponse(total=0, results=[], page=page, size=size)


# ── GET MY APPOINTMENTS (DOCTOR) ──────────────────────────────────────────────
@router.get("/me/appointments", response_model=AppointmentListResponse, summary="Get logged in doctor's appointments")
def get_my_appointments(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user = Depends(require_role("doctor"))
):
    """
    Returns appointments for the currently logged-in doctor, including patient names and complaints.
    """
    from app.models.appointment import Appointment
    from app.models.user import User

    appointments_query = (
        db.query(Appointment)
        .join(User, Appointment.patient_id == User.id)
        .filter(Appointment.doctor_id == current_user.id)
        .order_by(Appointment.appointment_datetime.asc())
        .offset(skip)
        .limit(limit)
        .all()
    )

    # Attach patient name dynamically since Pydantic will read from attributes
    for appt in appointments_query:
        appt.patient_name = appt.patient.name if appt.patient else "Bilinmiyor"

    return AppointmentListResponse(
        total=len(appointments_query),
        appointments=appointments_query
    )


# ── GET DOCTOR BY ID ─────────────────────────────────────────────────────────
@router.get("/{doctor_id}", response_model=DoctorResponse, summary="Get doctor details")
def get_doctor(doctor_id: int, db: Session = Depends(get_db)):
    doctor = crud.get_doctor_by_id(db, doctor_id)
    if not doctor:
        raise HTTPException(status_code=404, detail="Doctor not found.")
    return doctor


# ── CLINICS LIST ────────────────────────────────────────────────────────────
@router.get("/clinics/list", response_model=list[ClinicOut], summary="List all active clinics")
def list_clinics(
    city: Optional[str] = Query(None),
    clinic_type: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    query = db.query(Clinic).filter(Clinic.is_active == True)
    if city: query = query.filter(Clinic.city.ilike(f"%{city}%"))
    return query.all()


# ── CREATE CLINIC (ADMIN ONLY) ──────────────────────────────────────────────
@router.post("/clinics", response_model=ClinicOut, status_code=201, summary="Create a new clinic (admin only)")
def create_clinic(
    payload: ClinicCreate,
    db: Session = Depends(get_db),
    _admin = Depends(require_role("admin")),
):
    new_clinic = Clinic(
        name=payload.name,
        city=payload.city,
        district=payload.district,
        address=payload.address,
        clinic_type=payload.clinic_type,
        phone=payload.phone,
        is_active=True
    )
    db.add(new_clinic)
    db.commit()
    db.refresh(new_clinic)
    return new_clinic