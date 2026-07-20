from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render

from .forms import UserAccountForm, UserProfileForm
from .models import UserProfile


@login_required(login_url="accounts:login")
def dashboard_home(request):
    """Display the personalised dashboard for the logged-in user."""

    profile, profile_created = UserProfile.objects.get_or_create(
        user=request.user,
    )

    context = {
        "profile": profile,
        "profile_created": profile_created,
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
