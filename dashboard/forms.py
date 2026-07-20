from django import forms
from django.contrib.auth import get_user_model

from catalogue.models import Game

from .models import UserProfile


User = get_user_model()


class UserAccountForm(forms.ModelForm):
    """Allow a user to update basic account information."""

    class Meta:
        model = User
        fields = [
            "first_name",
            "last_name",
            "email",
        ]
        widgets = {
            "first_name": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "First name",
                },
            ),
            "last_name": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Last name",
                },
            ),
            "email": forms.EmailInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Email address",
                },
            ),
        }

    def clean_email(self):
        """Prevent two accounts from using the same email address."""

        email = self.cleaned_data.get("email")

        if not email:
            return email

        existing_users = User.objects.filter(
            email__iexact=email,
        ).exclude(
            pk=self.instance.pk,
        )

        if existing_users.exists():
            raise forms.ValidationError(
                "Another account already uses this email address."
            )

        return email


class UserProfileForm(forms.ModelForm):
    """Allow a user to update their extended profile information."""

    class Meta:
        model = UserProfile
        fields = [
            "display_name",
            "bio",
            "avatar",
            "preferred_game",
        ]
        widgets = {
            "display_name": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Public display name",
                },
            ),
            "bio": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 5,
                    "placeholder": "Write a short description about yourself.",
                },
            ),
            "avatar": forms.ClearableFileInput(
                attrs={
                    "class": "form-control",
                    "accept": "image/*",
                },
            ),
            "preferred_game": forms.Select(
                attrs={
                    "class": "form-select",
                },
            ),
        }

    def __init__(self, *args, **kwargs):
        """Show only active games in the preference dropdown."""

        super().__init__(*args, **kwargs)

        self.fields["preferred_game"].queryset = (
            Game.objects.filter(
                is_active=True,
            ).order_by("name")
        )

        self.fields["preferred_game"].empty_label = (
            "No preferred game selected"
        )
