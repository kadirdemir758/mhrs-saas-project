import sys
import os

# Mevcut dizini Python yoluna ekle (app modülünü bulabilmesi için)
sys.path.append(os.getcwd())

from app.database import engine, Base
from app.models import User, Doctor, Clinic, Appointment

def fix_my_database():
    print("🔄 Veritabanı şeması güncelleniyor...")
    
    # Tabloları temizleyip en güncel haliyle (patient_id dahil) kuruyoruz
    Base.metadata.drop_all(bind=engine)
    print("🗑️ Eski tablolar silindi.")
    
    Base.metadata.create_all(bind=engine)
    print("✅ Yeni tablolar (patient_id ile) oluşturuldu.")

if __name__ == "__main__":
    try:
        fix_my_database()
        print("\n🚀 İşlem TAMAM! Şimdi randevu almayı dene.")
    except Exception as e:
        print(f"❌ Bir hata oluştu: {e}")