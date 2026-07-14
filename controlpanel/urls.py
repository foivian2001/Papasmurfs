from django.urls import path

from . import views

app_name = "controlpanel"

urlpatterns = [
    path("", views.dashboard, name="dashboard"),
    path("games/", views.game_list, name="game_list"),
    path("games/add/", views.game_create, name="game_create"),
    path(
        "games/<int:game_id>/edit/",
        views.game_update,
        name="game_update",
    ),
    path(
        "games/<int:game_id>/delete/",
        views.game_delete_confirmation,
        name="game_delete_confirmation",
    ),
    path(
        "games/<int:game_id>/delete/confirm/",
        views.game_delete,
        name="game_delete",
    ),
]
