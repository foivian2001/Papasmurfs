from django.urls import path

from . import views


app_name = "ratings"

urlpatterns = [
    path(
        "package/<int:package_id>/submit/",
        views.submit_review,
        name="submit_review",
    ),
]
