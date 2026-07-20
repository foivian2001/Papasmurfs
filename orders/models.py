from decimal import Decimal

from django.conf import settings
from django.core.validators import MinValueValidator
from django.db import models

from catalogue.models import BoostPackage


class Order(models.Model):
    """Store a simulated purchase made by a registered user."""

    class Status(models.TextChoices):
        COMPLETED = "completed", "Completed"
        CANCELLED = "cancelled", "Cancelled"

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="orders",
    )

    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.COMPLETED,
    )

    total_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[
            MinValueValidator(Decimal("0.00")),
        ],
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    updated_at = models.DateTimeField(
        auto_now=True,
    )

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return (
            f"Order #{self.pk} by {self.user.username}"
        )

    @property
    def total_items(self):
        """Return the total quantity of services in this order."""

        return sum(
            item.quantity
            for item in self.items.all()
        )


class OrderItem(models.Model):
    """
    Store a snapshot of a package at the time it was purchased.

    Package details are copied into this model so order history remains
    accurate even if the original package is later changed or removed.
    """

    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name="items",
    )

    package = models.ForeignKey(
        BoostPackage,
        on_delete=models.SET_NULL,
        related_name="order_items",
        null=True,
        blank=True,
    )

    package_name = models.CharField(
        max_length=150,
    )

    game_name = models.CharField(
        max_length=100,
    )

    category_name = models.CharField(
        max_length=100,
    )

    current_rank_name = models.CharField(
        max_length=100,
    )

    target_rank_name = models.CharField(
        max_length=100,
    )

    unit_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[
            MinValueValidator(Decimal("0.00")),
        ],
    )

    quantity = models.PositiveIntegerField(
        validators=[
            MinValueValidator(1),
        ],
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    class Meta:
        ordering = ["id"]

    def __str__(self):
        return (
            f"{self.quantity} × {self.package_name} "
            f"for order #{self.order_id}"
        )

    @property
    def subtotal(self):
        """Return the saved unit price multiplied by quantity."""

        return self.unit_price * self.quantity
