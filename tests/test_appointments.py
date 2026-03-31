"""
MHRS SaaS — Appointment Endpoint Tests
"""
from datetime import datetime, timedelta, timezone


def _future_dt(hours_ahead: int = 48) -> str:
    """Returns an ISO 8601 datetime string in the future."""
    dt = datetime.now(timezone.utc) + timedelta(hours=hours_ahead)
    return dt.isoformat()


def _seed_doctor_and_clinic(db):
    """Creates a clinic and doctor in the test DB. Returns doctor_id."""
    from app.models.clinic import Clinic
    from app.models.doctor import Doctor

    clinic = Clinic(name="Test Hospital", city="Istanbul", district="Kadikoy",
                    clinic_type="cardiology")
    db.add(clinic)
    db.flush()

    doctor = Doctor(
        name="Dr. Test",
        specialization="Cardiology",
        clinic_id=clinic.id,
    )
    db.add(doctor)
    db.commit()
    db.refresh(doctor)
    return doctor.id


def test_create_appointment(client, auth_headers, db):
    doctor_id = _seed_doctor_and_clinic(db)
    resp = client.post("/api/v1/appointments", headers=auth_headers, json={
        "doctor_id": doctor_id,
        "appointment_dt": _future_dt(48),
        "complaint": "chest pain",
    })
    assert resp.status_code == 201
    data = resp.json()
    assert data["doctor_id"] == doctor_id
    assert data["status"] == "pending"


def test_create_appointment_unauthenticated(client, db):
    doctor_id = _seed_doctor_and_clinic(db)
    resp = client.post("/api/v1/appointments", json={
        "doctor_id": doctor_id,
        "appointment_dt": _future_dt(48),
    })
    assert resp.status_code == 403


def test_create_appointment_past_date(client, auth_headers, db):
    doctor_id = _seed_doctor_and_clinic(db)
    past_dt = (datetime.now(timezone.utc) - timedelta(hours=1)).isoformat()
    resp = client.post("/api/v1/appointments", headers=auth_headers, json={
        "doctor_id": doctor_id,
        "appointment_dt": past_dt,
    })
    assert resp.status_code == 422


def test_double_booking_rejected(client, auth_headers, db):
    doctor_id = _seed_doctor_and_clinic(db)
    slot = _future_dt(72)

    # First booking — should succeed
    r1 = client.post("/api/v1/appointments", headers=auth_headers, json={
        "doctor_id": doctor_id,
        "appointment_dt": slot,
    })
    assert r1.status_code == 201

    # Second booking same slot — should fail
    r2 = client.post("/api/v1/appointments", headers=auth_headers, json={
        "doctor_id": doctor_id,
        "appointment_dt": slot,
    })
    assert r2.status_code == 409


def test_list_appointments(client, auth_headers, db):
    doctor_id = _seed_doctor_and_clinic(db)
    client.post("/api/v1/appointments", headers=auth_headers, json={
        "doctor_id": doctor_id,
        "appointment_dt": _future_dt(100),
    })
    resp = client.get("/api/v1/appointments", headers=auth_headers)
    assert resp.status_code == 200
    assert isinstance(resp.json(), list)


def test_cancel_appointment(client, auth_headers, db):
    doctor_id = _seed_doctor_and_clinic(db)
    create_resp = client.post("/api/v1/appointments", headers=auth_headers, json={
        "doctor_id": doctor_id,
        "appointment_dt": _future_dt(200),
    })
    appointment_id = create_resp.json()["id"]

    cancel_resp = client.patch(
        f"/api/v1/appointments/{appointment_id}/cancel",
        headers=auth_headers,
        json={"reason": "Schedule conflict"},
    )
    assert cancel_resp.status_code == 200
    assert cancel_resp.json()["status"] == "cancelled"


def test_cancel_already_cancelled(client, auth_headers, db):
    doctor_id = _seed_doctor_and_clinic(db)
    create_resp = client.post("/api/v1/appointments", headers=auth_headers, json={
        "doctor_id": doctor_id,
        "appointment_dt": _future_dt(300),
    })
    appointment_id = create_resp.json()["id"]

    client.patch(f"/api/v1/appointments/{appointment_id}/cancel",
                 headers=auth_headers, json={})
    resp = client.patch(f"/api/v1/appointments/{appointment_id}/cancel",
                        headers=auth_headers, json={})
    assert resp.status_code == 400
