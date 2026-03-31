from fastapi.testclient import TestClient
from app.main import app
from app.database import SessionLocal
from app.models.user import User

client = TestClient(app)

def test_add_doctor():
    # Login as admin to get token
    res = client.post("/api/v1/auth/login", data={"username": "admin@mhrs.com", "password": "123"})
    if res.status_code != 200:
        # try 123456
        res = client.post("/api/v1/auth/login", data={"username": "admin@mhrs.com", "password": "123456"})
    
    if res.status_code != 200:
        print("Admin login failed:", res.json())
        return

    token = res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # Add a doctor
    payload = {
        "name": "Test Dr Ekleme",
        "email": "dr_test_ekleme@mhrs.com",
        "password": "password123",
        "specialization": "Kardiyoloji",
        "clinic_id": 1,
        "city": "İstanbul",
        "district": "Kadıköy"
    }
    
    res = client.post("/api/v1/admin/doctors", json=payload, headers=headers)
    import json
    with open("out.json", "w", encoding="utf-8") as f:
        json.dump({"status": res.status_code, "body": res.json()}, f, indent=2)

    # clean up if successful
    if res.status_code == 201:
        db = SessionLocal()
        db.query(User).filter(User.email == payload["email"]).delete()
        db.commit()

if __name__ == "__main__":
    test_add_doctor()
