from django.urls import path

from . import views


app_name = "orders"

urlpatterns = [
    path(
        "checkout/",
        views.checkout,
        name="checkout",
    ),
    path(
        "checkout/place/",
        views.place_order,
        name="place_order",
    ),
    path(
        "success/<int:order_id>/",
        views.order_success,
        name="success",
    ),
    path(
        "history/",
        views.order_history,
        name="history",
    ),
    path(
        "<int:order_id>/",
        views.order_detail,
        name="detail",
    ),
]
