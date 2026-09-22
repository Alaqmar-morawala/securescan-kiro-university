"""Pytest config: Django settings for SecureScan tests."""

import django
from django.conf import settings as dj_settings
import os

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

import pytest


def pytest_configure():
    import django
    django.setup()
