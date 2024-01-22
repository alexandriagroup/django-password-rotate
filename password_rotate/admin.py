from django.contrib import admin
from password_rotate.models import PasswordChange


@admin.register(PasswordChange)
class PasswordChangeAdmin(admin.ModelAdmin):
    model = PasswordChange
    list_display = ("user", "last_changed")
