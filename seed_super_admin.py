"""
seed_super_admin.py
────────────────────────────────────────────────
Veritabanına 'patron@mhrs.com' e-postasıyla bir
Süper Admin hesabı ekler.  Aynı e-posta zaten
varsa önce siler, ardından temiz bir şekilde yeniden oluşturur.
"""

from app.database import SessionLocal
from app.models.user import User
from security.auth import hash_password
from security.encryption_utils import encrypt_field


def seed_super_admin():
    db = SessionLocal()
    try:
        # ── Varsa önce sil ──────────────────────────────────────
        existing = db.query(User).filter(User.email == "patron@mhrs.com").first()
        if existing:
            db.delete(existing)
            db.commit()
            print("🗑️  Mevcut 'patron@mhrs.com' kaydı silindi.")

        # ── Yeni Süper Admin oluştur ────────────────────────────
        super_admin = User(
            tc_no_encrypted=encrypt_field("99999999999").encode("utf-8"),
            name="Süper Admin",
            email="patron@mhrs.com",
            hashed_password=hash_password("123456").encode("utf-8"),
            role="admin",
            is_verified=True,
        )
        db.add(super_admin)
        db.commit()

        print("✅ Süper Admin hesabı hazırlandı!")
        print("   📧 E-posta : patron@mhrs.com")
        print("   🔑 Şifre   : 123456")
        print("   🛡️  Rol     : admin")

    except Exception as e:
        db.rollback()
        print(f"❌ İşlem başarısız: {e}")
    finally:
        db.close()


if __name__ == "__main__":
    seed_super_admin()
