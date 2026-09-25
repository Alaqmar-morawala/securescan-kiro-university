"""SSRF / private-network guard tests (no DNS needed — see each test)."""

import socket

import pytest

from scanner.guards import TargetNotAllowed, validate_scan_target


@pytest.mark.parametrize(
    "url",
    [
        "http://127.0.0.1:8000/",
        "http://localhost/",
        "http://LOCALHOST:8080/",
        "http://sub.localhost/",
        "http://10.0.0.1/",
        "http://192.168.1.5/admin",
        "http://172.16.0.9/",
        "http://169.254.169.254/latest/meta-data/",
        "http://[::1]/",
        "http://[fe80::1]/",
        "http://0.0.0.0/",
        "https://metadata.internal/",
        "https://box.local/",
    ],
)
def test_private_and_internal_targets_blocked(url):
    with pytest.raises(TargetNotAllowed):
        validate_scan_target(url, resolve=True)


@pytest.mark.parametrize(
    "url",
    [
        "https://93.184.216.34/",  # public literal, no DNS involved
        "https://example.com/",    # hostname, resolve=False: static only
    ],
)
def test_public_targets_pass(url):
    assert validate_scan_target(url, resolve=True if "93.184" in url else False)


def test_public_literal_with_resolution_passes():
    assert validate_scan_target("https://93.184.216.34/", resolve=True)


def test_ftp_rejected():
    with pytest.raises(TargetNotAllowed):
        validate_scan_target("ftp://93.184.216.34/")


def test_dns_resolving_to_private_blocked(monkeypatch):
    def fake_getaddrinfo(host, *args, **kwargs):
        return [(socket.AF_INET, 0, 0, "", ("10.1.2.3", 0))]

    monkeypatch.setattr(socket, "getaddrinfo", fake_getaddrinfo)
    with pytest.raises(TargetNotAllowed):
        validate_scan_target("https://rebind.example/")


def test_dns_resolving_public_blocked_never(monkeypatch):
    def fake_getaddrinfo(host, *args, **kwargs):
        return [(socket.AF_INET, 0, 0, "", ("93.184.216.34", 0))]

    monkeypatch.setattr(socket, "getaddrinfo", fake_getaddrinfo)
    assert validate_scan_target("https://ok.example/") == "https://ok.example/"


def test_unresolvable_host_blocked(monkeypatch):
    def boom(*args, **kwargs):
        raise OSError("no dns")

    monkeypatch.setattr(socket, "getaddrinfo", boom)
    with pytest.raises(TargetNotAllowed):
        validate_scan_target("https://nope.example/")


def test_allow_private_override(monkeypatch):
    monkeypatch.setenv("SECURESCAN_ALLOW_PRIVATE_TARGETS", "1")
    assert validate_scan_target("http://127.0.0.1:8473/", resolve=True)


def test_form_rejects_private_literal():
    from scanner.forms import TargetForm

    form = TargetForm(
        data={"name": "t", "url": "http://127.0.0.1:8473/"}
    )
    assert not form.is_valid()
    assert "Blocked" in form.errors["url"][0]


def test_form_accepts_public_hostname_without_dns():
    from scanner.forms import TargetForm

    form = TargetForm(data={"name": "t", "url": "https://example.com"})
    assert form.is_valid(), form.errors
