from django.contrib import messages
from django.contrib.auth import get_user_model
from django.db.models import Q
from django.db.models.deletion import ProtectedError
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from catalogue.models import (
    BoostPackage,
    Game,
    Rank,
    ServiceCategory,
)
from orders.models import Order

from .decorators import staff_required
from .forms import (
    BoostPackageForm,
    GameForm,
    RankForm,
    ServiceCategoryForm,
)


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
        "order_count": Order.objects.count(),
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


@staff_required
def package_management_list(request):
    """
    Display boost packages for staff with management filters.
    """

    packages = (
        BoostPackage.objects
        .select_related(
            "category",
            "category__game",
            "current_rank",
            "target_rank",
        )
        .all()
    )

    games = Game.objects.order_by("name")

    categories = (
        ServiceCategory.objects
        .select_related("game")
        .order_by(
            "game__name",
            "name",
        )
    )

    name_query = request.GET.get(
        "name",
        "",
    ).strip()

    game_id = request.GET.get(
        "game",
        "",
    )

    category_id = request.GET.get(
        "category",
        "",
    )

    status = request.GET.get(
        "status",
        "",
    )

    if name_query:
        packages = packages.filter(
            name__icontains=name_query
        )

    if game_id:
        packages = packages.filter(
            category__game_id=game_id
        )

    if category_id:
        packages = packages.filter(
            category_id=category_id
        )

    if status == "active":
        packages = packages.filter(
            is_active=True
        )

    elif status == "inactive":
        packages = packages.filter(
            is_active=False
        )

    packages = packages.order_by(
        "category__game__name",
        "category__name",
        "current_rank__rank_order",
        "target_rank__rank_order",
    )

    context = {
        "packages": packages,
        "games": games,
        "categories": categories,
        "selected_name": name_query,
        "selected_game": game_id,
        "selected_category": category_id,
        "selected_status": status,
        "result_count": packages.count(),
    }

    return render(
        request,
        "controlpanel/packages/package_list.html",
        context,
    )


@staff_required
def package_create(request):
    """Allow staff members to create a boost package."""

    form = BoostPackageForm(
        request.POST or None,
        request.FILES or None,
    )

    if request.method == "POST" and form.is_valid():
        package = form.save()

        messages.success(
            request,
            f"{package.name} was created successfully.",
        )

        return redirect("controlpanel:package_list")

    context = {
        "form": form,
        "page_title": "Add boost package",
        "submit_text": "Create package",
    }

    return render(
        request,
        "controlpanel/packages/package_form.html",
        context,
    )


@staff_required
def package_update(request, package_id):
    """Allow staff members to update an existing boost package."""

    package = get_object_or_404(
        BoostPackage,
        id=package_id,
    )

    form = BoostPackageForm(
        request.POST or None,
        request.FILES or None,
        instance=package,
    )

    if request.method == "POST" and form.is_valid():
        updated_package = form.save()

        messages.success(
            request,
            f"{updated_package.name} was updated successfully.",
        )

        return redirect("controlpanel:package_list")

    context = {
        "form": form,
        "package": package,
        "page_title": f"Edit {package.name}",
        "submit_text": "Save changes",
    }

    return render(
        request,
        "controlpanel/packages/package_form.html",
        context,
    )


@staff_required
def package_delete_confirmation(request, package_id):
    """Display confirmation before deleting a boost package."""

    package = get_object_or_404(
        BoostPackage.objects.select_related(
            "category",
            "category__game",
            "current_rank",
            "target_rank",
        ),
        id=package_id,
    )

    context = {
        "package": package,
    }

    return render(
        request,
        "controlpanel/packages/package_confirm_delete.html",
        context,
    )


@staff_required
@require_POST
def package_delete(request, package_id):
    """Delete a boost package after receiving a confirmed POST request."""

    package = get_object_or_404(
        BoostPackage,
        id=package_id,
    )

    package_name = package.name
    package.delete()

    messages.success(
        request,
        f"{package_name} was deleted successfully.",
    )

    return redirect("controlpanel:package_list")


@staff_required
def order_list(request):
    """Display and filter customer orders for staff members."""

    orders = (
        Order.objects
        .select_related("user")
        .prefetch_related("items")
        .all()
    )

    query = request.GET.get(
        "query",
        "",
    ).strip()

    status = request.GET.get(
        "status",
        "",
    ).strip()

    if query:
        clean_query = query.lstrip("#")

        search_filter = (
            Q(user__username__icontains=query)
            | Q(user__email__icontains=query)
        )

        if clean_query.isdigit():
            search_filter |= Q(id=int(clean_query))

        orders = orders.filter(search_filter)

    if status in Order.Status.values:
        orders = orders.filter(
            status=status,
        )

    orders = orders.order_by("-created_at")

    context = {
        "orders": orders,
        "query": query,
        "selected_status": status,
        "status_choices": Order.Status.choices,
        "result_count": orders.count(),
    }

    return render(
        request,
        "controlpanel/orders/order_list.html",
        context,
    )


@staff_required
def order_detail(request, order_id):
    """Display a customer's order details to staff members."""

    order = get_object_or_404(
        Order.objects
        .select_related("user")
        .prefetch_related("items"),
        id=order_id,
    )

    context = {
        "order": order,
        "status_choices": Order.Status.choices,
    }

    return render(
        request,
        "controlpanel/orders/order_detail.html",
        context,
    )


@staff_required
@require_POST
def order_status_update(request, order_id):
    """Allow staff to update an order's status safely."""

    order = get_object_or_404(
        Order,
        id=order_id,
    )

    new_status = request.POST.get(
        "status",
        "",
    )

    if new_status not in Order.Status.values:
        messages.error(
            request,
            "The selected order status is invalid.",
        )

        return redirect(
            "controlpanel:order_detail",
            order_id=order.id,
        )

    if order.status == new_status:
        messages.info(
            request,
            "The order already has that status.",
        )

        return redirect(
            "controlpanel:order_detail",
            order_id=order.id,
        )

    order.status = new_status
    order.save(
        update_fields=[
            "status",
            "updated_at",
        ]
    )

    messages.success(
        request,
        (
            f"Order #{order.id} status was changed to "
            f"{order.get_status_display()}."
        ),
    )

    return redirect(
        "controlpanel:order_detail",
        order_id=order.id,
    )
