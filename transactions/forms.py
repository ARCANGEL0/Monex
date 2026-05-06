from django import forms
from django.utils.translation import gettext_lazy as _

from .models import Transaction


class TransactionForm(forms.ModelForm):
    class Meta:
        model = Transaction
        fields = ["kind", "name", "amount", "bank", "category", "occurred_on", "notes"]
        widgets = {
            "name": forms.TextInput(attrs={"class": "input", "placeholder": _("e.g. groceries lidl"), "autocomplete": "off"}),
            "amount": forms.NumberInput(attrs={"class": "input", "step": "0.01", "min": "0.01", "inputmode": "decimal"}),
            "occurred_on": forms.DateInput(attrs={"class": "input", "type": "date"}),
            "notes": forms.Textarea(attrs={"class": "textarea", "rows": 2}),
            "bank": forms.Select(attrs={"class": "select"}),
            "category": forms.Select(attrs={"class": "select"}),
        }
