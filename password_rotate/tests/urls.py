from django.urls import include, path
from django.contrib import admin


urlpatterns = [
    path("", include("django.contrib.auth.urls")),
    path("admin/", admin.site.urls),
    path("password_rotate/", include("password_rotate.urls")),
]
