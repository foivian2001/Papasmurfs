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

    path(
        "categories/",
        views.category_list,
        name="category_list",
    ),
        path(
        "categories/add/",
        views.category_create,
        name="category_create",
    ),
    path(
        "categories/<int:category_id>/edit/",
        views.category_update,
        name="category_update",
    ),
        path(
        "categories/<int:category_id>/delete/",
        views.category_delete_confirmation,
        name="category_delete_confirmation",
    ),
        path(
        "categories/<int:category_id>/delete/confirm/",
        views.category_delete,
        name="category_delete",
    ),
]
