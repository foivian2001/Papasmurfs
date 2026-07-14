from django.contrib import messages
from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404, redirect, render
from django.db.models.deletion import ProtectedError
from django.views.decorators.http import require_POST

from catalogue.models import (
    BoostPackage,
    Game,
    Rank,
    ServiceCategory,
)

from .decorators import staff_required
from .forms import GameForm, RankForm, ServiceCategoryForm


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


@staff_required
def game_list(request):
    """Display all games available in the catalogue."""

    games = Game.objects.all()

    context = {
        "games": games,
    }

    return render(
        request,
        "controlpanel/games/game_list.html",
        context,
    )


@staff_required
def game_create(request):
    """Allow staff members to add a new game."""

    form = GameForm(
        request.POST or None,
        request.FILES or None,
    )

    if request.method == "POST" and form.is_valid():
        game = form.save()

        messages.success(
            request,
            f"{game.name} was added successfully.",
        )

        return redirect("controlpanel:game_list")

    context = {
        "form": form,
        "page_title": "Add game",
        "submit_text": "Create game",
    }

    return render(
        request,
        "controlpanel/games/game_form.html",
        context,
    )


@staff_required
def game_update(request, game_id):
    """Allow staff members to update an existing game."""

    game = get_object_or_404(
        Game,
        id=game_id,
    )

    form = GameForm(
        request.POST or None,
        request.FILES or None,
        instance=game,
    )

    if request.method == "POST" and form.is_valid():
        updated_game = form.save()

        messages.success(
            request,
            f"{updated_game.name} was updated successfully.",
        )

        return redirect("controlpanel:game_list")

    context = {
        "form": form,
        "game": game,
        "page_title": f"Edit {game.name}",
        "submit_text": "Save changes",
    }

    return render(
        request,
        "controlpanel/games/game_form.html",
        context,
    )


@staff_required
def game_delete_confirmation(request, game_id):
    """Display a confirmation page before deleting a game."""

    game = get_object_or_404(
        Game,
        id=game_id,
    )

    context = {
        "game": game,
    }

    return render(
        request,
        "controlpanel/games/game_confirm_delete.html",
        context,
    )


@staff_required
@require_POST
def game_delete(request, game_id):
    """Delete a game after receiving a confirmed POST request."""

    game = get_object_or_404(
        Game,
        id=game_id,
    )

    game_name = game.name
    game.delete()

    messages.success(
        request,
        f"{game_name} was deleted successfully.",
    )

    return redirect("controlpanel:game_list")

@staff_required
def category_list(request):
    """Display all service categories."""

    categories = ServiceCategory.objects.select_related("game")

    context = {
        "categories": categories,
    }

    return render(
        request,
        "controlpanel/categories/category_list.html",
        context,
    )


@staff_required
def category_create(request):
    """Allow staff members to create a service category."""

    form = ServiceCategoryForm(
        request.POST or None,
    )

    if request.method == "POST" and form.is_valid():
        category = form.save()

        messages.success(
            request,
            f"{category.name} was created successfully.",
        )

        return redirect("controlpanel:category_list")

    context = {
        "form": form,
        "page_title": "Add service category",
        "submit_text": "Create category",
    }

    return render(
        request,
        "controlpanel/categories/category_form.html",
        context,
    )


@staff_required
def category_update(request, category_id):
    """Allow staff members to update a service category."""

    category = get_object_or_404(
        ServiceCategory,
        id=category_id,
    )

    form = ServiceCategoryForm(
        request.POST or None,
        instance=category,
    )

    if request.method == "POST" and form.is_valid():
        updated_category = form.save()

        messages.success(
            request,
            f"{updated_category.name} was updated successfully.",
        )

        return redirect("controlpanel:category_list")

    context = {
        "form": form,
        "category": category,
        "page_title": f"Edit {category.name}",
        "submit_text": "Save changes",
    }

    return render(
        request,
        "controlpanel/categories/category_form.html",
        context,
    )


@staff_required
def category_delete_confirmation(request, category_id):
    """Display confirmation before deleting a category."""

    category = get_object_or_404(
        ServiceCategory.objects.select_related("game"),
        id=category_id,
    )

    context = {
        "category": category,
    }

    return render(
        request,
        "controlpanel/categories/category_confirm_delete.html",
        context,
    )


@staff_required
@require_POST
def category_delete(request, category_id):
    """Delete a category after receiving a confirmed POST request."""

    category = get_object_or_404(
        ServiceCategory,
        id=category_id,
    )

    category_name = category.name
    category.delete()

    messages.success(
        request,
        f"{category_name} was deleted successfully.",
    )

    return redirect("controlpanel:category_list")

@staff_required
def rank_list(request):
    """Display all competitive ranks."""

    ranks = Rank.objects.select_related("game")

    context = {
        "ranks": ranks,
    }

    return render(
        request,
        "controlpanel/ranks/rank_list.html",
        context,
    )


@staff_required
def rank_create(request):
    """Allow staff members to create a competitive rank."""

    form = RankForm(
        request.POST or None,
    )

    if request.method == "POST" and form.is_valid():
        rank = form.save()

        messages.success(
            request,
            f"{rank.name} was created successfully.",
        )

        return redirect("controlpanel:rank_list")

    context = {
        "form": form,
        "page_title": "Add rank",
        "submit_text": "Create rank",
    }

    return render(
        request,
        "controlpanel/ranks/rank_form.html",
        context,
    )


@staff_required
def rank_update(request, rank_id):
    """Allow staff members to update an existing rank."""

    rank = get_object_or_404(
        Rank,
        id=rank_id,
    )

    form = RankForm(
        request.POST or None,
        instance=rank,
    )

    if request.method == "POST" and form.is_valid():
        updated_rank = form.save()

        messages.success(
            request,
            f"{updated_rank.name} was updated successfully.",
        )

        return redirect("controlpanel:rank_list")

    context = {
        "form": form,
        "rank": rank,
        "page_title": f"Edit {rank.name}",
        "submit_text": "Save changes",
    }

    return render(
        request,
        "controlpanel/ranks/rank_form.html",
        context,
    )


@staff_required
def rank_delete_confirmation(request, rank_id):
    """Display confirmation before deleting a competitive rank."""

    rank = get_object_or_404(
        Rank.objects.select_related("game"),
        id=rank_id,
    )

    context = {
        "rank": rank,
        "starting_package_count": (
            rank.packages_starting_here.count()
        ),
        "target_package_count": (
            rank.packages_ending_here.count()
        ),
    }

    return render(
        request,
        "controlpanel/ranks/rank_confirm_delete.html",
        context,
    )


@staff_required
@require_POST
def rank_delete(request, rank_id):
    """Delete a rank unless it is being used by a boost package."""

    rank = get_object_or_404(
        Rank,
        id=rank_id,
    )

    rank_name = rank.name

    try:
        rank.delete()
    except ProtectedError:
        messages.error(
            request,
            (
                f"{rank_name} cannot be deleted because it is used "
                "by one or more boost packages."
            ),
        )

        return redirect("controlpanel:rank_list")

    messages.success(
        request,
        f"{rank_name} was deleted successfully.",
    )

    return redirect("controlpanel:rank_list")

