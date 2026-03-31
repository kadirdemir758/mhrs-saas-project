"""
MHRS SaaS — PDF Randevu Belgesi Oluşturucu
"""
import io
from datetime import datetime
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from typing import Any


def to_ascii(text: str) -> str:
    """
    Şimdilik standart ReportLab Helvetica fontunun Tr karakter desteği kısıtlamalarını aşmak için
    basit bir karakter dönüştürme fonksiyonu kullanıyoruz.
    """
    if not text:
        return ""
    replacements = {
        'ı': 'i', 'ş': 's', 'ğ': 'g', 'ö': 'o', 'ç': 'c', 'ü': 'u',
        'İ': 'I', 'Ş': 'S', 'Ğ': 'G', 'Ö': 'O', 'Ç': 'C', 'Ü': 'U'
    }
    for search, replace in replacements.items():
        text = str(text).replace(search, replace)
    return text


def generate_appointment_pdf(appointment_data: dict) -> bytes:
    """
    Randevu bilgilerini (dict) alarak memory üzerinde A4 boyutunda bir PDF oluşturur
    ve bayt akışı (bytes) olarak geri döndürür. Sisteme/diske dosya kaydetmez.
    """
    buffer = io.BytesIO()
    
    # Yeni bir PDF kanvası (Canvas) oluştur
    c = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4
    
    # --- 1. Başlık Kutusu ve Metni ---
    c.setFillColor(colors.HexColor("#1e3a8a"))  # Modern Mavi
    c.rect(0, height - 80, width, 80, fill=True, stroke=False)
    
    c.setFillColor(colors.white)
    c.setFont("Helvetica-Bold", 22)
    # y ekseni alttan yukarı doğrudur (height = top)
    c.drawCentredString(width / 2.0, height - 50, "MHRS Randevu Belgesi")
    
    # --- 2. Randevu Detayları ---
    c.setFillColor(colors.black)
    
    # Satır yazıcısı (Helper)
    def draw_row(label: str, value: Any, y_pos: int):
        c.setFont("Helvetica-Bold", 14)
        c.drawString(60, y_pos, label)
        c.setFont("Helvetica", 14)
        c.drawString(200, y_pos, to_ascii(str(value)))
        # İnce yatay çizgi
        c.setStrokeColor(colors.lightgrey)
        c.line(60, y_pos - 10, width - 60, y_pos - 10)
        c.setStrokeColor(colors.black) # Reset
    
    start_y = height - 150
    line_gap = 40
    
    draw_row("Randevu No:", f"#{appointment_data.get('id', '---')}", start_y)
    draw_row("Hasta Adi:", appointment_data.get("patient_name", "-"), start_y - line_gap)
    draw_row("Doktor:", appointment_data.get("doctor_name", "-"), start_y - line_gap * 2)
    draw_row("Klinik:", appointment_data.get("clinic_name", "-"), start_y - line_gap * 3)
    draw_row("Tarih:", appointment_data.get("date", "-"), start_y - line_gap * 4)
    draw_row("Saat:", appointment_data.get("time", "-"), start_y - line_gap * 5)
    
    # --- 3. Alt Bilgi (Footer) ---
    c.setFont("Helvetica-Oblique", 12)
    c.setFillColor(colors.gray)
    c.drawCentredString(width / 2.0, 50, "Saglikli gunler dileriz...")
    
    # PDF'i belleğe işle ve kapat
    c.showPage()
    c.save()
    
    # Bytes verisini al ve buffer'ı boşalt
    pdf_bytes = buffer.getvalue()
    buffer.close()
    
    return pdf_bytes
