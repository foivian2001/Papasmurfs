from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from catalogue.models import BoostPackage

from .forms import CartItemQuantityForm
from .models import Cart, CartItem


@login_required(login_url="accounts:login")
def cart_detail(request):
    """Display the logged-in user's shopping cart."""

    cart, created = Cart.objects.get_or_create(
        user=request.user,
    )

    cart_items = cart.items.select_related(
        "package",
        "package__category",
        "package__category__game",
        "package__current_rank",
        "package__target_rank",
    )

    context = {
        "cart": cart,
        "cart_items": cart_items,
    }

    return render(
        request,
        "cart/cart_detail.html",
        context,
    )


@login_required(login_url="accounts:login")
@require_POST
def add_to_cart(request, package_id):
    """Add a selected boost package to the user's cart."""

    package = get_object_or_404(
        BoostPackage.objects.select_related(
            "category",
            "category__game",
        ),
        id=package_id,
        is_active=True,
        category__game__is_active=True,
    )

    form = CartItemQuantityForm(request.POST)

    if not form.is_valid():
        messages.error(
            request,
            "Please enter a quantity between 1 and 10.",
        )

        return redirect(
            "catalogue:package_detail",
            package_id=package.id,
        )

    selected_quantity = form.cleaned_data["quantity"]

    cart, created = Cart.objects.get_or_create(
        user=request.user,
    )

    cart_item, item_created = CartItem.objects.get_or_create(
        cart=cart,
        package=package,
        defaults={
            "quantity": selected_quantity,
        },
    )

    if item_created:
        messages.success(
            request,
            f"{package.name} was added to your cart.",
        )
    else:
        new_quantity = cart_item.quantity + selected_quantity

        if new_quantity > 10:
            messages.error(
                request,
                (
                    "The maximum quantity allowed for one "
                    "package is 10."
                ),
            )

            return redirect("cart:detail")

        cart_item.quantity = new_quantity
        cart_item.save(
            update_fields=[
                "quantity",
                "updated_at",
            ],
        )

        messages.success(
            request,
            f"The quantity of {package.name} was updated.",
        )

    return redirect("cart:detail")


@login_required(login_url="accounts:login")
@require_POST
def update_cart_item(request, item_id):
    """Update the quantity of an item belonging to the user."""

    cart_item = get_object_or_404(
        CartItem.objects.select_related(
            "cart",
            "package",
        ),
        id=item_id,
        cart__user=request.user,
    )

    form = CartItemQuantityForm(request.POST)

    if form.is_valid():
        cart_item.quantity = form.cleaned_data["quantity"]
        cart_item.save(
            update_fields=[
                "quantity",
                "updated_at",
            ],
        )

        messages.success(
            request,
            f"{cart_item.package.name} was updated.",
        )
    else:
        messages.error(
            request,
            "Please enter a quantity between 1 and 10.",
        )

    return redirect("cart:detail")


@login_required(login_url="accounts:login")
@require_POST
def remove_cart_item(request, item_id):
    """Remove an item belonging to the logged-in user."""

    cart_item = get_object_or_404(
        CartItem.objects.select_related(
            "package",
        ),
        id=item_id,
        cart__user=request.user,
    )

    package_name = cart_item.package.name
    cart_item.delete()

    messages.success(
        request,
        f"{package_name} was removed from your cart.",
    )

    return redirect("cart:detail")
