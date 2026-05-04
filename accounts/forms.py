from django import forms


class PasscodeForm(forms.Form):
    current_password = forms.CharField(
        widget=forms.PasswordInput(attrs={"class": "input", "autocomplete": "current-password"}),
        label="current passcode",
    )
    new_password = forms.CharField(
        widget=forms.PasswordInput(attrs={"class": "input", "autocomplete": "new-password"}),
        label="new passcode",
        min_length=4,
    )
    confirm_password = forms.CharField(
        widget=forms.PasswordInput(attrs={"class": "input", "autocomplete": "new-password"}),
        label="confirm passcode",
    )

    def __init__(self, user, *args, **kwargs):
        self.user = user
        super().__init__(*args, **kwargs)

    def clean_current_password(self):
        cp = self.cleaned_data.get("current_password")
        if not self.user.check_password(cp):
            raise forms.ValidationError("incorrect current passcode")
        return cp

    def clean(self):
        data = super().clean()
        if data.get("new_password") and data.get("confirm_password"):
            if data["new_password"] != data["confirm_password"]:
                self.add_error("confirm_password", "passcodes do not match")
        return data

    def save(self):
        self.user.set_password(self.cleaned_data["new_password"])
        self.user.save()
        return self.user
