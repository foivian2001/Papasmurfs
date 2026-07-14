from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.shortcuts import redirect, render
from django.views.decorators.http import require_POST


def register_view(request):
    """Register a new Papasmurfs user."""

    if request.user.is_authenticated:
        return redirect("core:home")

    form = UserCreationForm(request.POST or None)

    if request.method == "POST" and form.is_valid():
        user = form.save()
        login(request, user)

        return redirect("core:home")

    context = {
        "form": form,
    }

    return render(
        request,
        "accounts/register.html",
        context,
    )


def login_view(request):
    """Authenticate an existing Papasmurfs user."""

    if request.user.is_authenticated:
        return redirect("core:home")

    form = AuthenticationForm(
        request=request,
        data=request.POST or None,
    )

    if request.method == "POST" and form.is_valid():
        login(request, form.get_user())

        return redirect("core:home")

    context = {
        "form": form,
    }

    return render(
        request,
        "accounts/login.html",
        context,
    )


@login_required
@require_POST
def logout_view(request):
    """Log out the currently authenticated user."""

    logout(request)

    return redirect("core:home")
