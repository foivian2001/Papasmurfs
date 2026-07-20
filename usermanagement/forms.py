from django import forms
from django.contrib.auth import get_user_model


User = get_user_model()


class StaffUserForm(forms.ModelForm):
    """Allow administrators to update a registered user."""

    class Meta:
        model = User
        fields = [
            "first_name",
            "last_name",
            "email",
            "is_active",
            "is_staff",
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
            "is_active": forms.CheckboxInput(
                attrs={
                    "class": "form-check-input",
                },
            ),
            "is_staff": forms.CheckboxInput(
                attrs={
                    "class": "form-check-input",
                },
            ),
        }

    def clean_email(self):
        """Prevent duplicate email addresses."""

        email = self.cleaned_data.get("email")

        if not email:
            return email

        duplicate_users = User.objects.filter(
            email__iexact=email,
        ).exclude(
            pk=self.instance.pk,
        )

        if duplicate_users.exists():
            raise forms.ValidationError(
                "Another user already uses this email address."
            )

        return email
