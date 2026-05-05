from django.contrib.auth.views import LogoutView
from django.urls import path

from . import views

app_name = "accounts"

urlpatterns = [
    path("login/", views.LoginView.as_view(), name="login"),
    path("logout/", LogoutView.as_view(), name="logout"),
    path("first-run/", views.first_run, name="first_run"),
    path("first-run/setup-email/", views.first_run_setup_email, name="first_run_setup_email"),
    path("first-run/create/", views.first_run_create, name="first_run_create"),
    path("first-run/resend/", views.first_run_resend, name="first_run_resend"),
    path("first-run/verify/", views.first_run_verify, name="first_run_verify"),
    path("passcode/", views.passcode_change, name="passcode"),
    path("forgot/", views.forgot_password, name="forgot"),
    path("forgot/verify/", views.forgot_verify_code, name="forgot_verify"),
]
