from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path


urlpatterns = [
    path(
        "django-admin/",
        admin.site.urls,
    ),
    path(
        "control-panel/",
        include("controlpanel.urls"),
    ),
    path(
        "account/",
        include("accounts.urls"),
    ),
    path(
        "dashboard/",
        include("dashboard.urls"),
    ),
    path(
        "cart/",
        include("cart.urls"),
    ),
    path(
        "orders/",
        include("orders.urls"),
    ),
    path(
        "ratings/",
        include("ratings.urls"),
    ),
    path(
        "search/",
        include("searchapp.urls"),
    ),
    path(
        "services/",
        include("catalogue.urls"),
    ),
    path(
        "",
        include("core.urls"),
    ),
]

if settings.DEBUG:
    urlpatterns += static(
        settings.MEDIA_URL,
        document_root=settings.MEDIA_ROOT,
    )
