from django.urls import path

from . import views


app_name = "dashboard"

urlpatterns = [
    path(
        "",
        views.dashboard_home,
        name="home",
    ),
    path(
        "profile/edit/",
        views.edit_profile,
        name="edit_profile",
    ),
]
