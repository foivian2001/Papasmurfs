from django.contrib.auth import get_user_model
from django.shortcuts import render

from catalogue.models import (
    BoostPackage,
    Game,
    Rank,
    ServiceCategory,
)

from .decorators import staff_required


@staff_required
def dashboard(request):
    """Display statistics and management options for staff members."""

    user_model = get_user_model()

    context = {
        "game_count": Game.objects.count(),
        "category_count": ServiceCategory.objects.count(),
        "rank_count": Rank.objects.count(),
        "package_count": BoostPackage.objects.count(),
        "user_count": user_model.objects.count(),
    }

    return render(
        request,
        "controlpanel/dashboard.html",
        context,
    )
