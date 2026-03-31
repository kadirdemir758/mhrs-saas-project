from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_login():
    response = client.post("/api/v1/auth/login", json={
        "email": "hasta@mhrs.com",
        "password": "123456"
    })
    
    if response.status_code == 200 and "access_token" in response.json():
        print("✅ GİRİŞ SİSTEMİ KUSURSUZ ÇALIŞIYOR!")
    else:
        print(f"❌ GİRİŞ BAŞARISIZ! Durum Kodu: {response.status_code}")
        print(f"Hata Detayı: {response.text}")

if __name__ == "__main__":
    test_login()
