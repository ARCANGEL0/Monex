from django.contrib.auth.views import LogoutView
from django.urls import path

from . import views

app_name = "accounts"

urlpatterns = [
    path("login/", views.LoginView.as_view(), name="login"),
    path("logout/", LogoutView.as_view(), name="logout"),
    path("passcode/", views.passcode_change, name="passcode"),
    path("forgot/", views.forgot_password, name="forgot"),
    path("reset/<uidb64>/<token>/", views.AdamPasswordResetConfirmView.as_view(), name="password_reset_confirm"),
    path("reset/done/", views.AdamPasswordResetCompleteView.as_view(), name="password_reset_complete"),
]
