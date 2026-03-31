"""
MHRS SaaS — Belirti Analizi Şemaları (Symptom Analyzer)
"""
from pydantic import BaseModel, Field


class SymptomRequest(BaseModel):
    """
    Kullanıcının şikayetlerini ilettiği talep modeli.
    """
    symptom_text: str = Field(
        ..., 
        description="Hastanın kendi cümleleriyle girdiği şikayet metni (örn: 'Dünden beri şiddetli baş ağrım var.')",
        min_length=3
    )


class SymptomResponse(BaseModel):
    """
    Analiz motorundan dönen öneri modeli.
    """
    recommended_clinic: str = Field(..., description="NLP/Algoritma tarafından önerilen poliklinik/klinik adı")
    description: str = Field(..., description="Bu kliniğin neden önerildiğine dair hasta için kısa bir açıklama")
