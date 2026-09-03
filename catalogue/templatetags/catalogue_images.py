import cloudinary

from django import template
from django.templatetags.static import static


register = template.Library()


GAME_FALLBACKS = {
    "League of Legends": "images/games/league-of-legends.png",
    "Counter-Strike 2": "images/games/counter-strike-2.png",
    "Fortnite": "images/games/fortnite.png",
    "GTA Online": "images/games/gta-online.png",
}


def get_game(obj):
    """Return the game connected to a game or package object."""

    if obj is None:
        return None

    if hasattr(obj, "category"):
        category = getattr(obj, "category", None)

        if category is not None:
            return getattr(category, "game", None)

    return obj


@register.simple_tag
def catalogue_image_url(obj):
    """
    Return a Cloudinary image when Cloudinary is configured.

    Fresh/local installations fall back to bundled static
    game images so the catalogue still looks complete.
    """

    if obj is None:
        return ""

    game = get_game(obj)

    cloud_name = cloudinary.config().cloud_name

    image = getattr(obj, "image", None)

    if cloud_name and image:
        try:
            return image.url
        except (ValueError, AttributeError):
            pass

    if cloud_name and game is not None and game is not obj:
        game_image = getattr(game, "image", None)

        if game_image:
            try:
                return game_image.url
            except (ValueError, AttributeError):
                pass

    if game is None:
        return ""

    fallback = GAME_FALLBACKS.get(
        getattr(game, "name", "")
    )

    if not fallback:
        return ""

    return static(fallback)
