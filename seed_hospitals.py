"""
MHRS SaaS — Büyük Çaplı Hastane ve Doktor Seed Botu
"""
import os
import sys
import random

# PYTHONPATH'i proje dizinine bağla ki 'app' modülleri hatasız tanınsın
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy.orm import Session
from app.database import SessionLocal, engine, Base
from app.models.location import Province, District
from app.models.clinic import Clinic
from app.models.doctor import Doctor
from app.models.appointment import Appointment

POLICLINICS = [
    "Dahiliye", 
    "Göz Hastalıkları", 
    "Kulak Burun Boğaz", 
    "Ortopedi", 
    "Kardiyoloji"
]

FIRST_NAMES = [
    "Ali", "Ayşe", "Mehmet", "Fatma", "Ahmet", "Zeynep", "Mustafa", "Elif", 
    "Kemal", "Hatice", "Hasan", "Merve", "Hakan", "Esra", "Burak", "Ceren",
    "Gökhan", "Özlem", "İbrahim", "Seda", "Can", "Ece", "Oğuz", "Gizem",
    "Kadir", "Büşra", "Volkan", "Bahar", "Talat", "Sevgi"
]

LAST_NAMES = [
    "Yılmaz", "Kaya", "Demir", "Çelik", "Şahin", "Yıldız", "Özdemir", 
    "Arslan", "Doğan", "Kılıç", "Aslan", "Çetin", "Kara", "Koç", "Kurt",
    "Özkan", "Şimşek", "Polat", "Özcan", "Korkmaz", "Erdoğan", "Yavuz",
    "Can", "Aydın", "Güler"
]

TITLES = ["Uzman Dr.", "Dr.", "Doç. Dr.", "Prof. Dr.", "Op. Dr."]

def generate_doctor_name():
    first = random.choice(FIRST_NAMES)
    last = random.choice(LAST_NAMES)
    return f"{first} {last}"

def run_seeder():
    print("🔄 Veritabanı tabloları taranıyor...")
    Base.metadata.create_all(bind=engine)
    
    db: Session = SessionLocal()
    clinics_added = 0
    doctors_added = 0
    
    try:
        print("🧹 Çakışmaları önlemek için eski randevu, klinik ve doktor verileri temizleniyor...")
        db.query(Appointment).delete()
        db.query(Doctor).delete()
        db.query(Clinic).delete()
        db.commit()

        print("🏥 81 İl için kapsamlı klinik ve doktor verileri dağıtılıyor. (Lütfen bekleyin, bu işlem biraz sürebilir...)")
        
        all_provinces = db.query(Province).all()
        if not all_provinces:
            print("⚠️ Veritabanınızda hiç il bulunamadı. Lütfen önce seed_turkey.py'yi çalıştırın.")
            return

        for province in all_provinces:
            # İle ait tüm ilçeleri (District) al
            all_districts = db.query(District).filter(District.province_id == province.id).all()
            if not all_districts:
                continue
                
            selected_districts = []
            if province.name == "Kütahya":
                # Kütahya için "Simav" kesin olarak seçilmeli
                simav = next((d for d in all_districts if "Simav" in d.name), None)
                if simav: selected_districts.append(simav)
                
                # Kalan ilçelerden 1 veya 2 tane rastgele seç (Toplam 2-3 ilçe olacak)
                other_dists = [d for d in all_districts if d.id != (simav.id if simav else -1)]
                if other_dists:
                    k = random.randint(1, 2)
                    selected_districts.extend(random.sample(other_dists, min(k, len(other_dists))))
            else:
                # Genel 81 ilin her biri için rastgele 2 veya 3 ilçe seç
                k = random.randint(2, 3)
                if len(all_districts) >= k:
                    selected_districts = random.sample(all_districts, k)
                else:
                    selected_districts = all_districts
            
            # Her seçilen ilçe için, 5 ana polikliniği sisteme işle
            for district in selected_districts:
                for poli in POLICLINICS:
                    clinic_name = f"{district.name} Devlet Hastanesi - {poli} Polikliniği"
                    
                    new_clinic = Clinic(
                        name=clinic_name,
                        city=province.name,
                        district=district.name,
                        address=f"{district.name} Hastanesi Merkez Binasi Kat: {random.randint(1, 4)}",
                        clinic_type="Devlet Hastanesi",
                        phone=f"0 ({random.randint(200, 400)}) {random.randint(100, 999)} {random.randint(10, 99)} {random.randint(10, 99)}",
                        is_active=True
                    )
                    db.add(new_clinic)
                    db.flush() # Klinik (Poliklinik) ID'sini almak RAM'e yazdırır
                    clinics_added += 1
                    
                    # Açılan HER polikliniğe, rastgele 2 veya 3 Doktor ata
                    doc_count = random.randint(2, 3)
                    for _ in range(doc_count):
                        doc_title = random.choice(TITLES)
                        doc_name = generate_doctor_name()
                        
                        # Doktorun uzmanlık alanı ile poliklinik ismini eş zamanlı yapıyoruz
                        new_doctor = Doctor(
                            name=doc_name,
                            specialization=poli, 
                            clinic_id=new_clinic.id,
                            title=doc_title,
                            languages="Türkçe, İngilizce",
                            working_hours="09:00-17:00",
                            is_active=True
                        )
                        db.add(new_doctor)
                        doctors_added += 1
            
            # Belleği yormamak için her il döngüsünün sonunda topluca Commit işlemi gerçekleştir
            db.commit()
        
        print("-" * 50)
        print(f"🎉 İşlem Başarılı: 81 İlde toplam {clinics_added} Klinik ve {doctors_added} Doktor başarıyla oluşturuldu!")
        print("-" * 50)
        
    except Exception as e:
        db.rollback()
        print(f"❌ Veritabanına kayıt sırasında kritik hata: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    run_seeder()
