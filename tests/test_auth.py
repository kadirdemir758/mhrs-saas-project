"""
MHRS SaaS — Auth Endpoint Tests
"""
import pytest
from unittest.mock import patch


def test_register_success(client):
    resp = client.post("/api/v1/auth/register", json={
        "tc_no": "98765432109",
        "name": "New User",
        "email": "newuser@example.com",
        "password": "NewPass123",
    })
    assert resp.status_code == 201
    data = resp.json()
    assert data["email"] == "newuser@example.com"
    assert "message" in data


def test_register_duplicate_email(client, registered_user):
    resp = client.post("/api/v1/auth/register", json={
        "tc_no": "11111111111",
        "name": "Duplicate",
        "email": registered_user["email"],
        "password": "TestPass123",
    })
    assert resp.status_code == 409
    assert "email" in resp.json()["detail"].lower()


def test_register_invalid_tc_no(client):
    resp = client.post("/api/v1/auth/register", json={
        "tc_no": "123",  # Too short
        "name": "Bad TC",
        "email": "bad_tc@example.com",
        "password": "TestPass123",
    })
    assert resp.status_code == 422  # Validation error


def test_register_weak_password(client):
    resp = client.post("/api/v1/auth/register", json={
        "tc_no": "22222222222",
        "name": "Weak Pass",
        "email": "weak@example.com",
        "password": "pass",  # Too weak
    })
    assert resp.status_code == 422


def test_verify_email_success(client):
    # Register
    client.post("/api/v1/auth/register", json={
        "tc_no": "33333333333",
        "name": "Verify Me",
        "email": "verify@example.com",
        "password": "VerifyPass123",
    })

    # Get code from DB
    from app.models.user import User
    from tests.conftest import TestingSessionLocal
    session = TestingSessionLocal()
    user = session.query(User).filter_by(email="verify@example.com").first()
    code = user.verification_code
    session.close()

    resp = client.post("/api/v1/auth/verify-email", json={
        "email": "verify@example.com",
        "code": code,
    })
    assert resp.status_code == 200
    assert "verified" in resp.json()["message"].lower()


def test_verify_email_wrong_code(client):
    client.post("/api/v1/auth/register", json={
        "tc_no": "44444444444",
        "name": "Wrong Code",
        "email": "wrongcode@example.com",
        "password": "WrongPass123",
    })
    resp = client.post("/api/v1/auth/verify-email", json={
        "email": "wrongcode@example.com",
        "code": "000000",
    })
    assert resp.status_code == 400


def test_login_success(client, registered_user):
    resp = client.post("/api/v1/auth/login", json=registered_user)
    assert resp.status_code == 200
    data = resp.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


def test_login_wrong_password(client, registered_user):
    resp = client.post("/api/v1/auth/login", json={
        "email": registered_user["email"],
        "password": "WrongPassword!",
    })
    assert resp.status_code == 401


def test_login_unverified_user(client):
    client.post("/api/v1/auth/register", json={
        "tc_no": "55555555555",
        "name": "Unverified",
        "email": "unverified@example.com",
        "password": "UnverifiedPass123",
    })
    resp = client.post("/api/v1/auth/login", json={
        "email": "unverified@example.com",
        "password": "UnverifiedPass123",
    })
    assert resp.status_code == 403


def test_get_me(client, auth_headers):
    resp = client.get("/api/v1/auth/me", headers=auth_headers)
    assert resp.status_code == 200
    data = resp.json()
    assert data["email"] == "test@example.com"
    assert data["role"] == "patient"


def test_get_me_unauthenticated(client):
    resp = client.get("/api/v1/auth/me")
    assert resp.status_code == 403
