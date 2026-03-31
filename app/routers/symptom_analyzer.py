"""
MHRS SaaS — Belirti Analizi Router
"""
from fastapi import APIRouter

from app.schemas.symptom import SymptomRequest, SymptomResponse

# main.py tarafında prefix="/api/v1" eklendiği için, burada "/analyze" veriyoruz. 
# Böylece tam yol GET/POST /api/v1/analyze olacaktır.
router = APIRouter(
    prefix="/analyze",
    tags=["Symptom Analyzer"]
)

@router.post("/", response_model=SymptomResponse, summary="Belirtilere Göre Poliklinik Önerisi")
def analyze_symptoms(payload: SymptomRequest):
    """
    Hastanın girdiği "symptom_text" (şikayet) metnini analiz eder.
    (Faz 4: Geçici olarak Keyword-Matching kullanıyor, Faz 5'te NLP modeline geçirilebilir.)
    """
    text = payload.symptom_text.lower()
    
    # 1. Nöroloji Kontrolü
    if any(keyword in text for keyword in ["baş", "ağrı", "başım", "migren"]):
        return SymptomResponse(
            recommended_clinic="Nöroloji",
            description="Baş ağrısı ve nörolojik şikayetleriniz için öncelikle Nöroloji uzmanına görünmeniz önerilir."
        )
        
    # 2. Dahiliye (İç Hastalıkları) Kontrolü
    if any(keyword in text for keyword in ["karın", "mide", "bulantı", "kusma"]):
        return SymptomResponse(
            recommended_clinic="Dahiliye",
            description="Mide, sindirim ve bulantı şikayetleriniz detaylı değerlendirme için Dahiliye kliniği uygun görünmektedir."
        )
        
    # 3. Diş Hekimliği Kontrolü
    if any(keyword in text for keyword in ["diş", "dişim", "dolgu", "çürük", "dişeti", "ağız"]):
        return SymptomResponse(
            recommended_clinic="Diş Hekimliği",
            description="Diş ve ağız sağlığı şikayetleriniz için Diş Hekimliği bölümünden randevu almalısınız."
        )
        
    # HIÇBIRI EŞLEŞMEZSE (Fallback / Default)
    return SymptomResponse(
        recommended_clinic="Genel Cerrahi",
        description="Belirtileriniz belirgin bir klinik ile eşleştirilemedi. Genel kapsamlı muayene için Genel Cerrahi veya Dahiliye kliniğine başvurabilirsiniz."
    )
