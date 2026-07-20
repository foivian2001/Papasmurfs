from django.db.models import Q
from django.shortcuts import render

from catalogue.models import BoostPackage
from recommendations.services import record_search

from .forms import PackageSearchForm


def package_search(request):
    """Search and filter active public boost packages."""

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

    form = PackageSearchForm(request.GET or None)

    if form.is_valid():
        query = form.cleaned_data.get("query")
        game = form.cleaned_data.get("game")
        category = form.cleaned_data.get("category")
        current_rank = form.cleaned_data.get("current_rank")
        target_rank = form.cleaned_data.get("target_rank")
        minimum_price = form.cleaned_data.get("minimum_price")
        maximum_price = form.cleaned_data.get("maximum_price")
        maximum_days = form.cleaned_data.get("maximum_days")
        featured_only = form.cleaned_data.get("featured_only")

        if request.GET:
            record_search(
                request.user,
                form.cleaned_data,
            )

        if query:
            packages = packages.filter(
                Q(name__icontains=query)
                | Q(description__icontains=query)
                | Q(category__name__icontains=query)
                | Q(category__game__name__icontains=query)
                | Q(current_rank__name__icontains=query)
                | Q(target_rank__name__icontains=query)
            )

        if game:
            packages = packages.filter(
                category__game=game,
            )

        if category:
            packages = packages.filter(
                category=category,
            )

        if current_rank:
            packages = packages.filter(
                current_rank=current_rank,
            )

        if target_rank:
            packages = packages.filter(
                target_rank=target_rank,
            )

        if minimum_price is not None:
            packages = packages.filter(
                price__gte=minimum_price,
            )

        if maximum_price is not None:
            packages = packages.filter(
                price__lte=maximum_price,
            )

        if maximum_days is not None:
            packages = packages.filter(
                estimated_days__lte=maximum_days,
            )

        if featured_only:
            packages = packages.filter(
                is_featured=True,
            )

    packages = packages.order_by(
        "category__game__name",
        "price",
    )

    context = {
        "form": form,
        "packages": packages,
        "result_count": packages.count(),
    }

    return render(
        request,
        "searchapp/package_search.html",
        context,
    )
