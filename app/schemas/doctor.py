"""
MHRS SaaS — Doctor & Clinic Schemas
"""
from typing import Optional, List
from pydantic import BaseModel, ConfigDict, Field


# ── CLINIC SCHEMAS ──────────────────────────────────────────────────────────

class ClinicCreate(BaseModel):
    name: str
    city: str
    district: str
    address: Optional[str] = None
    clinic_type: Optional[str] = None
    phone: Optional[str] = None


class ClinicOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    city: str
    district: str
    address: Optional[str] = None
    clinic_type: Optional[str] = None
    phone: Optional[str] = None


# ── DOCTOR SCHEMAS ──────────────────────────────────────────────────────────

class DoctorCreate(BaseModel):
    name: str = Field(..., description="Doktorun ad ve soyadı")
    specialization: str = Field(..., description="Uzmanlık alanı")
    clinic_id: int = Field(..., description="Bağlı bulunduğu klinik ID'si")
    
    title: Optional[str] = None
    languages: Optional[str] = None
    working_hours: Optional[str] = None
    bio: Optional[str] = None


class AdminDoctorCreate(BaseModel):
    name: str = Field(..., description="Doktorun ad ve soyadı")
    email: str = Field(..., description="Giriş için e-posta adresi")
    password: str = Field(..., description="Giriş şifresi")
    specialization: str = Field(..., description="Uzmanlık alanı")
    clinic_id: int = Field(1, description="Bağlı bulunduğu klinik ID'si")
    city: str = Field(..., description="Şehir bilgisi")
    district: str = Field(..., description="İlçe bilgisi")


class DoctorResponse(BaseModel):
    """
    Kullanıcının talep ettiği DoctorResponse şeması (eski DoctorOut yerine).
    """
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    specialization: str
    clinic_id: int
    
    title: Optional[str] = None
    rating: float
    total_ratings: int
    languages: Optional[str] = None
    working_hours: Optional[str] = None
    is_active: bool
    
    clinic: Optional[ClinicOut] = None


class DoctorListResponse(BaseModel):
    total: int
    doctors: List[DoctorResponse]


# ── SEARCH SCHEMAS (ELASTICSEARCH) ──────────────────────────────────────────

class DoctorSearchRequest(BaseModel):
    q: Optional[str] = None
    city: Optional[str] = None
    specialization: Optional[str] = None
    min_rating: Optional[float] = None
    page: int = 1
    size: int = 20


class DoctorSearchResponse(BaseModel):
    total: int
    results: List[DoctorResponse]
    page: int
    size: int