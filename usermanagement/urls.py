from django.urls import path

from . import views


app_name = "usermanagement"

urlpatterns = [
    path(
        "",
        views.user_list,
        name="list",
    ),
    path(
        "<int:user_id>/edit/",
        views.user_update,
        name="update",
    ),
    path(
        "<int:user_id>/delete/",
        views.user_delete_confirmation,
        name="delete_confirmation",
    ),
    path(
        "<int:user_id>/delete/confirm/",
        views.user_delete,
        name="delete",
    ),
]
