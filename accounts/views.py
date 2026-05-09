import os
from datetime import timedelta

from django.conf import settings
from django.contrib.auth import get_user_model, update_session_auth_hash
from django.contrib.auth.decorators import login_not_required
from django.contrib.auth.views import LoginView as DjangoLoginView
from django.core.mail import send_mail
from django.db import IntegrityError
from django.http import HttpResponse
from django.shortcuts import redirect, render
from django.template.loader import render_to_string
from django.utils import timezone
from django.views.decorators.http import require_http_methods

from .forms import PasscodeForm
from .models import VerificationCode

User = get_user_model()


class LoginView(DjangoLoginView):
    template_name = "accounts/login.html"
    redirect_authenticated_user = True

    def form_valid(self, form):
        response = super().form_valid(form)
        remember = self.request.POST.get("remember_me")
        if remember:
            self.request.session.set_expiry(60 * 60 * 24 * 30)
        else:
            self.request.session.set_expiry(0)
        return response


def _has_real_email():
    user = (os.environ.get("EMAIL_HOST_USER") or "").strip()
    pw = (os.environ.get("EMAIL_HOST_PASSWORD") or "").strip()
    return bool(user) and bool(pw)


def _is_configured():
    return (
        User.objects.filter(is_superuser=True).exclude(email="").exists()
        and _has_real_email()
    )


def _send_code(email, code):
    from django.core.mail import get_connection

    if _has_real_email():
        conn = get_connection(
            backend="django.core.mail.backends.smtp.EmailBackend",
            host=os.environ.get("EMAIL_HOST", "smtp.gmail.com"),
            port=int(os.environ.get("EMAIL_PORT", "587")),
            username=os.environ.get("EMAIL_HOST_USER", ""),
            password=os.environ.get("EMAIL_HOST_PASSWORD", ""),
            use_tls=os.environ.get("EMAIL_USE_TLS", "1") == "1",
        )
    else:
        conn = get_connection(backend="django.core.mail.backends.console.EmailBackend")

    html = render_to_string("emails/verification_code.html", {"code": code, "email": email})
    send_mail(
        subject="MonEx · verification code",
        message=f"your verification code is: {code}\n\nexpires in 10 minutes.",
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[email],
        html_message=html,
        fail_silently=False,
        connection=conn,
    )


@login_not_required
def first_run(request):
    if _is_configured():
        return redirect("accounts:login")

    if not _has_real_email():
        request.session["first_run_step"] = "setup_email"
    step = request.session.get("first_run_step", "setup_email")
    ctx = {"step": step}

    if step == "code":
        ctx["email"] = request.session.get("first_run_email", "")
        ctx["username"] = request.session.get("first_run_username", "")

    return render(request, "accounts/first_run.html", ctx)


@login_not_required
@require_http_methods(["POST"])
def first_run_setup_email(request):
    email = (request.POST.get("email") or "").strip()
    app_pw = (request.POST.get("app_password") or "").strip()

    errors = []
    if not email or "@" not in email:
        errors.append("enter your gmail address")
    if not app_pw or len(app_pw) < 12:
        errors.append("app password looks wrong — should be 16 chars")

    if errors:
        return render(request, "accounts/first_run.html", {
            "step": "setup_email",
            "errors": errors,
            "setup_email": email,
        })

    env_path = settings.BASE_DIR / ".env"
    lines = env_path.read_text().splitlines()
    keys = {
        "EMAIL_HOST": "smtp.gmail.com",
        "EMAIL_PORT": "587",
        "EMAIL_USE_TLS": "1",
        "EMAIL_HOST_USER": email,
        "EMAIL_HOST_PASSWORD": app_pw,
    }
    updated_keys = set()
    for i, line in enumerate(lines):
        for key in keys:
            if line.startswith(f"{key}="):
                lines[i] = f"{key}={keys[key]}"
                updated_keys.add(key)
                break
    for key, val in keys.items():
        if key not in updated_keys:
            lines.append(f"{key}={val}")
    env_path.write_text("\n".join(lines) + "\n")

    for k, v in keys.items():
        os.environ[k] = v

    settings.EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"

    request.session["first_run_step"] = "create"
    return redirect("accounts:first_run")


@login_not_required
@require_http_methods(["POST"])
def first_run_create(request):
    if _is_configured():
        return redirect("accounts:login")

    username = (request.POST.get("username") or "").strip()
    email = (request.POST.get("email") or "").strip()
    password = request.POST.get("password", "")
    password2 = request.POST.get("password2", "")

    errors = []
    if len(username) < 2:
        errors.append("username too short")
    if not email or "@" not in email:
        errors.append("valid email required")
    if len(password) < 4:
        errors.append("passcode must be at least 4 chars")
    if password != password2:
        errors.append("passcodes don't match")

    if errors:
        return render(request, "accounts/first_run.html", {
            "step": "create",
            "errors": errors,
            "username": username,
            "email": email,
        })

    code = VerificationCode.generate_for(email)
    _send_code(email, code.code)

    request.session["first_run_step"] = "code"
    request.session["first_run_email"] = email
    request.session["first_run_username"] = username
    request.session["first_run_password"] = password
    return render(request, "accounts/first_run.html", {
        "step": "code",
        "email": email,
        "username": username,
    })


