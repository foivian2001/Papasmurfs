from django.contrib import messages
from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from catalogue.models import (
    BoostPackage,
    Game,
    Rank,
    ServiceCategory,
)

from .decorators import staff_required
from .forms import GameForm


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
