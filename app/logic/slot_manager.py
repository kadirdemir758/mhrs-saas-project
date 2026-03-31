"""
MHRS SaaS — Slot Yöneticisi (İş Mantığı)
"""
from datetime import date
from typing import List
from sqlalchemy.orm import Session

from app.models.appointment import Appointment, AppointmentStatus


def get_available_slots(db: Session, doctor_id: int, target_date: date) -> List[str]:
    """
    Doktorun belirli bir güne (target_date) ait müsait randevu saatlerini (HH:MM formatında) hesaplar.
    Mesai saatleri: 09:00 - 17:00 (15 dakikalık periyotlar)
    """
    # 1. 09:00'dan 17:00'ye kadar tüm olası 15 dakikalık slotları (HH:MM) oluştur
    all_slots = []
    for hour in range(9, 17):  # 09:00'dan 16:45'e kadar (17:00 kapalı sayılır)
        for minute in (0, 15, 30, 45):
            all_slots.append(f"{hour:02d}:{minute:02d}")

    # 2. İlgili doktorun aktif (iptal edilmemiş) randevularını çek
    # Performans ve güvenilirlik için filtrelemeyi doktor ID ve statü üzerinden yapıyoruz.
    active_appointments = db.query(Appointment).filter(
        Appointment.doctor_id == doctor_id,
        Appointment.status != AppointmentStatus.CANCELLED
    ).all()

    # 3. Çekilen randevuların tarihlerini (Python tarafında) kontrol ederek sadece o güne ait olan doluları bul
    # SQLite/MariaDB timezone fonksiyon farklılıklarından etkilenmemek adına tarih eşleştirmesi Python'da yapılıyor.
    booked_slots = set()
    for app in active_appointments:
        if app.appointment_datetime.date() == target_date:
            booked_slots.add(app.appointment_datetime.strftime("%H:%M"))

    # 4. Dolu olan slotları toplam listeden çıkararak filtrele (Filter mantığı)
    available_slots = [slot for slot in all_slots if slot not in booked_slots]

    return available_slots
