from django.contrib.auth.decorators import login_required
from django.db.models import Avg, Count
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.views.decorators.http import require_POST

from catalogue.models import BoostPackage
from orders.models import Order, OrderItem

from .forms import PackageReviewForm
from .models import PackageReview


@login_required(login_url="accounts:login")
@require_POST
def submit_review(request, package_id):
    """
    Create or update a package review through AJAX.

    Only users who completed an order containing this
    package are allowed to submit a review.
    """

    package = get_object_or_404(
        BoostPackage.objects.select_related(
            "category",
            "category__game",
        ),
        id=package_id,
        is_active=True,
        category__game__is_active=True,
    )

    # --------------------------------------------------------
    # VERIFIED CUSTOMER CHECK
    # --------------------------------------------------------

    has_completed_purchase = OrderItem.objects.filter(
        order__user=request.user,
        order__status=Order.Status.COMPLETED,
        package=package,
    ).exists()

    if not has_completed_purchase:
        return JsonResponse(
            {
                "success": False,
                "message": (
                    "You can review this service only after "
                    "completing an order that contains it."
                ),
            },
            status=403,
        )

    # --------------------------------------------------------
    # REVIEW FORM
    # --------------------------------------------------------

    form = PackageReviewForm(request.POST)

    if not form.is_valid():
        return JsonResponse(
            {
                "success": False,
                "message": (
                    "Please choose a rating between 1 and 5 stars."
                ),
                "errors": form.errors.get_json_data(),
            },
            status=400,
        )

    review, created = PackageReview.objects.update_or_create(
        user=request.user,
        package=package,
        defaults={
            "rating": form.cleaned_data["rating"],
            "review_text": form.cleaned_data["review_text"],
        },
    )

    statistics = PackageReview.objects.filter(
        package=package,
    ).aggregate(
        average_rating=Avg("rating"),
        review_count=Count("id"),
    )

    average_rating = (
        statistics["average_rating"]
        or 0
    )

    if created:
        message = (
            "Your review was submitted successfully."
        )
    else:
        message = (
            "Your review was updated successfully."
        )

    return JsonResponse(
        {
            "success": True,
            "message": message,
            "average_rating": round(
                float(average_rating),
                1,
            ),
            "review_count": statistics["review_count"],
            "review": {
                "user_id": request.user.id,
                "username": request.user.username,
                "rating": review.rating,
                "review_text": review.review_text,
                "updated_at": review.updated_at.strftime(
                    "%d %B %Y, %H:%M"
                ),
            },
        }
    )
