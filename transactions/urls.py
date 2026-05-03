from django.urls import path

from . import views

app_name = "transactions"

urlpatterns = [
    path("", views.transaction_list, name="list"),
    path("new/", views.transaction_create, name="create"),
    path("<int:pk>/edit/", views.transaction_edit, name="edit"),
    path("<int:pk>/delete/", views.transaction_delete, name="delete"),
    path("export.csv", views.transaction_csv, name="csv"),
    path("export.pdf", views.transaction_pdf, name="pdf"),
]
