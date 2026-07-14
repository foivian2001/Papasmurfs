from django.urls import path

from . import views

app_name = "controlpanel"

urlpatterns = [
    path("", views.dashboard, name="dashboard"),
]
