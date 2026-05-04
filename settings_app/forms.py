from django import forms

from transactions.models import Bank, Category


class BankForm(forms.ModelForm):
    class Meta:
        model = Bank
        fields = ["name", "color", "archived"]
        widgets = {
            "name": forms.TextInput(attrs={"class": "input"}),
            "color": forms.TextInput(attrs={"class": "input", "type": "color"}),
        }


class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ["name", "kind", "color", "archived"]
        widgets = {
            "name": forms.TextInput(attrs={"class": "input"}),
            "color": forms.TextInput(attrs={"class": "input", "type": "color"}),
        }
