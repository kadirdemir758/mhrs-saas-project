"""
MHRS SaaS — Randevu Slotları Router'ı
"""
from datetime import date
from typing import List
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.logic.slot_manager import get_available_slots

# main.py dosyasında include edilirken 'prefix="/api/v1"' var.
# Burada prefix="/slots" ekliyoruz ki tam yol "/api/v1/slots/available" olsun.
router = APIRouter(
    prefix="/slots",
    tags=["Slots & Availability"]
)

@router.get(
    "/available",
    response_model=List[str],
    summary="Belirli bir gündeki boş doktor saatlerini getir"
)
def fetch_available_slots(
    doctor_id: int = Query(..., description="Müsaitliği kontrol edilecek doktorun ID'si"),
    date_param: date = Query(..., alias="date", description="Tarih (YYYY-MM-DD formatında, örn: 2025-10-15)"),
    db: Session = Depends(get_db)
):
    """
    Belirtilen `doctor_id` ve `date` parametrelerine göre, mesai saatleri (09:00 - 17:00) 
    içerisinde henüz başka bir randevu alınmamış tüm **müsait 15 dakikalık periyotları** 
    ("HH:MM" formatında bir liste olarak) döndürür.
    
    Çıktı Örneği:
    `["09:00", "09:45", "10:15", "14:30", ...]`
    """
    return get_available_slots(db=db, doctor_id=doctor_id, target_date=date_param)
