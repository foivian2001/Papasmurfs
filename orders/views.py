import secrets
from datetime import date
from decimal import Decimal

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from cart.models import Cart, CartItem
from .models import Order, OrderItem


DEMO_APPROVED_CARD = "4242424242424242"
DEMO_DECLINED_CARD = "4000000000000002"


@login_required(login_url="accounts:login")
def checkout(request):
    """Display the simulated checkout and payment page."""

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
        "payment_errors": {},
        "payment_values": {
            "cardholder_name": (
                request.user.get_full_name()
                or request.user.username
            ),
            "expiry": "",
            "billing_country": "Greece",
        },
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
    """
    Validate a simulated card payment and convert the user's
    cart into a completed order.

    Payment information is used only for this request and is
    never saved to the database.
    """

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

    # --------------------------------------------------------
    # SIMULATED PAYMENT DATA
    # --------------------------------------------------------

    cardholder_name = request.POST.get(
        "cardholder_name",
        "",
    ).strip()

    raw_card_number = request.POST.get(
        "card_number",
        "",
    ).strip()

    expiry = request.POST.get(
        "expiry",
        "",
    ).strip()

    cvv = request.POST.get(
        "cvv",
        "",
    ).strip()

    billing_country = request.POST.get(
        "billing_country",
        "",
    ).strip()

    # Remove only normal formatting characters.
    card_number = (
        raw_card_number
        .replace(" ", "")
        .replace("-", "")
    )

    payment_errors = {}

    # --------------------------------------------------------
    # CARDHOLDER
    # --------------------------------------------------------

    if len(cardholder_name) < 2:
        payment_errors["cardholder_name"] = (
            "Enter the cardholder name."
        )

    # --------------------------------------------------------
    # DEMO CARD NUMBER
    # --------------------------------------------------------

    if card_number not in {
        DEMO_APPROVED_CARD,
        DEMO_DECLINED_CARD,
    }:
        payment_errors["card_number"] = (
            "Use one of the Papasmurfs demo card numbers."
        )

    # --------------------------------------------------------
    # EXPIRY DATE
    # --------------------------------------------------------

    if not expiry:
        payment_errors["expiry"] = (
            "Select an expiry date."
        )

    else:
        try:
            year_text, month_text = expiry.split("-")

            expiry_year = int(year_text)
            expiry_month = int(month_text)

            today = date.today()

            if not 1 <= expiry_month <= 12:
                raise ValueError

            if (
                expiry_year,
                expiry_month,
            ) < (
                today.year,
                today.month,
            ):
                payment_errors["expiry"] = (
                    "The simulated card has expired."
                )

        except (ValueError, TypeError):
            payment_errors["expiry"] = (
                "Enter a valid expiry date."
            )

    # --------------------------------------------------------
    # CVV
    # --------------------------------------------------------

    if (
        not cvv.isdigit()
        or len(cvv) != 3
    ):
        payment_errors["cvv"] = (
            "Enter a 3-digit demo CVV."
        )

    # --------------------------------------------------------
    # BILLING COUNTRY
    # --------------------------------------------------------

    if len(billing_country) < 2:
        payment_errors["billing_country"] = (
            "Enter a billing country."
        )

    # --------------------------------------------------------
    # RETURN VALIDATION ERRORS
    # --------------------------------------------------------

    if payment_errors:
        context = {
            "cart": cart,
            "cart_items": cart_items,
            "total_price": total_price,
            "payment_errors": payment_errors,
            "payment_values": {
                "cardholder_name": cardholder_name,
                "expiry": expiry,
                "billing_country": billing_country,
            },
        }

        return render(
            request,
            "orders/checkout.html",
            context,
            status=400,
        )

    # --------------------------------------------------------
    # SIMULATED DECLINED TRANSACTION
    # --------------------------------------------------------

    if card_number == DEMO_DECLINED_CARD:
        context = {
            "cart": cart,
            "cart_items": cart_items,
            "total_price": total_price,
            "payment_errors": {
                "card_number": (
                    "Transaction declined by the simulated bank. "
                    "Try the approved demo card."
                ),
            },
            "payment_values": {
                "cardholder_name": cardholder_name,
                "expiry": expiry,
                "billing_country": billing_country,
            },
        }

        return render(
            request,
            "orders/checkout.html",
            context,
            status=400,
        )

    # --------------------------------------------------------
    # SIMULATED PAYMENT APPROVED
    # --------------------------------------------------------

    transaction_reference = (
        "PS-"
        + secrets.token_hex(4).upper()
    )

    # --------------------------------------------------------
    # CREATE ORDER
    # --------------------------------------------------------

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

    OrderItem.objects.bulk_create(
        order_items
    )

    CartItem.objects.filter(
        cart=cart,
    ).delete()

    messages.success(
        request,
        (
            f"Simulated payment approved. "
            f"Transaction {transaction_reference}. "
            f"Demo card ending in {card_number[-4:]}. "
            f"Order #{order.id} was completed successfully. "
            f"No real payment was processed."
        ),
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
