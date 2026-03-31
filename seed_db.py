import sys
import os
from datetime import datetime, timezone
sys.path.append(os.getcwd())

from app.database import SessionLocal
from app.models import Doctor, Clinic, User

def seed_everything():
    db = SessionLocal()
    try:
        print("🚀 Tüm sistem (Hasta + Klinikler + 20 Doktor) yükleniyor...")
        
        # 1. SENİ EKLEYELİM (TC No zorunluluğu çözüldü)
        me = User(
            name="Kadir Kaya", 
            email="kadir@example.com", 
            hashed_password="123", 
            tc_no_encrypted="ENC_12345678901", # Burası boş kalamazdı, doldurduk!
            role="PATIENT",
            is_active=True
        )
        db.add(me)
        db.commit() 

        # 2. POLİKLİNİKLER
        klinikler = [
            Clinic(name="Dahiliye", city="Kütahya", district="Merkez", address="Blok A", is_active=True),
            Clinic(name="Kardiyoloji", city="Kütahya", district="Merkez", address="Blok B", is_active=True),
            Clinic(name="Nöroloji", city="Kütahya", district="Merkez", address="Blok C", is_active=True),
            Clinic(name="Göz Hastalıkları", city="Kütahya", district="Merkez", address="Blok D", is_active=True),
            Clinic(name="KBB", city="Kütahya", district="Merkez", address="Blok E", is_active=True)
        ]
        db.add_all(klinikler)
        db.commit()

        # 3. 20 TANE DOKTOR (Her kliniğe 4 doktor)
        isimler = [
            "Ahmet Yılmaz", "Ayşe Demir", "Mehmet Kaya", "Fatma Yıldız",
            "Can Özcan", "Elif Şahin", "Burak Çelik", "Zeynep Aydın",
            "Murat Aksoy", "Selin Doğan", "Hakan Erdem", "Deniz Yurt",
            "Okan Bulut", "Ece Koç", "Mert Güneş", "Aslı Arslan",
            "Kaan Tekin", "Gamze Polat", "Yiğit Kılıç", "Büşra Çetin"
        ]

        idx = 0
        for klinik in klinikler:
            for _ in range(4):
                dr = Doctor(
                    name=isimler[idx],
                    specialization=klinik.name,
                    title="Uzm. Dr.",
                    clinic_id=klinik.id,
                    is_active=True
                )
                db.add(dr)
                idx += 1
        
        db.commit()
        print(f"\n✅ ZAFER! 1 Hasta (Kadir), 5 Poliklinik ve {idx} Doktor hazır.")

    except Exception as e:
        print(f"❌ Hata: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    seed_everything()