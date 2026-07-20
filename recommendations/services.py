from catalogue.models import BoostPackage

from .models import SearchHistory


def record_search(user, cleaned_data):
    """Save meaningful search criteria for an authenticated user."""

    if not user.is_authenticated:
        return None

    query = (cleaned_data.get("query") or "").strip()
    game = cleaned_data.get("game")
    category = cleaned_data.get("category")
    current_rank = cleaned_data.get("current_rank")
    target_rank = cleaned_data.get("target_rank")
    minimum_price = cleaned_data.get("minimum_price")
    maximum_price = cleaned_data.get("maximum_price")
    maximum_days = cleaned_data.get("maximum_days")
    featured_only = cleaned_data.get("featured_only", False)

    has_criteria = any(
        [
            query,
            game,
            category,
            current_rank,
            target_rank,
            minimum_price is not None,
            maximum_price is not None,
            maximum_days is not None,
            featured_only,
        ]
    )

    if not has_criteria:
        return None

    latest_search = (
        SearchHistory.objects
        .filter(user=user)
        .first()
    )

    if latest_search:
        same_as_latest = all(
            [
                latest_search.query == query,
                latest_search.game_id == getattr(game, "id", None),
                latest_search.category_id
                == getattr(category, "id", None),
                latest_search.current_rank_id
                == getattr(current_rank, "id", None),
                latest_search.target_rank_id
                == getattr(target_rank, "id", None),
                latest_search.minimum_price == minimum_price,
                latest_search.maximum_price == maximum_price,
                latest_search.maximum_days == maximum_days,
                latest_search.featured_only == featured_only,
            ]
        )

        if same_as_latest:
            return latest_search

    search_entry = SearchHistory.objects.create(
        user=user,
        query=query,
        game=game,
        category=category,
        current_rank=current_rank,
        target_rank=target_rank,
        minimum_price=minimum_price,
        maximum_price=maximum_price,
        maximum_days=maximum_days,
        featured_only=featured_only,
    )

    old_search_ids = list(
        SearchHistory.objects
        .filter(user=user)
        .values_list("id", flat=True)[50:]
    )

    if old_search_ids:
        SearchHistory.objects.filter(
            id__in=old_search_ids,
        ).delete()

    return search_entry


def get_recommended_packages(user, limit=6):
    """Return ranked package recommendations for one user."""

    packages = list(
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

    search_history = list(
        SearchHistory.objects
        .filter(user=user)
        .select_related(
            "game",
            "category",
            "current_rank",
            "target_rank",
        )[:10]
    )

    profile = getattr(user, "profile", None)

    preferred_game_id = getattr(
        profile,
        "preferred_game_id",
        None,
    )

    ranked_recommendations = []

    for package in packages:
        score = 0
        reasons = []

        if (
            preferred_game_id
            and package.category.game_id == preferred_game_id
        ):
            score += 12
            reasons.append(
                "Matches your preferred game."
            )

        for position, search in enumerate(search_history):
            recency_weight = max(
                1,
                10 - position,
            )

            if (
                search.game_id
                and package.category.game_id == search.game_id
            ):
                score += 5 * recency_weight

                if not reasons:
                    reasons.append(
                        "Matches a game from your recent searches."
                    )

            if (
                search.category_id
                and package.category_id == search.category_id
            ):
                score += 5 * recency_weight

                if not reasons:
                    reasons.append(
                        "Matches a recently searched service category."
                    )

            if (
                search.current_rank_id
                and package.current_rank_id
                == search.current_rank_id
            ):
                score += 3 * recency_weight

                if not reasons:
                    reasons.append(
                        "Starts from a rank you recently searched."
                    )

            if (
                search.target_rank_id
                and package.target_rank_id
                == search.target_rank_id
            ):
                score += 4 * recency_weight

                if not reasons:
                    reasons.append(
                        "Reaches a rank you recently searched."
                    )

            if (
                search.minimum_price is not None
                and package.price >= search.minimum_price
            ):
                score += recency_weight

            if (
                search.maximum_price is not None
                and package.price <= search.maximum_price
            ):
                score += 2 * recency_weight

                if not reasons:
                    reasons.append(
                        "Fits a price range from your searches."
                    )

            if (
                search.maximum_days is not None
                and package.estimated_days <= search.maximum_days
            ):
                score += 2 * recency_weight

                if not reasons:
                    reasons.append(
                        "Fits your searched completion time."
                    )

            if search.featured_only and package.is_featured:
                score += 2 * recency_weight

            normalized_query = search.query.lower().strip()

            if normalized_query:
                package_text = " ".join(
                    [
                        package.name,
                        package.description,
                        package.category.name,
                        package.category.game.name,
                        package.current_rank.name,
                        package.target_rank.name,
                    ]
                ).lower()

                if normalized_query in package_text:
                    score += 4 * recency_weight

                    if not reasons:
                        reasons.append(
                            "Matches words from your recent searches."
                        )

        if package.is_featured:
            score += 2

        if reasons:
            reason = reasons[0]
        elif package.is_featured:
            reason = "Featured Papasmurfs service."
        else:
            reason = "Available service you may be interested in."

        ranked_recommendations.append(
            {
                "package": package,
                "score": score,
                "reason": reason,
            }
        )

    ranked_recommendations.sort(
        key=lambda recommendation: (
            -recommendation["score"],
            not recommendation["package"].is_featured,
            recommendation["package"].price,
        )
    )

    return ranked_recommendations[:limit]
