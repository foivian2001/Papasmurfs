from django.contrib import messages
from django.contrib.auth import get_user_model
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from controlpanel.decorators import staff_required

from .forms import StaffUserForm


User = get_user_model()


@staff_required
def user_list(request):
    """Display registered users inside the custom staff panel."""

    search_query = request.GET.get(
        "query",
        "",
    ).strip()

    users = User.objects.all().order_by(
        "-date_joined",
    )

    if search_query:
        users = users.filter(
            Q(username__icontains=search_query)
            | Q(first_name__icontains=search_query)
            | Q(last_name__icontains=search_query)
            | Q(email__icontains=search_query)
        )

    context = {
        "users": users,
        "search_query": search_query,
        "user_count": users.count(),
    }

    return render(
        request,
        "usermanagement/user_list.html",
        context,
    )


@staff_required
def user_update(request, user_id):
    """Allow staff to update an account safely."""

    managed_user = get_object_or_404(
        User,
        id=user_id,
    )

    if (
        managed_user.is_superuser
        and not request.user.is_superuser
    ):
        messages.error(
            request,
            "Only a superuser can modify another superuser.",
        )

        return redirect("usermanagement:list")

    original_is_active = managed_user.is_active
    original_is_staff = managed_user.is_staff

    if request.method == "POST":
        form = StaffUserForm(
            request.POST,
            instance=managed_user,
        )

        if form.is_valid():
            updated_user = form.save(
                commit=False,
            )

            if managed_user == request.user:
                updated_user.is_active = original_is_active
                updated_user.is_staff = original_is_staff

                messages.warning(
                    request,
                    (
                        "Your profile details were updated, but you "
                        "cannot deactivate yourself or remove your own "
                        "staff access."
                    ),
                )
            else:
                messages.success(
                    request,
                    f"{managed_user.username} was updated successfully.",
                )

            updated_user.save()

            return redirect("usermanagement:list")
    else:
        form = StaffUserForm(
            instance=managed_user,
        )

    context = {
        "form": form,
        "managed_user": managed_user,
    }

    return render(
        request,
        "usermanagement/user_form.html",
        context,
    )


@staff_required
def user_delete_confirmation(request, user_id):
    """Display confirmation before deleting an account."""

    managed_user = get_object_or_404(
        User,
        id=user_id,
    )

    if managed_user == request.user:
        messages.error(
            request,
            "You cannot delete your own account.",
        )

        return redirect("usermanagement:list")

    if managed_user.is_superuser:
        messages.error(
            request,
            "Superuser accounts cannot be deleted from this page.",
        )

        return redirect("usermanagement:list")

    context = {
        "managed_user": managed_user,
    }

    return render(
        request,
        "usermanagement/user_confirm_delete.html",
        context,
    )


@staff_required
@require_POST
def user_delete(request, user_id):
    """Delete an ordinary account after confirmation."""

    managed_user = get_object_or_404(
        User,
        id=user_id,
    )

    if managed_user == request.user:
        messages.error(
            request,
            "You cannot delete your own account.",
        )

        return redirect("usermanagement:list")

    if managed_user.is_superuser:
        messages.error(
            request,
            "Superuser accounts cannot be deleted here.",
        )

        return redirect("usermanagement:list")

    username = managed_user.username
    managed_user.delete()

    messages.success(
        request,
        f"{username} was deleted successfully.",
    )

    return redirect("usermanagement:list")
