"""Report views: HTML + PDF export (login + ownership enforced)."""

from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, render
from django.views import View

from scanner.models import Scan

from .services import build_pdf_bytes, ordered_findings


def _scan_for(request, pk):
    return get_object_or_404(
        Scan.objects.select_related("target", "config").prefetch_related(
            "findings"
        ),
        pk=pk,
        owner=request.user,
    )


class ReportHtmlView(LoginRequiredMixin, View):
    def get(self, request, pk):
        scan = _scan_for(request, pk)
        return render(
            request,
            "reports/report.html",
            {"scan": scan, "findings": ordered_findings(scan)},
        )


class ReportPdfView(LoginRequiredMixin, View):
    def get(self, request, pk):
        scan = _scan_for(request, pk)
        pdf = build_pdf_bytes(scan)
        resp = HttpResponse(pdf, content_type="application/pdf")
        resp["Content-Disposition"] = (
            f'attachment; filename="securescan-{scan.pk}.pdf"'
        )
        return resp
