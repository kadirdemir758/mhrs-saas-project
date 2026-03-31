import requests
import random

# --- AYARLAR ---
BASE_URL = "http://localhost:8000/api/v1"
EMAIL = "kadir_yeni@test.com"
PASSWORD = "Admin1234!"

# --- VERİ HAVUZU ---
bolumler = [
    "Kardiyoloji", "Göz Hastalıkları", "Dahiliye", "Ortopedi", 
    "Nöroloji", "Psikiyatri", "Kulak Burun Boğaz", "Üroloji", 
    "Dermatoloji", "Çocuk Sağlığı", "Genel Cerrahi", "Göğüs Hastalıkları"
]
unvanlar = ["Uzman Dr.", "Doç. Dr.", "Prof. Dr.", "Operatör Dr."]
isimler = ["Ahmet", "Mehmet", "Ayşe", "Fatma", "Can", "Ece", "Murat", "Selin", "Burak", "Zeynep", "Hakan", "Elif"]
soyisimler = ["Yılmaz", "Kaya", "Demir", "Çelik", "Yıldız", "Aydın", "Öztürk", "Arslan", "Doğan", "Kılıç", "Şahin", "Koç"]

# Şehir ve Öne Çıkan İlçeler (Örneği genişletebilirsin)
city_districts = {
    "İstanbul": ["Kadıköy", "Beşiktaş", "Üsküdar", "Fatih", "Pendik", "Şişli"],
    "Ankara": ["Çankaya", "Keçiören", "Yenimahalle", "Mamak", "Etimesgut"],
    "İzmir": ["Konak", "Karşıyaka", "Bornova", "Buca", "Çeşme"],
    "Kütahya": ["Merkez", "Tavşanlı", "Simav", "Gediz", "Emet", "Domaniç"],
    "Bursa": ["Osmangazi", "Nilüfer", "Yıldırım", "İnegöl"],
    "Antalya": ["Muratpaşa", "Kepez", "Alanya", "Manavgat"],
    "Adana": ["Seyhan", "Çukurova", "Yüreğir"],
    "Trabzon": ["Ortahisar", "Akçaabat", "Yomra"],
    "Erzurum": ["Yakutiye", "Palandöken", "Aziziye"],
    "Sivas": ["Merkez", "Şarkışla", "Suşehri"]
}

# 81 İlin tamamı (Eğer yukarıda ilçesi yoksa 'Merkez' ilçesi atanır)
tum_iller = [
    "Adana", "Adıyaman", "Afyonkarahisar", "Ağrı", "Amasya", "Ankara", "Antalya", "Artvin", "Aydın", "Balıkesir",
    "Bilecik", "Bingöl", "Bitlis", "Bolu", "Burdur", "Bursa", "Çanakkale", "Çankırı", "Çorum", "Denizli",
    "Diyarbakır", "Edirne", "Elazığ", "Erzincan", "Erzurum", "Eskişehir", "Gaziantep", "Giresun", "Gümüşhane", "Hakkari",
    "Hatay", "Isparta", "Mersin", "İstanbul", "İzmir", "Kars", "Kastamonu", "Kayseri", "Kırklareli", "Kırşehir",
    "Kocaeli", "Konya", "Kütahya", "Malatya", "Manisa", "Kahramanmaraş", "Mardin", "Muğla", "Muş", "Nevşehir",
    "Niğde", "Ordu", "Rize", "Sakarya", "Samsun", "Siirt", "Sinop", "Sivas", "Tekirdağ", "Tokat",
    "Trabzon", "Tunceli", "Şanlıurfa", "Uşak", "Van", "Yozgat", "Zonguldak", "Aksaray", "Bayburt", "Karaman",
    "Kırıkkale", "Batman", "Şırnak", "Bartın", "Ardahan", "Iğdır", "Yalova", "Karabük", "Kilis", "Osmaniye", "Düzce"
]

def get_token():
    try:
        resp = requests.post(f"{BASE_URL}/auth/login", json={"email": EMAIL, "password": PASSWORD})
        return resp.json().get("access_token") if resp.status_code == 200 else None
    except: return None

def seed_enterprise():
    token = get_token()
    if not token: 
        print("❌ Giriş başarısız!"); return
    
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    print("🏥 MHRS Veri Simülasyonu Başlatıldı...")

    for il in tum_iller:
        # Şehrin ilçelerini al, yoksa sadece 'Merkez' kullan
        ilceler = city_districts.get(il, ["Merkez"])
        
        for ilce in ilceler:
            # Her ilçeye rastgele 2-4 farklı branşta klinik aç
            secilen_bolumler = random.sample(bolumler, k=random.randint(2, 4))
            
            for bolum in secilen_bolumler:
                c_payload = {
                    "name": bolum, "city": il, "district": ilce,
                    "clinic_type": "Genel", "phone": f"0{random.randint(200, 500)}", 
                    "address": f"{il} {ilce} Devlet Hastanesi {bolum} Polikliniği"
                }
                c_resp = requests.post(f"{BASE_URL}/doctors/clinics", json=c_payload, headers=headers)
                
                if c_resp.status_code == 201:
                    k_id = c_resp.json()["id"]
                    print(f"📍 {il} / {ilce} -> {bolum} Kliniği açıldı.")
                    
                    # Her kliniğe 1-2 doktor ata
                    for _ in range(random.randint(1, 2)):
                        d_ad = f"{random.choice(isimler)} {random.choice(soyisimler)}"
                        d_payload = {
                            "name": d_ad, "specialization": bolum, "clinic_id": k_id,
                            "title": random.choice(unvanlar), "languages": "TR, EN", "working_hours": "09:00-17:00"
                        }
                        requests.post(f"{BASE_URL}/doctors/", json=d_payload, headers=headers)
                        print(f"   👨‍⚕️ Dr. {d_ad} görevlendirildi.")

if __name__ == "__main__":
    seed_enterprise()
    print("\n✅ GERÇEK MHRS VERİ SETİ BAŞARIYLA YÜKLENDİ!")