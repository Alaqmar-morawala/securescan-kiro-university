"""Scanner views: targets, configs, scan run, progress, detail, history."""

import threading

from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views import View
from django.views.generic import DetailView, ListView

from .docker_runner import run_scan, seed_estimate
from .engine import resolve_engine
from .forms import ScanConfigForm, TargetForm
from .models import Scan, Target
from .services import estimate_cost, order_findings


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
        return render(
            request, self.template_name,
            {"target": target, "form": ScanConfigForm()},
        )

    def post(self, request, pk):
        target = self._target(request, pk)
        form = ScanConfigForm(request.POST)
        if form.is_valid():
            config = form.save(commit=False)
            config.target = target
            config.save()
            cost, duration = estimate_cost(
                config.max_pages, config.spider_depth, config.scan_type
            )
            scan = Scan.objects.create(
                owner=request.user, target=target, config=config,
                cost_estimate=cost, duration_estimate_s=duration,
            )
            return redirect(
                "scanner:scan_detail", pk=scan.pk
            )
        return render(
            request, self.template_name,
            {"target": target, "form": form},
        )


class ScanStartView(LoginRequiredMixin, View):
    def post(self, request, pk):
        scan = get_object_or_404(Scan, pk=pk, owner=request.user)
        if scan.status == "RUNNING":
            return redirect("scanner:scan_detail", pk=scan.pk)
        seed_estimate(scan)
        if resolve_engine().is_real:
            # Real ZAP scans take minutes: run in the background so the
            # detail page can stream progress via the polling hook.
            threading.Thread(
                target=run_scan,
                args=(scan,),
                name=f"securescan-{scan.pk}",
                daemon=True,
            ).start()
        else:
            run_scan(scan)
        return redirect("scanner:scan_detail", pk=scan.pk)


class ScanDetailView(LoginRequiredMixin, DetailView):
    model = Scan
    template_name = "scanner/scan_detail.html"

    def get_queryset(self):
        return (
            Scan.objects.filter(owner=self.request.user)
            .select_related("target", "config")
            .prefetch_related("findings")
        )

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        findings = list(ctx["object"].findings.all())
        raw = [
            {"severity": f.severity, "name": f.name, "url": f.url, "pk": f.pk}
            for f in findings
        ]
        # order_findings sorts by severity (High > Medium > Low > Info);
        # preserve that order when mapping back to model instances.
        ordered_pks = [f["pk"] for f in order_findings(raw)]
        pk_to_finding = {f.pk: f for f in findings}
        ctx["findings"] = [
            pk_to_finding[pk] for pk in ordered_pks if pk in pk_to_finding
        ]
        return ctx


class ScanProgressView(LoginRequiredMixin, View):
    def get(self, request, pk):
        scan = get_object_or_404(Scan, pk=pk, owner=request.user)
        return JsonResponse({"status": scan.status, "progress": scan.progress})


class ScanHistoryView(LoginRequiredMixin, ListView):
    model = Scan
    template_name = "scanner/history.html"
    context_object_name = "scans"
    paginate_by = 10

    def get_queryset(self):
        return (
            Scan.objects.filter(owner=self.request.user)
            .select_related("target", "config")
        )
