from django.contrib import admin
from password_rotate.models import PasswordChange, PasswordHistory


@admin.register(PasswordChange)
class PasswordChangeAdmin(admin.ModelAdmin):
    model = PasswordChange
    list_display = ("user", "last_changed")


@admin.register(PasswordHistory)
class PasswordHistory(admin.ModelAdmin):
    model = PasswordHistory
    list_display = ("user", "created")
