"""Scanner forms with strict validation."""

from django import forms
from django.core.validators import URLValidator

from .crypto import encrypt_secret
from .guards import TargetNotAllowed, validate_scan_target
from .models import ScanConfig, Target


class TargetForm(forms.ModelForm):
    class Meta:
        model = Target
        fields = ["name", "url", "secret_header_name", "secret_header_value"]

    def clean_url(self):
        url = self.cleaned_data["url"].strip()
        URLValidator(schemes=["http", "https"])(url)
        if not (url.startswith("http://") or url.startswith("https://")):
            raise forms.ValidationError(
                "URL must start with http:// or https://"
            )
        # Static SSRF check only (no DNS at form time); the scan runner
        # re-validates with full resolution before fetching anything.
        try:
            url = validate_scan_target(url, resolve=False)
        except TargetNotAllowed as exc:
            raise forms.ValidationError(str(exc))
        return url

    def clean_secret_header_value(self):
        value = self.cleaned_data["secret_header_value"]
        return encrypt_secret(value) if value else ""


class ScanConfigForm(forms.ModelForm):
    class Meta:
        model = ScanConfig
        fields = ["scan_type", "spider_depth", "max_pages"]

    def clean_spider_depth(self):
        depth = self.cleaned_data["spider_depth"]
        if not 0 <= depth <= 5:
            raise forms.ValidationError("Depth must be between 0 and 5.")
        return depth

    def clean_max_pages(self):
        pages = self.cleaned_data["max_pages"]
        if not 1 <= pages <= 1000:
            raise forms.ValidationError("Pages must be between 1 and 1000.")
        return pages
