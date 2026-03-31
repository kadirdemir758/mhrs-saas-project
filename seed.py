from app.database import SessionLocal
from app.models.user import User
from app.models.doctor import Doctor
from security.auth import hash_password
from security.encryption_utils import encrypt_field

def seed_db():
    db = SessionLocal()
    try:
        # Clear existing
        db.query(User).filter(User.email.in_(["doktor@mhrs.com", "hasta@mhrs.com"])).delete(synchronize_session=False)
        db.commit()

        # Hasta
        hasta = User(
            tc_no_encrypted=encrypt_field("11111111111").encode("utf-8"),
            name="Test Hasta",
            email="hasta@mhrs.com",
            hashed_password=hash_password("123456").encode("utf-8"),
            role="patient",
            is_verified=True,
        )
        db.add(hasta)
        
        # Doktor (first create in Doctor table, then User or vice versa depending on your model)
        # Assuming just User table for login is enough, but to make it realistic we could add to doctor 
        doktor = User(
            tc_no_encrypted=encrypt_field("22222222222").encode("utf-8"),
            name="Test Doktor",
            email="doktor@mhrs.com",
            hashed_password=hash_password("123456").encode("utf-8"),
            role="doctor",
            is_verified=True,
        )
        db.add(doktor)

        # Yönetici
        admin = User(
            tc_no_encrypted=encrypt_field("33333333333").encode("utf-8"),
            name="Sistem Yöneticisi",
            email="admin@mhrs.com",
            hashed_password=hash_password("123456").encode("utf-8"),
            role="admin",
            is_verified=True,
        )
        db.add(admin)

        db.commit()
        
        print("✅ Seeds successfully created!")
    except Exception as e:
        print(f"❌ Seed failed: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    seed_db()
