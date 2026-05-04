from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("admin/", admin.site.urls),
    path("accounts/", include("accounts.urls", namespace="accounts")),
    path("transactions/", include("transactions.urls", namespace="transactions")),
    path("analytics/", include("analytics.urls", namespace="analytics")),
    path("recurring/", include("recurring.urls", namespace="recurring")),
    path("settings/", include("settings_app.urls", namespace="settings_app")),
    path("", include("dashboard.urls", namespace="dashboard")),
]
