from django.urls import include, path
from django.contrib import admin
from django.http import HttpResponse


def some_page(request):
    return HttpResponse("Welcome to some page!")


urlpatterns = [
    path("", include("django.contrib.auth.urls")),
    path("admin/", admin.site.urls),
    path("password_rotate/", include("password_rotate.urls")),
    path("some_page/", some_page),
]
