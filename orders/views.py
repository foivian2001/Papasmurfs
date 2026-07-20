from decimal import Decimal

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from cart.models import Cart, CartItem

from .models import Order, OrderItem


@login_required(login_url="accounts:login")
def checkout(request):
    """Display the simulated checkout confirmation page."""

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

    if not cart_items.exists():
        messages.info(
            request,
            "Your cart is empty.",
        )

        return redirect("cart:detail")

    total_price = sum(
        (
            item.package.price * item.quantity
            for item in cart_items
        ),
        Decimal("0.00"),
    )

    context = {
        "cart": cart,
        "cart_items": cart_items,
        "total_price": total_price,
    }

    return render(
        request,
        "orders/checkout.html",
        context,
    )


@login_required(login_url="accounts:login")
@require_POST
@transaction.atomic
def place_order(request):
    """Convert the user's cart into a completed simulated order."""

    cart = get_object_or_404(
        Cart.objects.select_for_update(),
        user=request.user,
    )

    cart_items = list(
        CartItem.objects.select_for_update()
        .filter(cart=cart)
        .select_related(
            "package",
            "package__category",
            "package__category__game",
            "package__current_rank",
            "package__target_rank",
        )
    )

    if not cart_items:
        messages.error(
            request,
            "Your cart is empty.",
        )

        return redirect("cart:detail")

    unavailable_items = [
        item
        for item in cart_items
        if (
            not item.package.is_active
            or not item.package.category.game.is_active
        )
    ]

    if unavailable_items:
        messages.error(
            request,
            (
                "One or more packages are no longer available. "
                "Please review your cart."
            ),
        )

        return redirect("cart:detail")

    total_price = sum(
        (
            item.package.price * item.quantity
            for item in cart_items
        ),
        Decimal("0.00"),
    )

    order = Order.objects.create(
        user=request.user,
        status=Order.Status.COMPLETED,
        total_price=total_price,
    )

    order_items = []

    for cart_item in cart_items:
        package = cart_item.package

        order_items.append(
            OrderItem(
                order=order,
                package=package,
                package_name=package.name,
                game_name=package.category.game.name,
                category_name=package.category.name,
                current_rank_name=package.current_rank.name,
                target_rank_name=package.target_rank.name,
                unit_price=package.price,
                quantity=cart_item.quantity,
            )
        )

    OrderItem.objects.bulk_create(order_items)

    CartItem.objects.filter(
        cart=cart,
    ).delete()

    messages.success(
        request,
        f"Order #{order.id} was completed successfully.",
    )

    return redirect(
        "orders:success",
        order_id=order.id,
    )


@login_required(login_url="accounts:login")
def order_success(request, order_id):
    """Display confirmation for a completed order."""

    order = get_object_or_404(
        Order.objects.prefetch_related("items"),
        id=order_id,
        user=request.user,
    )

    context = {
        "order": order,
    }

    return render(
        request,
        "orders/order_success.html",
        context,
    )


@login_required(login_url="accounts:login")
def order_history(request):
    """Display all orders belonging to the logged-in user."""

    orders = (
        Order.objects
        .filter(user=request.user)
        .prefetch_related("items")
    )

    context = {
        "orders": orders,
    }

    return render(
        request,
        "orders/order_history.html",
        context,
    )


@login_required(login_url="accounts:login")
def order_detail(request, order_id):
    """Display one order belonging to the logged-in user."""

    order = get_object_or_404(
        Order.objects.prefetch_related("items"),
        id=order_id,
        user=request.user,
    )

    context = {
        "order": order,
    }

    return render(
        request,
        "orders/order_detail.html",
        context,
    )
