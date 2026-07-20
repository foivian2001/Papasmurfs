from decimal import Decimal

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Sum
from django.shortcuts import redirect, render

from orders.models import Order
from recommendations.services import get_recommended_packages

from .forms import UserAccountForm, UserProfileForm
from .models import UserProfile


@login_required(login_url="accounts:login")
def dashboard_home(request):
    """Display the personalised dashboard for the logged-in user."""

    profile, profile_created = UserProfile.objects.get_or_create(
        user=request.user,
    )

    user_orders = Order.objects.filter(
        user=request.user,
    )

    recent_orders = user_orders.prefetch_related(
        "items",
    )[:3]

    completed_orders = user_orders.filter(
        status=Order.Status.COMPLETED,
    )

    total_spent = completed_orders.aggregate(
        total=Sum("total_price"),
    )["total"] or Decimal("0.00")

    recommended_packages = get_recommended_packages(
        request.user,
        limit=3,
    )

    context = {
        "profile": profile,
        "profile_created": profile_created,
        "recent_orders": recent_orders,
        "order_count": user_orders.count(),
        "total_spent": total_spent,
        "recommended_packages": recommended_packages,
    }

    return render(
        request,
        "dashboard/dashboard_home.html",
        context,
    )


@login_required(login_url="accounts:login")
def edit_profile(request):
    """Allow the logged-in user to edit their account and profile."""

    profile, created = UserProfile.objects.get_or_create(
        user=request.user,
    )

    if request.method == "POST":
        account_form = UserAccountForm(
            request.POST,
            instance=request.user,
        )

        profile_form = UserProfileForm(
            request.POST,
            request.FILES,
            instance=profile,
        )

        if account_form.is_valid() and profile_form.is_valid():
            account_form.save()
            profile_form.save()

            messages.success(
                request,
                "Your profile was updated successfully.",
            )

            return redirect("dashboard:home")
    else:
        account_form = UserAccountForm(
            instance=request.user,
        )

        profile_form = UserProfileForm(
            instance=profile,
        )

    context = {
        "account_form": account_form,
        "profile_form": profile_form,
    }

    return render(
        request,
        "dashboard/edit_profile.html",
        context,
    )
