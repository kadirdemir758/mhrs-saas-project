import sys
sys.stdout.reconfigure(encoding='utf-8')
import datetime
import random
from fastapi.testclient import TestClient
from app.main import app
from app.database import SessionLocal
from app.models.doctor import Doctor
from app.models.clinic import Clinic
from app.models.user import User

client = TestClient(app)

def get_or_create_test_data():
    db = SessionLocal()
    try:
        clinic = db.query(Clinic).first()
        if not clinic:
            clinic = Clinic(name="Test Clinic", city="Test City", district="Test District")
            db.add(clinic)
            db.commit()
            db.refresh(clinic)
            
        user_doctor = db.query(User).filter(User.email == "doktor@mhrs.com").first()
        if not user_doctor:
            print("❌ User doktor@mhrs.com bulunamadı. Önce seed.py'yi çalıştırın.")
            exit(1)
            
        doctor = db.query(Doctor).filter(Doctor.id == user_doctor.id).first()
        if not doctor:
            doctor = Doctor(id=user_doctor.id, name="Test Doktor", specialization="Genel", clinic_id=clinic.id, title="Dr.", education="Tıp", languages="Türkçe", working_hours="09:00-17:00")
            db.add(doctor)
        else:
            doctor.title = "Dr."
            doctor.education = "Tıp"
            doctor.languages = "Türkçe"
            doctor.working_hours = "09:00-17:00"
        
        db.commit()
        db.refresh(doctor)
            
        user_patient = db.query(User).filter(User.email == "hasta@mhrs.com").first()
        return doctor.id, clinic.id, user_patient.id
    finally:
        db.close()

def main():
    print("🔄 Test Verileri Hazırlanıyor...")
    doc_id, clinic_id, p_id = get_or_create_test_data()
    
    print("➡️ Adım 1: hasta@mhrs.com ile giriş yapılıyor...")
    res = client.post("/api/v1/auth/login", json={"email": "hasta@mhrs.com", "password": "123456"})
    if res.status_code != 200:
        print(f"❌ Hasta login başarısız! {res.status_code} - {res.text}")
        return
    patient_token = res.json()["access_token"]
    print("✅ Hasta token alındı.")

    print("➡️ Adım 2: Randevu oluşturuluyor...")
    now = datetime.datetime.now(datetime.timezone.utc)
    future = now + datetime.timedelta(days=random.randint(1, 30))
    appt_time = future.replace(hour=random.randint(9, 16), minute=random.choice([0, 15, 30, 45]), second=0, microsecond=0)
    
    appt_data = {
        "doctor_id": doc_id,
        "clinic_id": clinic_id,
        "appointment_datetime": appt_time.isoformat(),
        "complaint": "Otomatik test şikayeti"
    }
    
    headers = {"Authorization": f"Bearer {patient_token}"}
    res = client.post(f"/api/v1/appointments/?patient_id={p_id}", json=appt_data, headers=headers)
    if res.status_code != 201:
        print(f"❌ Randevu oluşturma başarısız! {res.status_code} - {res.text}")
        return
    print("✅ Randevu başarıyla oluşturuldu.")
    
    print("➡️ Adım 3: doktor@mhrs.com ile giriş yapılıyor...")
    res = client.post("/api/v1/auth/login", json={"email": "doktor@mhrs.com", "password": "123456"})
    if res.status_code != 200:
        print(f"❌ Doktor login başarısız! {res.status_code} - {res.text}")
        return
    doctor_token = res.json()["access_token"]
    print("✅ Doktor token alındı.")

    print("➡️ Adım 4: Doktor randevuları listeleniyor...")
    headers = {"Authorization": f"Bearer {doctor_token}"}
    res = client.get("/api/v1/doctors/me/appointments", headers=headers)
    if res.status_code != 200:
        print(f"❌ Randevu listesi alınamadı! {res.status_code} - {res.text}")
        return
        
    appointments = res.json().get("appointments", [])
    found = any(a.get("complaint") == "Otomatik test şikayeti" for a in appointments)
    
    if found:
        print("\n\033[92m✅ UÇTAN UCA TEST BAŞARILI: HASTA RANDEVU ALDI VE DOKTOR PANELİNE DÜŞTÜ!\033[0m\n")
    else:
        print("\n❌ UÇTAN UCA TEST BAŞARISIZ: Randevu doktora ulaşmadı.\n")
        print("Gelen randevular:", appointments)

if __name__ == "__main__":
    main()
