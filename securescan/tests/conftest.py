"""Pytest config: Django settings for SecureScan tests."""

import os

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")


def pytest_configure():
    import django

    django.setup()