@login_not_required
@require_http_methods(["POST"])
def first_run_resend(request):
    email = request.session.get("first_run_email", "")
    username = request.session.get("first_run_username", "")
    if email:
        code = VerificationCode.generate_for(email)
        _send_code(email, code.code)
    return render(request, "accounts/first_run.html", {
        "step": "code",
        "email": email,
        "username": username,
    })


@login_not_required
@require_http_methods(["POST"])
def first_run_verify(request):
    if _is_configured():
        return redirect("accounts:login")

    email = request.session.get("first_run_email", "")
    code = (request.POST.get("code") or "").strip().replace(" ", "")

    if not code or len(code) != 6:
        return render(request, "accounts/first_run.html", {
            "step": "code",
            "errors": ["enter the 6-digit code"],
            "email": email,
        })

    if not VerificationCode.verify(email, code):
        return render(request, "accounts/first_run.html", {
            "step": "code",
            "errors": ["invalid or expired code. try again."],
            "email": email,
            "wrong_code": True,
        })

    username = request.session.pop("first_run_username")
    email = request.session.pop("first_run_email")
    password = request.session.pop("first_run_password")

    existing = User.objects.filter(is_superuser=True).first()
    if existing:
        existing.username = username
        existing.email = email
        existing.is_staff = True
        existing.is_superuser = True
        existing.set_password(password)
        existing.save()
    else:
        try:
            User.objects.create_superuser(username=username, email=email, password=password)
        except IntegrityError:
            request.session["first_run_username"] = username
            request.session["first_run_email"] = email
            request.session["first_run_password"] = password
            return render(request, "accounts/first_run.html", {
                "step": "code",
                "errors": ["that operator id already exists. pick another."],
                "email": email,
                "username": username,
            })

    request.session.pop("first_run_step", None)
    return render(request, "accounts/first_run_success.html", {"username": username})


# -- passcode change ---------------------------------------------------

@require_http_methods(["GET", "POST"])
def passcode_change(request):
    if not request.headers.get("HX-Request"):
        return redirect("tracker:dashboard")
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


# -- forgot password via 6-digit code ----------------------------------

@login_not_required
@require_http_methods(["GET", "POST"])
def forgot_password(request):
    if not request.headers.get("HX-Request"):
        return redirect("accounts:login")

    step = request.session.get("forgot_step", "email")

    if step == "sent":
        return render(request, "accounts/_forgot_code.html", {
            "email": request.session.get("forgot_email", ""),
        })

    if step == "verified":
        if request.method == "POST":
            pw = request.POST.get("password", "")
            pw2 = request.POST.get("password2", "")
            if pw != pw2 or len(pw) < 4:
                return render(request, "accounts/_forgot_new_pw.html", {
                    "errors": ["passcodes must match and be 4+ chars"],
                })
            email = request.session.get("forgot_email", "")
            user = User.objects.filter(email=email).first()
            if user:
                user.set_password(pw)
                user.save()
            request.session.pop("forgot_step", None)
            request.session.pop("forgot_email", None)
            return render(request, "accounts/_forgot_done.html", {})
        return render(request, "accounts/_forgot_new_pw.html", {})

    # step == "email"
    if request.method == "POST":
        email = (request.POST.get("email") or "").strip()
        user = User.objects.filter(email=email).first()
        if user:
            code_obj = VerificationCode.generate_for(email)
            _send_code(email, code_obj.code)
        request.session["forgot_step"] = "sent"
        request.session["forgot_email"] = email
        return render(request, "accounts/_forgot_code.html", {"email": email})

    return render(request, "accounts/_forgot_modal.html", {})


@login_not_required
@require_http_methods(["POST"])
def forgot_verify_code(request):
    email = request.session.get("forgot_email", "")
    code = (request.POST.get("code") or "").strip().replace(" ", "")

    if not code or len(code) != 6:
        return render(request, "accounts/_forgot_code.html", {
            "email": email,
            "errors": ["enter the 6-digit code"],
        })

    if not VerificationCode.verify(email, code):
        return render(request, "accounts/_forgot_code.html", {
            "email": email,
            "errors": ["invalid or expired code"],
            "wrong_code": True,
        })

    request.session["forgot_step"] = "verified"
    return render(request, "accounts/_forgot_new_pw.html", {})
