from django.db.models import Avg, Count
from django.shortcuts import get_object_or_404, render

from .models import BoostPackage


def package_list(request):
    """Display all active public boost packages."""

    packages = (
        BoostPackage.objects
        .filter(
            is_active=True,
            category__game__is_active=True,
        )
        .select_related(
            "category",
            "category__game",
            "current_rank",
            "target_rank",
        )
        .order_by(
            "category__game__name",
            "price",
        )
    )

    context = {
        "packages": packages,
    }

    return render(
        request,
        "catalogue/package_list.html",
        context,
    )


def package_detail(request, package_id):
    """Display one active package and its customer reviews."""

    package = get_object_or_404(
        BoostPackage.objects.select_related(
            "category",
            "category__game",
            "current_rank",
            "target_rank",
        ),
        id=package_id,
        is_active=True,
        category__game__is_active=True,
    )

    reviews = package.reviews.select_related(
        "user",
    ).all()

    statistics = reviews.aggregate(
        average_rating=Avg("rating"),
        review_count=Count("id"),
    )

    average_rating = statistics["average_rating"] or 0
    review_count = statistics["review_count"]

    user_review = None

    if request.user.is_authenticated:
        user_review = reviews.filter(
            user=request.user,
        ).first()

    context = {
        "package": package,
        "reviews": reviews,
        "average_rating": average_rating,
        "review_count": review_count,
        "user_review": user_review,
    }

    return render(
        request,
        "catalogue/package_detail.html",
        context,
    )
