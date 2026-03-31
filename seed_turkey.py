"""
MHRS SaaS — Akıllı Seed Botu (Türkiye İl-İlçe Katmanlayıcı)
"""
import os
import sys
import requests
from sqlalchemy.orm import Session

# PYTHONPATH'i proje dizinine bağla ki 'app' modülleri tanınsın
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.database import SessionLocal, engine, Base
from app.models.location import Province, District

# Güvenilir Turkey API Rotaları
SOURCE_URL = "https://turkiyeapi.dev/api/v1/provinces"

def run_seeder():
    print("🔄 Veritabanı tabloları taranıyor...")
    # Yeni yazdığımız Province ve District modelleri için tablo üret
    Base.metadata.create_all(bind=engine)
    
    print(f"🌍 Hedef kaynaktan veri çekiliyor: {SOURCE_URL}")
    try:
        response = requests.get(SOURCE_URL)
        response.raise_for_status()
        json_resp = response.json()
        data = json_resp.get("data", [])
    except Exception as e:
        print(f"❌ Veri çekerken bağlantı hatası oluştu: {e}")
        return

    db: Session = SessionLocal()
    
    try:
        print("🧹 Çakışmaları önlemek için eski konum verileri temizleniyor...")
        db.query(District).delete()
        db.query(Province).delete()
        db.commit()

        print("🏗️ Veriler parse ediliyor ve MariaDB'ye aktarılıyor. (Lütfen bekleyin...)")
        
        objects_to_add = []
        for item in data:
            province_name = item.get("name")
            districts_data = item.get("districts", [])
            
            # İli oluştur
            province = Province(name=province_name)
            db.add(province)
            db.flush() # province.id bilgisini RAM üzerinde almamızı sağlar
            
            # İlişik ilçeleri yığınla (Bulk Add optimizasyonu)
            for d in districts_data:
                district_name = d.get("name")
                objects_to_add.append(District(name=district_name, province_id=province.id))
        
        # Tüm ilçeleri topluca aktar
        db.add_all(objects_to_add)
        db.commit()
        
        print("🎉 Tebrikler! Türkiye'nin 81 İli ve yüzlerce ilçesi MariaDB sisteminize başarıyla işlenmiştir.")
    except Exception as e:
        db.rollback()
        print(f"❌ Veritabanına kayıt işlemi sırasında hata fırlatıldı: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    run_seeder()
