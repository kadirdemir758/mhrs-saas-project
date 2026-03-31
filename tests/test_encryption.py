"""
MHRS SaaS — Encryption Tests
"""
import pytest
from security.encryption_utils import encrypt_field, decrypt_field, encrypt_medical_record


def test_encrypt_returns_non_empty():
    result = encrypt_field("hello")
    assert result
    assert isinstance(result, str)


def test_encrypt_differs_from_plaintext():
    plain = "sensitive_data_12345"
    encrypted = encrypt_field(plain)
    assert encrypted != plain


def test_encrypt_decrypt_roundtrip():
    plain = "test patient data"
    assert decrypt_field(encrypt_field(plain)) == plain


def test_roundtrip_tc_no():
    tc = "12345678901"
    assert decrypt_field(encrypt_field(tc)) == tc


def test_roundtrip_unicode():
    text = "Tükenmez kalemi sev"  # Turkish Unicode
    assert decrypt_field(encrypt_field(text)) == text


def test_encrypt_empty_string():
    assert encrypt_field("") == ""
    assert decrypt_field("") == ""


def test_different_inputs_produce_different_ciphertexts():
    ct1 = encrypt_field("patient A notes")
    ct2 = encrypt_field("patient B notes")
    assert ct1 != ct2


def test_bulk_medical_record_encryption():
    record = {
        "notes": "chest pain",
        "complaint": "shortness of breath",
        "doctor_id": 5,           # Not a sensitive field — should not be encrypted
    }
    result = encrypt_medical_record(record)
    assert result["notes"] != record["notes"]
    assert result["complaint"] != record["complaint"]
    assert result["doctor_id"] == 5    # Passthrough unchanged


def test_decrypt_invalid_token_raises():
    with pytest.raises(ValueError):
        decrypt_field("not_a_valid_token")
