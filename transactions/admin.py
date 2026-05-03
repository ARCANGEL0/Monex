from django.contrib import admin

from . import models


@admin.register(models.Bank)
class BankAdmin(admin.ModelAdmin):
    list_display = ("name", "color", "archived")
    list_filter = ("archived",)


@admin.register(models.Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "kind", "color", "archived")
    list_filter = ("kind", "archived")


@admin.register(models.Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ("occurred_on", "name", "kind", "amount", "bank", "category")
    list_filter = ("kind", "bank", "category", "occurred_on")
    search_fields = ("name", "notes")
    date_hierarchy = "occurred_on"


@admin.register(models.Budget)
class BudgetAdmin(admin.ModelAdmin):
    list_display = ("month", "overall_cap")


@admin.register(models.CategoryBudget)
class CategoryBudgetAdmin(admin.ModelAdmin):
    list_display = ("month", "category", "cap")
    list_filter = ("month", "category")
