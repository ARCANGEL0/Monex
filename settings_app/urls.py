from django.urls import path

from . import views

app_name = "settings_app"

urlpatterns = [
    path("", views.home, name="home"),
    path("budget/save/", views.budget_save, name="budget_save"),
    path("banks/new/", views.bank_create, name="bank_create"),
    path("banks/<int:pk>/edit/", views.bank_edit, name="bank_edit"),
    path("banks/<int:pk>/delete/", views.bank_delete, name="bank_delete"),
    path("categories/new/", views.category_create, name="cat_create"),
    path("categories/<int:pk>/edit/", views.category_edit, name="cat_edit"),
    path("categories/<int:pk>/delete/", views.category_delete, name="cat_delete"),
    path("users/new/", views.user_create, name="user_create"),
    path("users/<int:pk>/edit/", views.user_edit, name="user_edit"),
    path("users/<int:pk>/delete/", views.user_delete, name="user_delete"),
]
