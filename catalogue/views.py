from decimal import Decimal, InvalidOperation

from django.core.paginator import Paginator
from django.db.models import Avg, Count
from django.shortcuts import get_object_or_404, render

from .models import (
    BoostPackage,
    Game,
    Rank,
    ServiceCategory,
)


def package_list(request):
    """
    Public Services catalogue.

    The Services page is designed for browsing:
    Game -> Category -> Rank progression -> Price / Time.

    Only active packages belonging to active games
    are shown to customers.
    """

    base_packages = (
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

    games = (
        Game.objects
        .filter(is_active=True)
        .order_by("name")
    )

    categories = (
        ServiceCategory.objects
        .select_related("game")
        .filter(game__is_active=True)
        .order_by(
            "game__name",
            "name",
        )
    )

    ranks = (
        Rank.objects
        .select_related("game")
        .filter(game__is_active=True)
        .order_by(
            "game__name",
            "rank_order",
        )
    )

    # --------------------------------------------------------
    # READ FILTERS
    # --------------------------------------------------------

    game_id = request.GET.get(
        "game",
        "",
    )

    category_id = request.GET.get(
        "category",
        "",
    )

    current_rank_id = request.GET.get(
        "current_rank",
        "",
    )

    target_rank_id = request.GET.get(
        "target_rank",
        "",
    )

    max_price = request.GET.get(
        "max_price",
        "",
    ).strip()

    max_days = request.GET.get(
        "max_days",
        "",
    ).strip()

    sort = request.GET.get(
        "sort",
        "recommended",
    )

    # --------------------------------------------------------
    # SELECTED GAME
    # --------------------------------------------------------

    selected_game = None

    if game_id:
        selected_game = (
            games
            .filter(id=game_id)
            .first()
        )

    # --------------------------------------------------------
    # FEATURED PACKAGES
    # --------------------------------------------------------

    featured_packages = (
        base_packages
        .filter(is_featured=True)
        .order_by(
            "category__game__name",
            "price",
        )[:6]
    )

    # --------------------------------------------------------
    # MAIN CATALOGUE QUERY
    # --------------------------------------------------------

    packages = base_packages

    if selected_game:
        packages = packages.filter(
            category__game=selected_game
        )

        categories = categories.filter(
            game=selected_game
        )

        ranks = ranks.filter(
            game=selected_game
        )

    if category_id:
        packages = packages.filter(
            category_id=category_id
        )

    if current_rank_id:
        packages = packages.filter(
            current_rank_id=current_rank_id
        )

    if target_rank_id:
        packages = packages.filter(
            target_rank_id=target_rank_id
        )

    # --------------------------------------------------------
    # PRICE FILTER
    # --------------------------------------------------------

    if max_price:

        try:
            price_value = Decimal(max_price)

            if price_value >= 0:
                packages = packages.filter(
                    price__lte=price_value
                )

        except InvalidOperation:
            pass

    # --------------------------------------------------------
    # COMPLETION TIME FILTER
    # --------------------------------------------------------

    if max_days:

        try:
            days_value = int(max_days)

            if days_value > 0:
                packages = packages.filter(
                    estimated_days__lte=days_value
                )

        except ValueError:
            pass

    # --------------------------------------------------------
    # SORTING
    # --------------------------------------------------------

    if sort == "price_low":

        packages = packages.order_by(
            "price"
        )

    elif sort == "price_high":

        packages = packages.order_by(
            "-price"
        )

    elif sort == "fastest":

        packages = packages.order_by(
            "estimated_days",
            "price",
        )

    elif sort == "target":

        packages = packages.order_by(
            "target_rank__rank_order",
            "price",
        )

    else:

        packages = packages.order_by(
            "-is_featured",
            "current_rank__rank_order",
            "target_rank__rank_order",
            "price",
        )

    # --------------------------------------------------------
    # PAGINATION
    # --------------------------------------------------------

    # We deliberately do not dump hundreds of packages
    # onto the screen until a customer selects a game.
    show_catalogue = selected_game is not None

    page_obj = None
    result_count = 0

    if show_catalogue:

        paginator = Paginator(
            packages,
            24,
        )

        page_obj = paginator.get_page(
            request.GET.get("page")
        )

        result_count = paginator.count

    # --------------------------------------------------------
    # TEMPLATE CONTEXT
    # --------------------------------------------------------

    context = {
        "games": games,
        "categories": categories,
        "ranks": ranks,

        "featured_packages": featured_packages,

        "selected_game": selected_game,
        "selected_category": category_id,
        "selected_current_rank": current_rank_id,
        "selected_target_rank": target_rank_id,
        "selected_max_price": max_price,
        "selected_max_days": max_days,
        "selected_sort": sort,

        "show_catalogue": show_catalogue,
        "page_obj": page_obj,
        "result_count": result_count,
    }

    return render(
        request,
        "catalogue/package_list.html",
        context,
    )


def package_detail(request, package_id):
    """
    Display one active package and its customer reviews.
    """

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

    average_rating = (
        statistics["average_rating"]
        or 0
    )

    review_count = statistics[
        "review_count"
    ]

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
