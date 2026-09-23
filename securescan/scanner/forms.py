"""Scanner forms with strict validation."""

from django import forms
from django.core.validators import URLValidator

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
        return url


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
