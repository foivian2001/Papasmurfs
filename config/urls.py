from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("django-admin/", admin.site.urls),
    path("control-panel/", include("controlpanel.urls")),
    path("account/", include("accounts.urls")),
    path("services/", include("catalogue.urls")),
    path("", include("core.urls")),
]
