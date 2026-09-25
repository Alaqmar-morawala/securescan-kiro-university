"""Report views: HTML + PDF + CSV export (login + ownership enforced)."""

import csv

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


class ReportCsvView(LoginRequiredMixin, View):
    def get(self, request, pk):
        scan = _scan_for(request, pk)
        resp = HttpResponse(content_type="text/csv")
        resp["Content-Disposition"] = (
            f'attachment; filename="securescan-{scan.pk}.csv"'
        )
        writer = csv.writer(resp)
        writer.writerow(
            ["Severity", "Finding", "URL", "CWE", "Description", "Solution"]
        )
        for f in ordered_findings(scan):
            writer.writerow(
                [f.severity, f.name, f.url, f.cwe, f.description, f.solution]
            )
        return resp
