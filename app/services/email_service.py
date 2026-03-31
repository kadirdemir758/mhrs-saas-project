"""
MHRS SaaS — Email Service
Composes and sends HTML emails via SMTP.
Used by the email_worker.py consumer.
"""
import smtplib
import ssl
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from app.config import get_settings

settings = get_settings()


def _build_verification_email(name: str, code: str) -> str:
    """Returns a styled HTML email body for verification codes."""
    return f"""
<!DOCTYPE html>
<html lang="tr">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>MHRS E-posta Doğrulama</title>
</head>
<body style="margin:0; padding:0; background-color:#f0f4f8; font-family: 'Segoe UI', Arial, sans-serif;">
  <table width="100%" cellpadding="0" cellspacing="0" style="background-color:#f0f4f8; padding: 40px 0;">
    <tr>
      <td align="center">
        <table width="560" cellpadding="0" cellspacing="0" style="background:#ffffff; border-radius:12px; overflow:hidden; box-shadow: 0 4px 20px rgba(0,0,0,0.1);">
          <!-- Header -->
          <tr>
            <td style="background: linear-gradient(135deg, #1565C0 0%, #0288D1 100%); padding: 36px 40px; text-align:center;">
              <h1 style="margin:0; color:#ffffff; font-size:28px; font-weight:700; letter-spacing:1px;">🏥 MHRS SaaS</h1>
              <p style="margin:8px 0 0; color:rgba(255,255,255,0.85); font-size:14px;">Hastane Randevu Sistemi</p>
            </td>
          </tr>
          <!-- Body -->
          <tr>
            <td style="padding: 40px;">
              <h2 style="color:#1a2e44; font-size:22px; margin-top:0;">Merhaba, {name}! 👋</h2>
              <p style="color:#4a5568; font-size:15px; line-height:1.7;">
                MHRS SaaS'a hoş geldiniz. Hesabınızı etkinleştirmek için aşağıdaki
                <strong>6 haneli doğrulama kodunu</strong> kullanın.
              </p>
              <!-- Code Box -->
              <div style="margin: 32px 0; text-align:center;">
                <div style="display:inline-block; background:#EBF5FF; border: 2px dashed #1565C0;
                            border-radius:12px; padding: 20px 48px;">
                  <span style="font-size:42px; font-weight:900; letter-spacing:12px; color:#1565C0;
                               font-family: 'Courier New', monospace;">{code}</span>
                </div>
              </div>
              <p style="color:#718096; font-size:13px; text-align:center;">
                ⏰ Bu kod <strong>15 dakika</strong> geçerlidir.
              </p>
              <hr style="border:none; border-top:1px solid #e2e8f0; margin: 32px 0;">
              <p style="color:#a0aec0; font-size:12px; text-align:center;">
                Bu e-postayı siz talep etmediyseniz güvenle görmezden gelebilirsiniz.<br>
                MHRS SaaS &copy; 2026 — Tüm hakları saklıdır.
              </p>
            </td>
          </tr>
        </table>
      </td>
    </tr>
  </table>
</body>
</html>
"""


def _build_appointment_reminder_email(name: str, doctor_name: str, appointment_dt: str) -> str:
    """Returns HTML email body for appointment reminders."""
    return f"""
<!DOCTYPE html>
<html lang="tr">
<body style="font-family: 'Segoe UI', Arial, sans-serif; background:#f0f4f8; margin:0; padding:40px 0;">
  <table width="100%" cellpadding="0" cellspacing="0">
    <tr><td align="center">
      <table width="560" style="background:#fff; border-radius:12px; box-shadow:0 4px 20px rgba(0,0,0,0.1);">
        <tr>
          <td style="background: linear-gradient(135deg, #1565C0 0%, #0288D1 100%); padding:32px 40px; text-align:center; border-radius:12px 12px 0 0;">
            <h1 style="color:#fff; margin:0; font-size:24px;">📅 Randevu Hatırlatması</h1>
          </td>
        </tr>
        <tr>
          <td style="padding:40px;">
            <p style="color:#2d3748; font-size:16px;">Merhaba <strong>{name}</strong>,</p>
            <p style="color:#4a5568; line-height:1.7;">
              <strong>{doctor_name}</strong> ile randevunuz yaklaşıyor.
            </p>
            <div style="background:#EBF5FF; border-left:4px solid #1565C0; padding:16px 20px; border-radius:6px; margin:20px 0;">
              <p style="margin:0; color:#1565C0; font-size:18px; font-weight:600;">{appointment_dt}</p>
            </div>
            <p style="color:#718096; font-size:13px;">Randevunuzu iptal etmek için uygulamayı kullanabilirsiniz.</p>
          </td>
        </tr>
      </table>
    </td></tr>
  </table>
</body>
</html>
"""


def send_verification_email(email: str, name: str, code: str) -> None:
    """
    Sends a verification email via SMTP (TLS).

    Args:
        email: Recipient email address.
        name: Recipient display name.
        code: 6-digit verification code.

    Raises:
        smtplib.SMTPException: If sending fails.
    """
    msg = MIMEMultipart("alternative")
    msg["Subject"] = f"[MHRS] E-posta Doğrulama Kodunuz: {code}"
    msg["From"] = f"{settings.smtp_from_name} <{settings.smtp_from_email}>"
    msg["To"] = email

    html_body = _build_verification_email(name, code)
    msg.attach(MIMEText(html_body, "html", "utf-8"))

    context = ssl.create_default_context()
    with smtplib.SMTP(settings.smtp_host, settings.smtp_port) as server:
        server.ehlo()
        server.starttls(context=context)
        server.login(settings.smtp_user, settings.smtp_password)
        server.sendmail(settings.smtp_from_email, email, msg.as_string())

    print(f"✅ Verification email sent to {email}")


def send_appointment_reminder(email: str, name: str, doctor_name: str, appointment_dt: str) -> None:
    """Sends an appointment reminder email."""
    msg = MIMEMultipart("alternative")
    msg["Subject"] = f"[MHRS] Randevu Hatırlatması — {appointment_dt}"
    msg["From"] = f"{settings.smtp_from_name} <{settings.smtp_from_email}>"
    msg["To"] = email

    html_body = _build_appointment_reminder_email(name, doctor_name, appointment_dt)
    msg.attach(MIMEText(html_body, "html", "utf-8"))

    context = ssl.create_default_context()
    with smtplib.SMTP(settings.smtp_host, settings.smtp_port) as server:
        server.ehlo()
        server.starttls(context=context)
        server.login(settings.smtp_user, settings.smtp_password)
        server.sendmail(settings.smtp_from_email, email, msg.as_string())

    print(f"✅ Appointment reminder sent to {email}")
