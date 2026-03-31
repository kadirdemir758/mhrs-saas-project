import pymysql

# .env dosyasındaki gerçek bilgilerle güncelliyoruz
db = pymysql.connect(
    host="localhost",
    user="root",          # Veya mhrs_user kullanabilirsin
    password="rootpass",  # .env dosyasındaki MYSQL_ROOT_PASSWORD
    database="mhrs_db"
)

try:
    with db.cursor() as cursor:
        # Yetki güncelleme sorgusu
        sql = "UPDATE users SET role = 'admin' WHERE email = 'kadir@test.com'"
        cursor.execute(sql)
    db.commit()
    print("✅ Başarıyla ADMIN oldun!")
except Exception as e:
    print(f"❌ Hata oluştu: {e}")
finally:
    db.close()