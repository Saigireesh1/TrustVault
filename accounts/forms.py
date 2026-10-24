
from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm

from .models import User


class TrustVaultLoginForm(AuthenticationForm):
    username = forms.CharField(
        widget=forms.TextInput(attrs={
            "class": "form-control",
            "autocomplete": "username",
        })
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            "class": "form-control",
            "autocomplete": "current-password",
        })
    )


class RegistrationForm(UserCreationForm):
    class Meta:
        model = User
        fields = ("username",)

    def save(self, commit=True):
        user = super().save(commit=False)
        user.role = User.Role.VIEWER
        user.is_active = False

        if commit:
            user.save()

        return user
