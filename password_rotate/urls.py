from django.urls import path

from .views import ForcePasswordChangeView


urlpatterns = [
    path("", ForcePasswordChangeView.as_view(), name="force_password_change")
]
