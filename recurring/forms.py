from django import forms
from django.utils.translation import gettext_lazy as _

from .models import RecurringTransaction


class RecurringForm(forms.ModelForm):
    class Meta:
        model = RecurringTransaction
        fields = ["kind", "name", "amount", "bank", "category", "day_of_month", "active", "notes"]
        widgets = {
            "name": forms.TextInput(attrs={"class": "input", "placeholder": _("e.g. spotify")}),
            "amount": forms.NumberInput(attrs={"class": "input", "step": "0.01", "min": "0.01", "inputmode": "decimal"}),
            "day_of_month": forms.NumberInput(attrs={"class": "input", "min": 1, "max": 28}),
            "bank": forms.Select(attrs={"class": "select"}),
            "category": forms.Select(attrs={"class": "select"}),
            "notes": forms.Textarea(attrs={"class": "textarea", "rows": 2}),
        }
