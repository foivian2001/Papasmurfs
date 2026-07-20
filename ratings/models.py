from django.conf import settings
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

from catalogue.models import BoostPackage


class PackageReview(models.Model):
    """Store one user's rating and optional review for a package."""

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="package_reviews",
    )

    package = models.ForeignKey(
        BoostPackage,
        on_delete=models.CASCADE,
        related_name="reviews",
    )

    rating = models.PositiveSmallIntegerField(
        validators=[
            MinValueValidator(1),
            MaxValueValidator(5),
        ],
    )

    review_text = models.TextField(
        blank=True,
        max_length=1000,
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    updated_at = models.DateTimeField(
        auto_now=True,
    )

    class Meta:
        ordering = ["-updated_at"]

        constraints = [
            models.UniqueConstraint(
                fields=[
                    "user",
                    "package",
                ],
                name="unique_user_review_per_package",
            ),
        ]

    def __str__(self):
        return (
            f"{self.user.username} rated "
            f"{self.package.name} {self.rating}/5"
        )
