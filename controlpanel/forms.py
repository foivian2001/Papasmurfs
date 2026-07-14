from django import forms

from catalogue.models import Game


class GameForm(forms.ModelForm):
    """Form used by staff to create and update catalogue games."""

    class Meta:
        model = Game
        fields = [
            "name",
            "description",
            "image",
            "is_active",
        ]
        widgets = {
            "name": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Example: League of Legends",
                },
            ),
            "description": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 5,
                    "placeholder": "Describe the game and available services.",
                },
            ),
            "image": forms.ClearableFileInput(
                attrs={
                    "class": "form-control",
                    "accept": "image/*",
                },
            ),
            "is_active": forms.CheckboxInput(
                attrs={
                    "class": "form-check-input",
                },
            ),
        }
