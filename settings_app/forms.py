from django import forms
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _

from transactions.models import Bank, Category

User = get_user_model()


class OperatorForm(forms.ModelForm):
    password = forms.CharField(
        required=False,
        widget=forms.PasswordInput(attrs={"class": "input", "autocomplete": "new-password"}),
        help_text=_("leave blank to keep existing passcode"),
    )

    class Meta:
        model = User
        fields = ["username", "email", "is_superuser", "password"]
        widgets = {
            "username": forms.TextInput(attrs={"class": "input", "autocomplete": "off"}),
            "email": forms.EmailInput(attrs={"class": "input", "autocomplete": "off"}),
        }

    def __init__(self, *args, creating=False, **kwargs):
        super().__init__(*args, **kwargs)
        self.creating = creating
        if creating:
            self.fields["password"].required = True
            self.fields["password"].help_text = ""

    def save(self, commit=True):
        user = super().save(commit=False)
        password = self.cleaned_data.get("password")
        if password:
            user.set_password(password)
        if commit:
            user.save()
        return user


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
