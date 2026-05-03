from django.urls import path

from . import views

app_name = "recurring"

urlpatterns = [
    path("", views.home, name="list"),
    path("new/", views.create, name="create"),
    path("<int:pk>/edit/", views.edit, name="edit"),
    path("<int:pk>/delete/", views.delete, name="delete"),
]
