from functools import wraps

from django.core.exceptions import PermissionDenied
from django.shortcuts import redirect


def staff_required(view_function):
    """Allow only authenticated staff members to access a view."""

    @wraps(view_function)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect("accounts:login")

        if not request.user.is_staff:
            raise PermissionDenied

        return view_function(request, *args, **kwargs)

    return wrapper
