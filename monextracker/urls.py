from django.contrib import admin
from django.conf.urls.i18n import set_language
from django.urls import include, path
from django.shortcuts import redirect

urlpatterns = [
    path("i18n/setlang/", set_language, name="set_language"),
    # auth entry (unavoidable)
    path("accounts/", include("accounts.urls", namespace="accounts")),

    # htmx-only internal endpoints — reject direct visits
    path("_/d/", include("dashboard.urls", namespace="dashboard")),
    path("_/t/", include("transactions.urls", namespace="transactions")),
    path("_/a/", include("analytics.urls", namespace="analytics")),
    path("_/r/", include("recurring.urls", namespace="recurring")),
    path("_/s/", include("settings_app.urls", namespace="settings_app")),

    # everything else → root
    path("", include("core.urls", namespace="core")),
    path("admin/", lambda r: redirect("core:root")),
]
