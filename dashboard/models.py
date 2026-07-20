from django.conf import settings
from django.db import models

from catalogue.models import Game


class UserProfile(models.Model):
    """Store additional information for a registered user."""

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="profile",
    )

    display_name = models.CharField(
        max_length=100,
        blank=True,
    )

    bio = models.TextField(
        blank=True,
    )

    avatar = models.ImageField(
        upload_to="profiles/",
        blank=True,
    )

    preferred_game = models.ForeignKey(
        Game,
        on_delete=models.SET_NULL,
        related_name="preferred_by_users",
        null=True,
        blank=True,
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    updated_at = models.DateTimeField(
        auto_now=True,
    )

    class Meta:
        ordering = ["user__username"]

    def __str__(self):
        return f"{self.user.username}'s profile"
