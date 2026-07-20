from django import forms

from catalogue.models import Game, Rank, ServiceCategory


class PackageSearchForm(forms.Form):
    """Search and filter active boost packages."""

    query = forms.CharField(
        required=False,
        label="Search",
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "placeholder": (
                    "Search package name, game or description..."
                ),
            },
        ),
    )

    game = forms.ModelChoiceField(
        queryset=Game.objects.filter(is_active=True),
        required=False,
        empty_label="All games",
        widget=forms.Select(
            attrs={
                "class": "form-select",
            },
        ),
    )

    category = forms.ModelChoiceField(
        queryset=ServiceCategory.objects.select_related("game"),
        required=False,
        empty_label="All service categories",
        widget=forms.Select(
            attrs={
                "class": "form-select",
            },
        ),
    )

    current_rank = forms.ModelChoiceField(
        queryset=Rank.objects.select_related("game"),
        required=False,
        empty_label="Any current rank",
        widget=forms.Select(
            attrs={
                "class": "form-select",
            },
        ),
    )

    target_rank = forms.ModelChoiceField(
        queryset=Rank.objects.select_related("game"),
        required=False,
        empty_label="Any target rank",
        widget=forms.Select(
            attrs={
                "class": "form-select",
            },
        ),
    )

    minimum_price = forms.DecimalField(
        required=False,
        min_value=0,
        decimal_places=2,
        label="Minimum price",
        widget=forms.NumberInput(
            attrs={
                "class": "form-control",
                "placeholder": "0.00",
                "step": "0.01",
            },
        ),
    )

    maximum_price = forms.DecimalField(
        required=False,
        min_value=0,
        decimal_places=2,
        label="Maximum price",
        widget=forms.NumberInput(
            attrs={
                "class": "form-control",
                "placeholder": "100.00",
                "step": "0.01",
            },
        ),
    )

    maximum_days = forms.IntegerField(
        required=False,
        min_value=1,
        label="Maximum completion time",
        widget=forms.NumberInput(
            attrs={
                "class": "form-control",
                "placeholder": "Example: 3",
                "min": 1,
            },
        ),
    )

    featured_only = forms.BooleanField(
        required=False,
        label="Featured packages only",
        widget=forms.CheckboxInput(
            attrs={
                "class": "form-check-input",
            },
        ),
    )

    def clean(self):
        """Validate the selected price range."""

        cleaned_data = super().clean()

        minimum_price = cleaned_data.get("minimum_price")
        maximum_price = cleaned_data.get("maximum_price")

        if (
            minimum_price is not None
            and maximum_price is not None
            and minimum_price > maximum_price
        ):
            self.add_error(
                "maximum_price",
                "Maximum price must be greater than minimum price.",
            )

        return cleaned_data
