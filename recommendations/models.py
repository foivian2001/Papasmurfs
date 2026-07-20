from django.conf import settings
from django.db import models

from catalogue.models import Game, Rank, ServiceCategory


class SearchHistory(models.Model):
    """Store search criteria used by an authenticated user."""

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="search_history",
    )

    query = models.CharField(
        max_length=200,
        blank=True,
    )

    game = models.ForeignKey(
        Game,
        on_delete=models.SET_NULL,
        related_name="search_history_entries",
        null=True,
        blank=True,
    )

    category = models.ForeignKey(
        ServiceCategory,
        on_delete=models.SET_NULL,
        related_name="search_history_entries",
        null=True,
        blank=True,
    )

    current_rank = models.ForeignKey(
        Rank,
        on_delete=models.SET_NULL,
        related_name="current_rank_searches",
        null=True,
        blank=True,
    )

    target_rank = models.ForeignKey(
        Rank,
        on_delete=models.SET_NULL,
        related_name="target_rank_searches",
        null=True,
        blank=True,
    )

    minimum_price = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        null=True,
        blank=True,
    )

    maximum_price = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        null=True,
        blank=True,
    )

    maximum_days = models.PositiveIntegerField(
        null=True,
        blank=True,
    )

    featured_only = models.BooleanField(
        default=False,
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        search_description = self.query or "Filtered search"

        return (
            f"{self.user.username}: "
            f"{search_description}"
        )

    @property
    def has_search_criteria(self):
        """Return whether the entry contains meaningful search criteria."""

        return any(
            [
                self.query,
                self.game_id,
                self.category_id,
                self.current_rank_id,
                self.target_rank_id,
                self.minimum_price is not None,
                self.maximum_price is not None,
                self.maximum_days is not None,
                self.featured_only,
            ]
        )
