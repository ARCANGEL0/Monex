from django.contrib import admin

from . import models


@admin.register(models.RecurringTransaction)
class RecurringAdmin(admin.ModelAdmin):
    list_display = ("name", "kind", "amount", "day_of_month", "bank", "category", "active", "last_materialized_on")
    list_filter = ("active", "kind", "bank")
    search_fields = ("name",)
