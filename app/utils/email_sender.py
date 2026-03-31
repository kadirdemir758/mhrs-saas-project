import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

SENDER_EMAIL = "kadir.demir2007@gmail.com".strip()
SENDER_PASSWORD = "nkpzkkfmcnizwxnb".strip()

def _send_email(to_email: str, subject: str, body: str, error_context: str = ""):
    print(f"\n🤖 [BİLDİRİM BOTU] {to_email} adresine mail gönderimi başlatıldı...")
    try:
        msg = MIMEMultipart()
        msg['From'] = f"E-MHRS Destek <{SENDER_EMAIL}>"
        msg['To'] = to_email
        msg['Subject'] = subject
        
        msg.attach(MIMEText(body, 'plain', 'utf-8'))

        # Gmail sunucusuna bağlanıp maili ateşliyoruz (Timeout ile with bloğunda)
        with smtplib.SMTP('smtp.gmail.com', 587, timeout=10) as server:
            server.starttls()
            server.login(SENDER_EMAIL, SENDER_PASSWORD)
            server.send_message(msg)
            
        print(f"✅ Mail {to_email} adresine uçuruldu! {error_context}")
        
    except Exception as e:
        print(f"❌ MAİL HATASI: {str(e)}")
        print(f"🛠️ Geçici Çözüm (Debug Modu): Terminal üzerinden testinize devam edebilirsiniz {error_context}")


def send_verification_code(to_email: str, code: str):
    subject = "E-MHRS Hesabınızı Doğrulayın"
    body = f"""Merhaba,
E-MHRS sistemine hoş geldiniz!

Hesabınızı aktifleştirmek için doğrulama kodunuz: {code}

Sağlıklı günler dileriz.
"""
    _send_email(to_email, subject, body, error_context=f"| Kodun: {code}")


def send_password_reset_code(to_email: str, code: str):
    subject = "E-MHRS Şifre Sıfırlama Kodunuz"
    body = f"""Merhaba,

Şifrenizi sıfırlamak için onay kodunuz oluşturulmuştur.
Bu kodu ekrandaki ilgili alana girerek yeni şifrenizi belirleyebilirsiniz.

Doğrulama Kodunuz: {code}

Eğer bu işlemi siz başlatmadıysanız lütfen bu maili dikkate almayınız.
Sağlıklı günler dileriz.
"""
    _send_email(to_email, subject, body, error_context=f"| Kodun: {code}")


def send_appointment_confirmation(to_email: str, doctor_name: str, date: str, time: str, clinic_name: str):
    subject = "E-MHRS Randevunuz Onaylandı"
    body = f"""Sayın Hastamız,

{clinic_name} polikliniğinde, {doctor_name} isimli hekimimize ait randevunuz başarıyla oluşturulmuştur.

Randevu Tarihi: {date}
Randevu Saati: {time}

Sağlıklı günler dileriz.
"""
    _send_email(to_email, subject, body)


def send_appointment_cancellation(to_email: str, doctor_name: str, date: str, time: str):
    subject = "E-MHRS Randevunuz İptal Edildi"
    body = f"""Sayın Hastamız,

{doctor_name} isimli hekimimize ait {date} tarihi ve saat {time} için planlanan randevunuz iptal edilmiştir.

Sağlıklı günler dileriz.
"""
    _send_email(to_email, subject, body)