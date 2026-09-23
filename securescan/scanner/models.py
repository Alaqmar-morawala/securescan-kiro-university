"""Scanner models: targets, configs, scans, findings."""

from django.conf import settings
from django.db import models


class Target(models.Model):
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
        related_name="targets"
    )
    name = models.CharField(max_length=120)
    url = models.URLField(max_length=500)
    secret_header_name = models.CharField(
        max_length=120, blank=True, default=""
    )
    secret_header_value = models.CharField(
        max_length=500, blank=True, default=""
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return f"{self.name} ({self.url})"


class ScanConfig(models.Model):
    SCAN_TYPES = [
        ("baseline", "Baseline"),
        ("spider", "Spider"),
        ("active", "Active"),
        ("full", "Full"),
    ]
    target = models.ForeignKey(
        Target, on_delete=models.CASCADE, related_name="configs"
    )
    scan_type = models.CharField(
        max_length=16, choices=SCAN_TYPES, default="baseline"
    )
    spider_depth = models.PositiveSmallIntegerField(default=2)
    max_pages = models.PositiveIntegerField(default=50)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return f"{self.target.name} / {self.scan_type} d={self.spider_depth}"


class Scan(models.Model):
    STATUS = [
        ("QUEUED", "Queued"),
        ("RUNNING", "Running"),
        ("DONE", "Done"),
        ("FAILED", "Failed"),
    ]
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
        related_name="scans"
    )
    target = models.ForeignKey(
        Target, on_delete=models.CASCADE, related_name="scans"
    )
    config = models.ForeignKey(
        ScanConfig, on_delete=models.CASCADE, related_name="scans"
    )
    status = models.CharField(max_length=10, choices=STATUS, default="QUEUED")
    progress = models.PositiveSmallIntegerField(default=0)
    cost_estimate = models.DecimalField(
        max_digits=10, decimal_places=2, default=0
    )
    duration_estimate_s = models.PositiveIntegerField(default=0)
    error = models.TextField(blank=True, default="")
    created_at = models.DateTimeField(auto_now_add=True)
    finished_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [models.Index(fields=["owner", "-created_at"])]

    def __str__(self) -> str:
        return f"Scan {self.pk} {self.target.name} [{self.status}]"


class Finding(models.Model):
    SEVERITY = [
        ("High", "High"), ("Medium", "Medium"),
        ("Low", "Low"), ("Info", "Info"),
    ]
    scan = models.ForeignKey(
        Scan, on_delete=models.CASCADE, related_name="findings"
    )
    name = models.CharField(max_length=200)
    severity = models.CharField(
        max_length=10, choices=SEVERITY, default="Info"
    )
    url = models.URLField(max_length=500, blank=True, default="")
    description = models.TextField(blank=True, default="")
    solution = models.TextField(blank=True, default="")
    cwe = models.CharField(max_length=20, blank=True, default="")

    class Meta:
        ordering = ["scan", "name"]

    def __str__(self) -> str:
        return f"{self.severity}: {self.name}"
