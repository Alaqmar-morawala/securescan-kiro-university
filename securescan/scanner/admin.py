from django.contrib import admin

from .models import Finding, Scan, ScanConfig, Target


@admin.register(Target)
class TargetAdmin(admin.ModelAdmin):
    list_display = ("name", "url", "owner", "secret_header_set", "created_at")
    search_fields = ("name", "url", "owner__username")
    # The ciphertext never renders in admin; use the app form to set secrets.
    exclude = ("secret_header_value",)

    @admin.display(boolean=True, description="Secret header")
    def secret_header_set(self, obj) -> bool:
        return obj.has_secret_header


@admin.register(ScanConfig)
class ScanConfigAdmin(admin.ModelAdmin):
    list_display = ("target", "scan_type", "spider_depth", "max_pages", "created_at")
    list_filter = ("scan_type",)


@admin.register(Scan)
class ScanAdmin(admin.ModelAdmin):
    list_display = ("pk", "target", "owner", "status", "progress", "created_at")
    list_filter = ("status",)
    search_fields = ("target__name", "owner__username")
    readonly_fields = (
        "status", "progress", "cost_estimate", "duration_estimate_s", "error",
    )


@admin.register(Finding)
class FindingAdmin(admin.ModelAdmin):
    list_display = ("severity", "name", "cwe", "scan")
    list_filter = ("severity",)
    search_fields = ("name", "url")
