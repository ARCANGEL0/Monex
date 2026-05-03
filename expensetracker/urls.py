from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("admin/", admin.site.urls),
    path("accounts/", include("accounts.urls", namespace="accounts")),
    path("transactions/", include("transactions.urls", namespace="transactions")),
    path("", include("dashboard.urls", namespace="dashboard")),
]
