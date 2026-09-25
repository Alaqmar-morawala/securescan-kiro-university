from django.urls import path

from .views import ReportCsvView, ReportHtmlView, ReportPdfView

app_name = "reports"

urlpatterns = [
    path(
        "scans/<int:pk>/report.html",
        ReportHtmlView.as_view(),
        name="report_html",
    ),
    path(
        "scans/<int:pk>/report.pdf",
        ReportPdfView.as_view(),
        name="report_pdf",
    ),
    path(
        "scans/<int:pk>/report.csv",
        ReportCsvView.as_view(),
        name="report_csv",
    ),
]
