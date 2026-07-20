from django import forms


class CartItemQuantityForm(forms.Form):
    """Validate the quantity selected for a cart item."""

    quantity = forms.IntegerField(
        min_value=1,
        max_value=10,
        widget=forms.NumberInput(
            attrs={
                "class": "form-control cart-quantity-input",
                "min": 1,
                "max": 10,
            },
        ),
    )
