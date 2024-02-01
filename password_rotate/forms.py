from django.contrib.auth.forms import PasswordChangeForm
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

from rapidfuzz import fuzz
from django.conf import settings


class ForcePasswordChangeForm(PasswordChangeForm):
    """
    This form ensures the new password is not too similar to the old password.
    """
    def clean(self):
        cleaned_data = super().clean()

        if cleaned_data.get("old_password") and cleaned_data.get("new_password1"):
            ratio = fuzz.ratio(
                cleaned_data["old_password"],
                cleaned_data["new_password1"]
            )
            if ratio >= settings.PASSWORD_ROTATE_MAX_SIMILARITY_RATIO:
                raise ValidationError(
                    {"new_password1": _("The new password is too similar to the old one.")},
                    code="password_similar"
                )
        return cleaned_data
