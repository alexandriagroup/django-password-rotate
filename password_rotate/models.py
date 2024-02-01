from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _
from password_rotate.managers import PasswordHistoryManager


class PasswordChange(models.Model):
    """
    Records when users change a password to support an expiration policy
    """
    last_changed = models.DateTimeField(db_index=True, auto_now_add=True)
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.user.username}"


class PasswordHistory(models.Model):
    """
    Stores a single password history entry, related to :model:`auth.User`.
    """
    created = models.DateTimeField(
        auto_now_add=True, verbose_name=_("created"), db_index=True, help_text=_("The date the entry was created.")
    )
    password = models.CharField(
        max_length=128, verbose_name=_("password"), help_text=_("The encrypted password.")
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name=_("user"),
        help_text=_("The user this password history entry belongs to."),
        related_name="password_history_entries",
        on_delete=models.CASCADE,
    )

    objects = PasswordHistoryManager()

    def __str__(self):
        return f"{self.user.username} - {self.created}"

    class Meta:
        get_latest_by = "created"
        ordering = ["-created"]
        verbose_name = _("password history entry")
        verbose_name_plural = _("password history entries")
