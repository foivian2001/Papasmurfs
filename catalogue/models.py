from cloudinary.models import CloudinaryField
from django.core.exceptions import ValidationError
from django.db import models


class Game(models.Model):
    """A competitive game available on the Papasmurfs platform."""

    name = models.CharField(max_length=100, unique=True)
    description = models.TextField()

    image = CloudinaryField(
        "image",
        folder="papasmurfs/games",
    )

    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


class ServiceCategory(models.Model):
    """A service category belonging to a particular game."""

    game = models.ForeignKey(
        Game,
        on_delete=models.CASCADE,
        related_name="service_categories",
    )

    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)

    class Meta:
        ordering = ["game__name", "name"]

        constraints = [
            models.UniqueConstraint(
                fields=["game", "name"],
                name="unique_service_category_per_game",
            ),
        ]

    def __str__(self):
        return f"{self.game.name} - {self.name}"


class Rank(models.Model):
    """A competitive rank belonging to a particular game."""

    game = models.ForeignKey(
        Game,
        on_delete=models.CASCADE,
        related_name="ranks",
    )

    name = models.CharField(max_length=100)
    rank_order = models.PositiveIntegerField()

    class Meta:
        ordering = ["game__name", "rank_order"]

        constraints = [
            models.UniqueConstraint(
                fields=["game", "name"],
                name="unique_rank_name_per_game",
            ),
            models.UniqueConstraint(
                fields=["game", "rank_order"],
                name="unique_rank_order_per_game",
            ),
        ]

    def __str__(self):
        return f"{self.game.name} - {self.name}"


class BoostPackage(models.Model):
    """A purchasable rank-boosting package."""

    category = models.ForeignKey(
        ServiceCategory,
        on_delete=models.CASCADE,
        related_name="packages",
    )

    current_rank = models.ForeignKey(
        Rank,
        on_delete=models.PROTECT,
        related_name="packages_starting_here",
    )

    target_rank = models.ForeignKey(
        Rank,
        on_delete=models.PROTECT,
        related_name="packages_ending_here",
    )

    name = models.CharField(max_length=150)
    description = models.TextField()

    price = models.DecimalField(
        max_digits=8,
        decimal_places=2,
    )

    estimated_days = models.PositiveIntegerField()

    image = CloudinaryField(
        "image",
        folder="papasmurfs/packages",
        blank=True,
    )

    is_featured = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["category__game__name", "price"]

    def clean(self):
        """Validate that package ranks belong to the correct game."""

        errors = {}

        if self.category_id and self.current_rank_id:
            if self.current_rank.game_id != self.category.game_id:
                errors["current_rank"] = (
                    "The current rank must belong to the selected game."
                )

        if self.category_id and self.target_rank_id:
            if self.target_rank.game_id != self.category.game_id:
                errors["target_rank"] = (
                    "The target rank must belong to the selected game."
                )

        if self.current_rank_id and self.target_rank_id:
            if self.current_rank.game_id == self.target_rank.game_id:
                if (
                    self.current_rank.rank_order
                    >= self.target_rank.rank_order
                ):
                    errors["target_rank"] = (
                        "The target rank must be higher "
                        "than the current rank."
                    )

        if errors:
            raise ValidationError(errors)

    def __str__(self):
        return self.name
    