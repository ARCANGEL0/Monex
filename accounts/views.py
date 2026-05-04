from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.decorators import login_not_required
from django.contrib.auth.forms import PasswordResetForm
from django.contrib.auth.views import (
    LoginView,
    PasswordResetCompleteView,
    PasswordResetConfirmView,
)
from django.http import HttpResponse
from django.shortcuts import render
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.views.decorators.http import require_http_methods

from .forms import PasscodeForm


@method_decorator(login_not_required, name="dispatch")
class LoginView(LoginView):
    template_name = "accounts/login.html"
    redirect_authenticated_user = True


@require_http_methods(["GET", "POST"])
def passcode_change(request):
    if request.method == "POST":
        form = PasscodeForm(request.user, request.POST)
        if form.is_valid():
            form.save()
            update_session_auth_hash(request, request.user)
            response = HttpResponse(status=204)
            response["HX-Refresh"] = "true"
            return response
    else:
        form = PasscodeForm(request.user)
    return render(request, "accounts/_passcode_modal.html", {"form": form})


@login_not_required
@require_http_methods(["GET", "POST"])
def forgot_password(request):
    if request.method == "POST":
        form = PasswordResetForm(request.POST)
        if form.is_valid():
            form.save(
                request=request,
                use_https=request.is_secure(),
                email_template_name="registration/password_reset_email.html",
                subject_template_name="registration/password_reset_subject.txt",
                from_email=None,
            )
            return render(request, "accounts/_forgot_sent.html", {})
    else:
        form = PasswordResetForm()
    return render(request, "accounts/_forgot_modal.html", {"form": form})


@method_decorator(login_not_required, name="dispatch")
class AdamPasswordResetConfirmView(PasswordResetConfirmView):
    template_name = "registration/password_reset_confirm.html"
    success_url = reverse_lazy("accounts:password_reset_complete")


@method_decorator(login_not_required, name="dispatch")
class AdamPasswordResetCompleteView(PasswordResetCompleteView):
    template_name = "registration/password_reset_complete.html"
