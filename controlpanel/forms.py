from django import forms

from catalogue.models import Game, ServiceCategory


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

class ServiceCategoryForm(forms.ModelForm):
    """Form used by staff to create and update service categories."""

    class Meta:
        model = ServiceCategory
        fields = [
            "game",
            "name",
            "description",
        ]
        widgets = {
            "game": forms.Select(
                attrs={
                    "class": "form-select",
                },
            ),
            "name": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Example: Solo/Duo Boost",
                },
            ),
            "description": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 4,
                    "placeholder": "Describe this type of boosting service.",
                },
            ),
        }
