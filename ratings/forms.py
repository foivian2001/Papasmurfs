from django import forms

from .models import PackageReview


class PackageReviewForm(forms.ModelForm):
    """Validate a package rating and optional written review."""

    class Meta:
        model = PackageReview
        fields = [
            "rating",
            "review_text",
        ]
        widgets = {
            "rating": forms.HiddenInput(),
            "review_text": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 4,
                    "maxlength": 1000,
                    "placeholder": (
                        "Share your experience with this package..."
                    ),
                },
            ),
        }
