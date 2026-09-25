"""Secret-at-rest: encryption, decryption, masking, model + form wiring."""

import pytest
from django.contrib.auth.models import User

from scanner.crypto import decrypt_secret, encrypt_secret, is_encrypted, mask_secret
from scanner.models import Target


def test_roundtrip():
    stored = encrypt_secret("token-abc-123")
    assert is_encrypted(stored)
    assert stored != "token-abc-123"
    assert decrypt_secret(stored) == "token-abc-123"


def test_legacy_plaintext_passthrough():
    assert not is_encrypted("plain-old-value")
    assert decrypt_secret("plain-old-value") == "plain-old-value"
    assert decrypt_secret("") == ""


def test_mask():
    assert mask_secret("") == ""
    assert mask_secret(encrypt_secret("supersecret-token-4321")).endswith("4321")
    assert "supersecret" not in mask_secret(encrypt_secret("supersecret-token-4321"))


@pytest.mark.django_db
def test_model_property_and_storage(user=None):
    user = User.objects.create_user("secret-owner", password="x12345678")
    stored = encrypt_secret("raw-header-value-9")
    t = Target.objects.create(
        owner=user,
        name="t",
        url="https://example.com",
        secret_header_name="X-Auth",
        secret_header_value=stored,
    )
    t.refresh_from_db()
    assert t.secret_header_value_plain == "raw-header-value-9"
    assert t.has_secret_header
    assert t.secret_header_masked.startswith("••••")
    assert "raw-header-value" not in t.secret_header_masked


@pytest.mark.django_db
def test_form_encrypts_before_save(client):
    User.objects.create_user("form-user", password="x12345678")
    assert client.login(username="form-user", password="x12345678")
    resp = client.post(
        "/targets/add/",
        {
            "name": "authed",
            "url": "https://example.com",
            "secret_header_name": "X-Auth",
            "secret_header_value": "dont-leak-me",
        },
    )
    assert resp.status_code == 302
    t = Target.objects.get(name="authed")
    assert "dont-leak-me" not in t.secret_header_value
    assert is_encrypted(t.secret_header_value)
    assert t.secret_header_value_plain == "dont-leak-me"
