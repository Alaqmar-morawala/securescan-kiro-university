"""Scanner views: targets, configs, scan run, progress, detail, history."""

from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views import View
from django.views.generic import DetailView, ListView

from .services import ordered_findings, run_scan, seed_estimate
from .forms import ScanConfigForm, TargetForm
from .models import Scan, ScanConfig, Target
from .services import estimate_cost


class TargetCreateView(LoginRequiredMixin, View):
    template_name = "scanner/target_form.html"

    def get(self, request):
        return render(request, self.template_name, {"form": TargetForm()})

    def post(self, request):
        form = TargetForm(request.POST)
        if form.is_valid():
            target = form.save(commit=False)
            target.owner = request.user
            target.save()
            return redirect("scanner:configure", pk=target.pk)
        return render(request, self.template_name, {"form": form})


class ScanConfigView(LoginRequiredMixin, View):
    template_name = "scanner/configure.html"

    def _target(self, request, pk):
        return get_object_or_404(Target, pk=pk, owner=request.user)

    def get(self, request, pk):
        target = self._target(request, pk)
        return render(request, self.template_name, {"target": target, "form": ScanConfigForm()})

    def post(self, request, pk):
        target = self._target(request, pk)
        form = ScanConfigForm(request.POST)
        if form.is_valid():
            config = form.save(commit=False)
            config.target = target
            config.save()
            cost, duration = estimate_cost(config.max_pages, config.spider_depth, config.scan_type)
            scan = Scan.objects.create(
                owner=request.user, target=target, config=config,
                cost_estimate=cost, duration_estimate_s=duration,
            )
            return redirect("scanner:scan_detail", pk=scan.pk)
        return render(request, self.template_name, {"target": target, "form": form})


class ScanStartView(LoginRequiredMixin, View):
    def post(self, request, pk):
        scan = get_object_or_404(Scan, pk=pk, owner=request.user)
        seed_estimate(scan)
        run_scan(scan)
        return redirect("scanner:scan_detail", pk=scan.pk)


class ScanDetailView(LoginRequiredMixin, DetailView):
    model = Scan
    template_name = "scanner/scan_detail.html"

    def get_queryset(self):
        return Scan.objects.filter(owner=self.request.user).select_related("target", "config").prefetch_related("findings")

    def get_context_data(self, **kwargs):
        from reports.services import ordered_findings  # noqa: F401 — replaced below
        from scanner.services import order_findings

        ctx = super().get_context_data(**kwargs)
        raw = [
            {"severity": f.severity, "name": f.name, "url": f.url, "pk": f.pk}
            for f in ctx["findings"]
        ]
        ordered = {f["pk"]: f for f in order_findings(raw)}
        ctx["findings"] = [f for f in ctx["findings"] if f.pk in ordered]
        return ctx



class ScanProgressView(LoginRequiredMixin, View):
    def get(self, request, pk):
        scan = get_object_or_404(Scan, pk=pk, owner=request.user)
        return JsonResponse({"status": scan.status, "progress": scan.progress})


class ScanHistoryView(LoginRequiredMixin, ListView):
    model = Scan
    template_name = "scanner/history.html"
    context_object_name = "scans"

    def get_queryset(self):
        return Scan.objects.filter(owner=self.request.user).select_related("target", "config")

