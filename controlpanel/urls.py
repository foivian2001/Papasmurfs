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

        path(
        "ranks/",
        views.rank_list,
        name="rank_list",
    ),
    path(
        "ranks/add/",
        views.rank_create,
        name="rank_create",
    ),
    path(
        "ranks/<int:rank_id>/edit/",
        views.rank_update,
        name="rank_update",
    ),
    path(
        "ranks/<int:rank_id>/delete/",
        views.rank_delete_confirmation,
        name="rank_delete_confirmation",
    ),
    path(
        "ranks/<int:rank_id>/delete/confirm/",
        views.rank_delete,
        name="rank_delete",
    ),

        path(
        "packages/",
        views.package_management_list,
        name="package_list",
    ),
    path(
        "packages/add/",
        views.package_create,
        name="package_create",
    ),
    path(
        "packages/<int:package_id>/edit/",
        views.package_update,
        name="package_update",
    ),
    path(
        "packages/<int:package_id>/delete/",
        views.package_delete_confirmation,
        name="package_delete_confirmation",
    ),
    path(
        "packages/<int:package_id>/delete/confirm/",
        views.package_delete,
        name="package_delete",
    ),
]
