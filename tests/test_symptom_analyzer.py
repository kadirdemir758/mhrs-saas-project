"""
MHRS SaaS — Symptom Analyzer Tests
"""


def test_cardiology_keywords(client):
    resp = client.post("/api/v1/symptom-analyzer", json={
        "text": "I have severe chest pain and heart palpitations"
    })
    assert resp.status_code == 200
    data = resp.json()
    assert data["suggested_clinic_type"] == "cardiology"
    assert "chest pain" in data["matched_keywords"] or "heart" in data["matched_keywords"]


def test_neurology_keywords(client):
    resp = client.post("/api/v1/symptom-analyzer", json={
        "text": "I have a terrible migraine and dizziness"
    })
    assert resp.status_code == 200
    assert resp.json()["suggested_clinic_type"] == "neurology"


def test_ophthalmology_keywords(client):
    resp = client.post("/api/v1/symptom-analyzer", json={
        "text": "my eye hurts and my vision is blurry"
    })
    assert resp.status_code == 200
    assert resp.json()["suggested_clinic_type"] == "ophthalmology"


def test_gastroenterology_keywords(client):
    resp = client.post("/api/v1/symptom-analyzer", json={
        "text": "I have abdominal pain, nausea, and vomiting"
    })
    assert resp.status_code == 200
    assert resp.json()["suggested_clinic_type"] == "gastroenterology"


def test_fallback_to_general_practice(client):
    resp = client.post("/api/v1/symptom-analyzer", json={
        "text": "I feel general discomfort"
    })
    assert resp.status_code == 200
    # "general" keyword maps to general_practice
    assert resp.json()["suggested_clinic_type"] == "general_practice"


def test_high_confidence_multiple_matches(client):
    resp = client.post("/api/v1/symptom-analyzer", json={
        "text": "chest pain, heart palpitation and blood pressure problem"
    })
    assert resp.status_code == 200
    data = resp.json()
    assert data["suggested_clinic_type"] == "cardiology"
    assert data["confidence"] == "high"


def test_low_confidence_no_match(client):
    resp = client.post("/api/v1/symptom-analyzer", json={
        "text": "I want to see a doctor"
    })
    assert resp.status_code == 200
    assert resp.json()["confidence"] == "low"


def test_short_text_validation(client):
    resp = client.post("/api/v1/symptom-analyzer", json={"text": "ab"})
    assert resp.status_code == 422
