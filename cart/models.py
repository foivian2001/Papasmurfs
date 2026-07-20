from decimal import Decimal

from django.conf import settings
from django.core.validators import MinValueValidator
from django.db import models

from catalogue.models import BoostPackage


class Cart(models.Model):
    """Store the active shopping cart belonging to one user."""

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="shopping_cart",
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    updated_at = models.DateTimeField(
        auto_now=True,
    )

    class Meta:
        ordering = ["-updated_at"]

    def __str__(self):
        return f"{self.user.username}'s cart"

    @property
    def total_items(self):
        """Return the total quantity of services in the cart."""

        return sum(
            item.quantity
            for item in self.items.all()
        )

    @property
    def total_price(self):
        """Return the combined price of every cart item."""

        return sum(
            (
                item.subtotal
                for item in self.items.select_related("package")
            ),
            Decimal("0.00"),
        )


class CartItem(models.Model):
    """Connect one boost package to a user's shopping cart."""

    cart = models.ForeignKey(
        Cart,
        on_delete=models.CASCADE,
        related_name="items",
    )

    package = models.ForeignKey(
        BoostPackage,
        on_delete=models.CASCADE,
        related_name="cart_items",
    )

    quantity = models.PositiveIntegerField(
        default=1,
        validators=[
            MinValueValidator(1),
        ],
    )

    added_at = models.DateTimeField(
        auto_now_add=True,
    )

    updated_at = models.DateTimeField(
        auto_now=True,
    )

    class Meta:
        ordering = ["added_at"]

        constraints = [
            models.UniqueConstraint(
                fields=[
                    "cart",
                    "package",
                ],
                name="unique_package_per_cart",
            ),
        ]

    def __str__(self):
        return (
            f"{self.quantity} × {self.package.name} "
            f"in {self.cart.user.username}'s cart"
        )

    @property
    def subtotal(self):
        """Return the package price multiplied by its quantity."""

        return self.package.price * self.quantity
