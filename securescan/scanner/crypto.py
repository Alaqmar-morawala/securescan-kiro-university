"""Secret-at-rest encryption for ``Target.secret_header_value``.

Uses Fernet (AES-128-CBC + HMAC-SHA256) from ``cryptography`` with a key
derived from Django's ``SECRET_KEY`` via SHA-256 — no extra key material to
manage for this single field. Ciphertext is stored as ``enc1:<token>``;
values without that prefix are treated as legacy plaintext and passed
through on read (the next form save re-encrypts them).

The ``cryptography`` import is deferred: mock mode and every model load
work without the package installed; only actually *storing* a secret
requires it (``requirements.txt`` pins it).
"""

from __future__ import annotations

import base64
import hashlib

_PREFIX = "enc1:"


def _fernet():
    try:
        from cryptography.fernet import Fernet
    except ImportError as exc:  # pragma: no cover - only when storing secrets
        raise RuntimeError(
            "Storing a secret header requires the 'cryptography' package "
            "(pip install cryptography)."
        ) from exc
    from django.conf import settings

    key = base64.urlsafe_b64encode(
        hashlib.sha256(settings.SECRET_KEY.encode()).digest()
    )
    return Fernet(key)


def is_encrypted(stored: str) -> bool:
    return bool(stored) and stored.startswith(_PREFIX)


def encrypt_secret(plain: str) -> str:
    """Encrypt a plaintext secret for storage."""
    return _PREFIX + _fernet().encrypt(plain.encode()).decode()


def decrypt_secret(stored: str) -> str:
    """Decrypt a stored secret; legacy plaintext passes through unchanged."""
    if not stored:
        return ""
    if not is_encrypted(stored):
        return stored  # legacy row predating encryption
    return _fernet().decrypt(stored[len(_PREFIX):].encode()).decode()


def mask_secret(stored: str) -> str:
    """Masked preview safe to render in admin/UI: ``••••last4``."""
    plain = decrypt_secret(stored)
    if not plain:
        return ""
    return "••••" + plain[-4:]
