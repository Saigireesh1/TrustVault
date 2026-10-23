
from django import forms
from django.contrib.auth import get_user_model

from .models import Document, DocumentGrant

User = get_user_model()


class UploadDocumentForm(forms.Form):
    title = forms.CharField(
        max_length=200,
        widget=forms.TextInput(
            attrs={"class": "form-control"}
        ),
    )

    category = forms.CharField(
        max_length=80,
        widget=forms.TextInput(
            attrs={"class": "form-control"}
        ),
    )

    file = forms.FileField(
        widget=forms.ClearableFileInput(
            attrs={"class": "form-control"}
        ),
    )


class DocumentEditForm(forms.ModelForm):
    class Meta:
        model = Document
        fields = ["title", "category"]
        widgets = {
            "title": forms.TextInput(
                attrs={"class": "form-control"}
            ),
            "category": forms.TextInput(
                attrs={"class": "form-control"}
            ),
        }


class GrantForm(forms.Form):
    user = forms.ModelChoiceField(
        queryset=User.objects.filter(is_active=True),
        widget=forms.Select(
            attrs={"class": "form-select"}
        ),
        label="Select user",
    )

    permission = forms.ChoiceField(
        choices=DocumentGrant.Permission.choices,
        widget=forms.Select(
            attrs={"class": "form-select"}
        ),
        label="Permission",
    )
