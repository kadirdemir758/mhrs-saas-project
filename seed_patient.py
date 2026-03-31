from app.database import SessionLocal
from app.models.user import User
from security.auth import hash_password
from security.encryption_utils import encrypt_field

def seed_patient():
    db = SessionLocal()
    try:
        existing = db.query(User).filter(User.email == "test_hasta@mhrs.com").first()
        if existing:
            print("ℹ️  test_hasta@mhrs.com zaten mevcut, atlanıyor.")
            return

        hasta = User(
            tc_no_encrypted=encrypt_field("44444444444").encode("utf-8"),
            name="Test Hasta 2",
            email="test_hasta@mhrs.com",
            hashed_password=hash_password("123456").encode("utf-8"),
            role="patient",
            is_verified=True,
        )
        db.add(hasta)
        db.commit()
        print("✅ Test hastası başarıyla oluşturuldu! (test_hasta@mhrs.com / 123456)")
    except Exception as e:
        print(f"❌ Hata: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    seed_patient()
