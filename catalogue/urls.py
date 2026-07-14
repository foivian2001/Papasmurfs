from django.urls import path

from . import views

app_name = "catalogue"

urlpatterns = [
    path("", views.package_list, name="package_list"),
    path(
        "packages/<int:package_id>/",
        views.package_detail,
        name="package_detail",
    ),
]
