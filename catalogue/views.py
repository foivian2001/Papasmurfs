from django.shortcuts import get_object_or_404, render

from .models import BoostPackage


def package_list(request):
    """Display all active boosting packages."""

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
    """Display the details of one active boosting package."""

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

    context = {
        "package": package,
    }

    return render(
        request,
        "catalogue/package_detail.html",
        context,
    )
