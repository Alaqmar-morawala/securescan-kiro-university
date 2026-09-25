"""Pytest config: Django settings for SecureScan tests."""

import os

# Tests are deterministic offline: force mock fixtures unless a test file
# explicitly opts into the real engine (see test_engine_selection.py, which
# overrides the setting, and test_real_zap_integration.py gated by
# RUN_ZAP_E2E=1).
os.environ.setdefault("SECURESCAN_MOCK", "1")
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")


def pytest_configure():
    import django

    django.setup()
    # pytest-django may import config.settings (via pytest.ini) before this
    # conftest's env defaults are read, so force the offline engine here as
    # well: tests must be deterministic even when a ZAP daemon is running.
    from django.conf import settings

    settings.SECURESCAN_MOCK = True
