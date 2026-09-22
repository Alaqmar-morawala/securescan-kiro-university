from django.urls import path

from .views import (
    ScanConfigView,
    ScanDetailView,
    ScanHistoryView,
    ScanProgressView,
    ScanStartView,
    TargetCreateView,
)

app_name = "scanner"

urlpatterns = [
    path("targets/add/", TargetCreateView.as_view(), name="target_add"),
    path("targets/<int:pk>/configure/", ScanConfigView.as_view(), name="configure"),
    path("scans/<int:pk>/start/", ScanStartView.as_view(), name="scan_start"),
    path("scans/<int:pk>/progress/", ScanProgressView.as_view(), name="scan_progress"),
    path("scans/<int:pk>/", ScanDetailView.as_view(), name="scan_detail"),
    path("history/", ScanHistoryView.as_view(), name="history"),
]
