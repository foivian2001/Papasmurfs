from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from .models import SearchHistory
from .services import get_recommended_packages


@login_required(login_url="accounts:login")
def recommendation_list(request):
    """Display personalised package recommendations."""

    recommendations = get_recommended_packages(
        request.user,
        limit=12,
    )

    recent_searches = (
        SearchHistory.objects
        .filter(user=request.user)
        .select_related(
            "game",
            "category",
            "current_rank",
            "target_rank",
        )[:5]
    )

    context = {
        "recommendations": recommendations,
        "recent_searches": recent_searches,
    }

    return render(
        request,
        "recommendations/recommendation_list.html",
        context,
    )
