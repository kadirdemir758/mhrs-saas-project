import sys
import random
from datetime import datetime, timedelta, timezone

sys.path.append('.') 

from app.database import SessionLocal
from app.models.user import User
from app.models.doctor import Doctor
from app.models.clinic import Clinic
from app.models.appointment import Appointment, AppointmentStatus

def seed_appointments():
    db = SessionLocal()
    try:
        # Get doctor user
        doctor_user = db.query(User).filter(User.email == "doktor@mhrs.com").first()
        if not doctor_user:
            print("❌ doktor@mhrs.com bulunamadı! Lütfen önce seed.py çalıştırın.")
            return

        # Get doctor profile
        doctor = db.query(Doctor).filter(Doctor.id == doctor_user.id).first()
        if not doctor:
            print("ℹ️ Doktor profili yok, oluşturuluyor...")
            clinic = db.query(Clinic).first()
            if not clinic:
                clinic = Clinic(name="Merkez Poliklinik", city="İstanbul", district="Kadıköy", is_active=True)
                db.add(clinic)
                db.commit()
                db.refresh(clinic)
            
            doctor = Doctor(
                id=doctor_user.id, 
                name=doctor_user.name, 
                specialization="Dahiliye", 
                clinic_id=clinic.id,
                title="Uzm. Dr.",
                is_active=True
            )
            db.add(doctor)
            db.commit()
            db.refresh(doctor)
            
        clinic_id = doctor.clinic_id
        if not clinic_id:
            clinic = db.query(Clinic).first()
            clinic_id = clinic.id if clinic else None
        
        # Get patient
        patient_user = db.query(User).filter(User.email == "hasta@mhrs.com").first()
        if not patient_user:
            print("❌ hasta@mhrs.com bulunamadı!")
            return
            
        complaints = ["Baş ağrısı", "Gözlerde yanma", "Rutin kontrol", "Sırt ağrısı", "Mide bulantısı", "Halsizlik", "Öksürük"]
        
        db.query(Appointment).filter(Appointment.doctor_id == doctor.id).delete()
        print("ℹ️ Eski test randevuları temizlendi.")
        db.commit()

        print(f"🔄 {doctor.name} için randevular ekleniyor...")
        now = datetime.now(timezone.utc)
        
        appointments_to_add = []
        for i in range(10):
            # Mix past and future
            if i < 4:
                days_offset = -random.randint(1, 10)
                status = random.choice([AppointmentStatus.COMPLETED, AppointmentStatus.COMPLETED, AppointmentStatus.NO_SHOW])
            else:
                days_offset = random.randint(1, 14)
                status = AppointmentStatus.PENDING
                
            appt_time = now + timedelta(days=days_offset)
            minute = random.choice([0, 15, 30, 45])
            hour = random.randint(9, 16)
            appt_time = appt_time.replace(hour=hour, minute=minute, second=0, microsecond=0)
            
            appt = Appointment(
                patient_id=patient_user.id,
                doctor_id=doctor.id,
                clinic_id=clinic_id,
                appointment_datetime=appt_time,
                complaint=random.choice(complaints),
                status=status
            )
            appointments_to_add.append(appt)
            
        db.add_all(appointments_to_add)
        db.commit()
        print("✅ Başarıyla 10 adet rastgele randevu eklendi!")

    except Exception as e:
        print(f"❌ Hata oluştu: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    seed_appointments()
