from django import forms

from catalogue.models import Game, Rank, ServiceCategory


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

class RankForm(forms.ModelForm):
    """Form used by staff to create and update competitive ranks."""

    class Meta:
        model = Rank
        fields = [
            "game",
            "name",
            "rank_order",
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
                    "placeholder": "Example: Gold",
                },
            ),
            "rank_order": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "min": 1,
                    "placeholder": "Example: 4",
                },
            ),
        }

    def clean(self):
        """Prevent duplicate rank names and ordering values per game."""

        cleaned_data = super().clean()

        game = cleaned_data.get("game")
        name = cleaned_data.get("name")
        rank_order = cleaned_data.get("rank_order")

        if not game:
            return cleaned_data

        ranks = Rank.objects.filter(game=game)

        if self.instance.pk:
            ranks = ranks.exclude(pk=self.instance.pk)

        if name and ranks.filter(name__iexact=name).exists():
            self.add_error(
                "name",
                "A rank with this name already exists for the selected game.",
            )

        if (
            rank_order is not None
            and ranks.filter(rank_order=rank_order).exists()
        ):
            self.add_error(
                "rank_order",
                "This order number is already used by another rank "
                "for the selected game.",
            )

        return cleaned_data
