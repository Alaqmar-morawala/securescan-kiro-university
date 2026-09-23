"""Accounts views: register, dashboard."""

from django.contrib.auth import login
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect, render
from django.views import View
from django.views.generic import TemplateView

from scanner.models import Scan, Target


class RegisterView(View):
    template_name = "accounts/register.html"

    def get(self, request):
        if request.user.is_authenticated:
            return redirect("/accounts/")
        return render(
            request, self.template_name, {"form": UserCreationForm()}
        )

    def post(self, request):
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect("/accounts/")
        return render(request, self.template_name, {"form": form})


class DashboardView(LoginRequiredMixin, TemplateView):
    template_name = "dashboard.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["targets"] = Target.objects.filter(owner=self.request.user)[:10]
        ctx["scans"] = Scan.objects.filter(owner=self.request.user)[:10]
        return ctx
